from pydantic import BaseModel, Field, create_model
from pydantic.networks import HttpUrl

from sqlalchemy import JSON, Column, Integer, String, Float, ForeignKey, Boolean, BigInteger
from app.database import Base


# def create_pydantic_model_from_json(data: dict, model_name: str = "DynamicModel") -> BaseModel:
#     """JSON 데이터를 기반으로 Pydantic 모델을 동적으로 생성하는 함수"""
#     fields = {
#         field_name: (type(field_value), ...)  # 타입 추론 및 기본값 설정
#         for field_name, field_value in data.items()
#     }
#     return create_model(model_name, **fields)


# def create_dynamic(json_data: dict):
#     DynamicModel = create_pydantic_model_from_json(json_data)

#     UserStatus = DynamicModel(**json_data)
#     print(UserStatus)


class Characters(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    character_id = Column(String(50))
    character_name = Column(String(30))
    level = Column(Integer)
    job_id = Column(String(50))
    job_grow_id = Column(String(50))
    job_name = Column(String(30))
    job_grow_name = Column(String(30))
    fame = Column(Integer)
    adventure_id = Column(Integer, ForeignKey('adventures.id'))
    guild_id = Column(Integer, ForeignKey('guilds.id'))
    deal = Column(BigInteger)
    buff = Column(Integer)

class Adventures(Base):
    __tablename__ = 'adventures'
    id = Column(Integer, primary_key=True, index=True)
    adventure_name = Column(String(30))

class Guilds(Base):
    __tablename__ = 'guilds'
    id = Column(Integer, primary_key=True, index=True)
    guild_name = Column(String(30))


class Servers(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String(10))
    server_name = Column(String(10))


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(JSON)
    characters_id = Column(Integer, ForeignKey('characters.id'))
    

    




class CharactersBase(BaseModel):
    server_id: str
    character_id: str
    character_name: str
    level: int
    job_id: str
    job_grow_id: str
    job_name: str
    job_grow_name: str
    fame: int
    adventure_name: str
    guild_name: str
    deal: int
    buff: int

class StatusBase(BaseModel):
    status: dict

class AdventureBase(BaseModel):
    adventure_id: int
    adventure_name: str

class GuildBase(BaseModel):
    guild_id: int
    guild_name: str

class ServerBase(BaseModel):
    server_id: str
    server_name: str

