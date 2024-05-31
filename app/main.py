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



@app.get("/search", response_class=HTMLResponse)
def search_character(request: Request, characterName: str = Query(None), serverId: str = Query("all"), adventureName: str = Query(None), db = db_dependency) :
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters?characterName={characterName}&apikey={API_KEY}"
    response = requests.get(url)
    
    
    # If adventureName is given, search characters in the adventure
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
            return templates.TemplateResponse("search.html", {"request": request, "servers": data.servers , "characterList": {}})
            
    # If characterName is given, search characters with the name
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

    # Get status from database
    db = SessionLocal()
    db_character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id
    db_status = db.query(models.Status).filter(models.Status.characters_id == db_character_id).first()

    
    if db_status:
        status = db_status.status
    else:
        status = {}

    if response.status_code == 200:
        return templates.TemplateResponse(
            "info.html", 
            {   
                "request": request,
                "equipmentsJSON": equipJSON,
                "servers": data.servers,
                "serverId": serverId,
                "serverName": data.servers[serverId],
                "fame" : fame,
                "adventureName" : equipJSON['adventureName'],
                "status": status
            }
            )
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    



@app.get("/getEquipments/{serverId}/{characterId}")
async def get_equipments_json(serverId: str, characterId: str):
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment?apikey={API_KEY}"
    response = requests.get(url)
    equipJSON = response.json()


    if response.status_code == 200:
        return JSONResponse(content=equipJSON)  # JSONResponse 사용
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    

# getAvater From DB
@app.get("/getAvatar/{serverId}/{characterId}")
async def get_avatar_json(serverId: str, characterId: str):
    db = SessionLocal()
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id
    db_avatar = db.query(models.Avatars).filter(models.Avatars.characters_id == character_id).first()
    if db_avatar:
        return JSONResponse(content=db_avatar.avatar_JSON)
    else:
        raise HTTPException(status_code=404, detail="No character data found")

    

@app.post("/saveCharacter", status_code=status.HTTP_201_CREATED)
async def save_character(characters: models.CharactersBase, db : db_dependency):

    db = SessionLocal()
   
    db_first = db.query(models.Characters).first() 

    # Check if character already exists
    if db_first:
        db_existing_character = db.query(models.Characters).filter(models.Characters.character_id == characters.character_id).first() # 중복 체크
        if db_existing_character:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Character with this name already exists"
            )
        

    # Check if adventure already exists
    db_adventure = db.query(models.Adventures).filter(models.Adventures.adventure_name == characters.adventure_name).first()
    if not db_adventure:
        db_adventure = models.Adventures(adventure_name=characters.adventure_name)
        db.add(db_adventure)
        db.commit()



    # Check if guild already exists
    # (Some characters don't have guild)
    if characters.guild_name:
        db_guild = db.query(models.Guilds).filter(models.Guilds.guild_name == characters.guild_name).first()
        if not db_guild:
            db_guild = models.Guilds(guild_name=characters.guild_name)
            db.add(db_guild)
            db.commit()



    # refine characters data to temp_characters
    temp_characters = characters.dict()
    temp_characters.pop("adventure_name")
    temp_characters.pop("guild_name")
    temp_characters["adventure_id"] = db_adventure.id
    temp_characters["guild_id"] = db_guild.id
    temp_characters["server_id"] = db.query(models.Servers).filter(models.Servers.server_id == characters.server_id).first().id
    

    
    db_character = models.Characters(**temp_characters)
    db.add(db_character)
    db.commit()
    db.refresh(db_character)



@app.get("/saveStatus/{serverId}/{characterId}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def save_status(serverId: str, characterId: str):

    
    # Get character status
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/status?apikey={API_KEY}"
    response = requests.get(url)
    statusJSON = response.json()



    # refine status data
    result = {}
    for item in statusJSON["status"]:
        name = item.get("name")
        value = item.get("value")
        if name:
            result[name] = value
    ## result = {"HP": value, "MP": value, ...}

    
    db = SessionLocal()

    # Get Character id (1, 2, 3, ...)
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id
    

    # Check if status already exists
    db_status = db.query(models.Status).filter(models.Status.characters_id == character_id).first()

    if db_status:
        # Update existing status
        db_status.status = result
    else:
        # Create new status
        db_status = models.Status(status = result, characters_id = character_id)
        db.add(db_status)

    db.commit()
    db.refresh(db_status)
    
    
    if response.status_code == 200:
        return JSONResponse(content=result)
    else:
        raise HTTPException(status_code=404, detail="No character data found")


# saveAvatar
@app.get("/saveAvatar/{serverId}/{characterId}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def save_avatar(serverId: str, characterId: str):
        
    # Get character avatar
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/avatar?apikey={API_KEY}"
    response = requests.get(url)
    avatarJSON = response.json()

    db = SessionLocal()

    # refine avatar data
    result = avatarJSON["avatar"]
    ## result = {"모자 아바타": "레어 모자 클론 아바타", ...}

    # Get Character id (1, 2, 3, ...)
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id

    # Check if avatar already exists
    db_avatar = db.query(models.Avatars).filter(models.Avatars.characters_id == character_id).first()

    if db_avatar:
        # Update existing avatar
        db_avatar.avatar = result
    else:
        # Create new avatar
        db_avatar = models.Avatars(avatar_JSON = result, characters_id = character_id)
        db.add(db_avatar)



    db.commit()
    db.refresh(db_avatar)

    if response.status_code == 200:
        return JSONResponse(content=avatarJSON)
    else:
        raise HTTPException(status_code=404, detail="No character data found")   
        

# saveTrait
@app.get("/saveTrait/{serverId}/{characterId}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def save_trait(serverId: str, characterId: str):
            
    # Get character trait
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/equip/equipment-trait?apikey={API_KEY}"
    response = requests.get(url)
    traitJSON = response.json()

    db = SessionLocal()

    # Get Character id (1, 2, 3, ...)
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id

    # Check if trait already exists
    db_trait = db.query(models.Traits).filter(models.Traits.characters_id == character_id).first()

    if db_trait:
        # Update existing trait
        db_trait.trait = traitJSON
    else:
        # Create new trait
        db_trait = models.Traits(trait_JSON = traitJSON, characters_id = character_id)
        db.add(db_trait)

    db.commit()
    db.refresh(db_trait)

    if response.status_code == 200:
        return JSONResponse(content=traitJSON)
    else:
        raise HTTPException(status_code=404, detail="No character data found")
    

# saveSkill
@app.get("/saveSkill/{serverId}/{characterId}", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def save_skill(serverId: str, characterId: str):

    # Get character skill
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters/{characterId}/skill/style?apikey={API_KEY}"
    response = requests.get(url)
    skillJSON = response.json()



    db = SessionLocal()

    # Get Character id (1, 2, 3, ...)
    character_id = db.query(models.Characters).filter(models.Characters.character_id == characterId).first().id

    # Check if skill already exists
    db_skill = db.query(models.Skills).filter(models.Skills.characters_id == character_id).first()

    if db_skill:
        # Update existing skill
        db_skill.skill = skillJSON
    else:
        # Create new skill
        db_skill = models.Skills(skill_JSON = skillJSON, characters_id = character_id)
        db.add(db_skill)

    db.commit()
    db.refresh(db_skill)

    if response.status_code == 200:
        return JSONResponse(content=skillJSON)
    else:
        raise HTTPException(status_code=404, detail="No character data found")








