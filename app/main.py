from fastapi import FastAPI, HTTPException, status, Body, Depends , Query
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Annotated

from websockets import serve
from app import models, data
from pydantic import BaseModel
from app.database import SessionLocal, engine

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session , column_property, sessionmaker

from starlette.requests import Request
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")
models.Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")  # static 디렉토리 마운트

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


API_KEY = "PZ2F29nXBUBg0LlJPTtRnw76C4r43x82" # Need to hide this key


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request ,"servers": data.servers})



@app.get("/searchCharacter", response_class=HTMLResponse)
def search_character(request: Request, characterName: str = Query(None), serverId: str = Query("all"), adventureName: str = Query(None), db = db_dependency) :
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters?characterName={characterName}&apikey={API_KEY}"
    response = requests.get(url)
    
    print("searchCharacter")
    if adventureName:
        db = SessionLocal()
        adventure = db.query(models.Adventures).filter(models.Adventures.adventure_name == adventureName).first()
        if adventure:
            adventureId = adventure.id
            characters = db.query(models.Characters).filter(models.Characters.adventure_id == adventureId).all()
            if characters:
                
                serverId = db.query(models.Servers).filter(models.Servers.id == characters[0].server_id).first().server_id

                characterList = {"rows": []}

                for character in characters:
                    characterList["rows"].append({"serverId": serverId,
                                                "characterId": character.character_id,
                                                "characterName": character.character_name,
                                                "level": character.level,
                                                "jobId": character.job_id,
                                                "jobGrowId": character.job_grow_id,
                                                "jobName": character.job_name,
                                                "jobGrowName": character.job_grow_name,
                                                "fame": character.fame})
                    
                    
                return templates.TemplateResponse("search.html", {"request": request, "characterList": characterList, "servers": data.servers})
        else:
            raise HTTPException(status_code=404, detail="Adventure not found")
            
        
        
    elif characterName and serverId:
        if response.status_code == 200:
            characterList = response.json()
            return templates.TemplateResponse("search.html", {"request": request, "characterList": characterList, "servers": data.servers})
        else:
            raise HTTPException(status_code=404, detail="Character not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid search parameters")



    


@app.get("/info" ,  response_class=HTMLResponse)
async def info(request: Request, characterId: str = Query(...), serverId: str = Query(...)):
    equipmentUrl = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment?apikey={API_KEY}"
    response = requests.get(equipmentUrl)
    equipJSON = response.json()

    # Get character fame
    characterName = equipJSON["characterName"]
    characterUrl = f"https://api.neople.co.kr/df/servers/{serverId}/characters?characterName={characterName}&apikey={API_KEY}"
    response2 = requests.get(characterUrl) 
    charJSON = response2.json()
    fame = charJSON['rows'][0]['fame']

    
    if response.status_code == 200:
        return templates.TemplateResponse("info.html", {"request": request, "equipmentsJSON": equipJSON, "servers": data.servers, "serverId": serverId, "fame" : fame})
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    



@app.get("/info/{characterId}/{serverId}")
async def get_equipments_json(characterId: str, serverId: str):
    equipmentUrl = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment?apikey={API_KEY}"
    response = requests.get(equipmentUrl)
    equipJSON = response.json()
    if response.status_code == 200:
        return JSONResponse(content=equipJSON)  # JSONResponse 사용
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    


@app.post("/character/create", status_code=status.HTTP_201_CREATED)
async def create_character(characters: models.CharactersBase, db : db_dependency):

    db = SessionLocal()
   
    print("db_first")
    db_first = db.query(models.Characters).first() 

    if db_first:
        existing_character = db.query(models.Characters).filter(models.Characters.character_id == characters.character_id).first() # 중복 체크
        if existing_character:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Character with this name already exists"
            )
        

    print("adventure:", characters.adventure_name)
    db_adventure = db.query(models.Adventures).filter(models.Adventures.adventure_name == characters.adventure_name).first()
    if not db_adventure:
        db_adventure = models.Adventures(adventure_name=characters.adventure_name)
        db.add(db_adventure)
        db.commit()

    
    print("guild")
    if characters.guild_name:
        db_guild = db.query(models.Guilds).filter(models.Guilds.guild_name == characters.guild_name).first()
        if not db_guild:
            db_guild = models.Guilds(guild_name=characters.guild_name)
            db.add(db_guild)
            db.commit()


    temp_characters = characters.dict()

    temp_characters.pop("adventure_name")
    temp_characters.pop("guild_name")
    
    temp_characters["adventure_id"] = db_adventure.id
    temp_characters["guild_id"] = db_guild.id
    temp_characters["server_id"] = db.query(models.Servers).filter(models.Servers.server_id == characters.server_id).first().id
    print("temp_characters:", temp_characters)


    
    db_character = models.Characters(**temp_characters)


    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    # return db_user



@app.get("/getStatus/{serverId}/{characterId}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def get_status(serverId: str, characterId: str):

    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/status?apikey={API_KEY}"
    response = requests.get(url)
    statusJSON = response.json()

    result = {}
    for item in statusJSON["status"]:
        name = item.get("name")
        value = item.get("value")
        if name:
            result[name] = value


    
    db = SessionLocal()
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id
    db_status = models.Status(status = result, characters_id = character_id)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    


    if response.status_code == 200:
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    