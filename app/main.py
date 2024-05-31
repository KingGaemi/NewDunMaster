from fastapi import FastAPI, HTTPException, status, Body, Depends , Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Annotated
from app import models, data
from pydantic import BaseModel
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session
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
def search_character(request: Request, characterName: str = Query(...), serverId: str = Query("all") ) :
    url = f"https://api.neople.co.kr/df/servers/{serverId}/characters?characterName={characterName}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        characterList = response.json()
        return templates.TemplateResponse("search.html", {"request": request, "characterList": characterList, "servers": data.servers})
    else:
        raise HTTPException(status_code=404, detail="Character not found")



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
    


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: models.UserBase, db : db_dependency):
    existing_user = db.query(models.User).filter(models.User.charId == user.charId).first()  # 중복 체크
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this name already exists"
        )

    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # return db_user
