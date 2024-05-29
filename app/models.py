
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
    characters_id = Column(Integer, ForeignKey('characters.id'))
    status = Column(JSON)
    
    

class Equipments(Base):
    __tablename__ = 'equipments'

    id = Column(Integer, primary_key=True, index=True)
    characters_id = Column(Integer, ForeignKey('characters.id'))
    weapon_id = Column(Integer, ForeignKey('weapons.id'))
    title_id = Column(Integer)
    jacket_id = Column(Integer)
    shoulder_id = Column(Integer)
    pants_id = Column(Integer)
    belt_id = Column(Integer)
    shoes_id = Column(Integer)
    neck_id = Column(Integer)
    bracelet_id = Column(Integer)
    ring_id = Column(Integer)
    sub_weapon_id = Column(Integer)
    earing_id = Column(Integer)
    magic_stone_id = Column(Integer)

    

class Weapons(Base):
    __tablename__ = 'weapons'

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(50))
    enchant = Column(Integer, ForeignKey('enchantments.id'))


class Enchantments(Base):
    __tablename__ = 'enchantments'

    id = Column(Integer, primary_key=True, index=True)
    enchant_name = Column(String(50))
    enchant_value = Column(Integer)
    reinforce_skill = Column(String(50))
    reinforce_value = Column(Integer)
    # card_name = Column(String(50))
    # card_upgrade = Column(Integer)
    # card_id = Column(Integer, Foreign_key='cards.id')

class Avatars(Base):
    __tablename__ = 'avatars'

    id = Column(Integer, primary_key=True, index=True)
    characters_id = Column(Integer, ForeignKey('characters.id'))

    avatar_JSON = Column(JSON)
    
    # head_id = Column(Integer)
    # hear_id = Column(Integer)
    # face_id = Column(Integer)
    # chest_id = Column(Integer)
    # top_id = Column(Integer)
    # bottom_id = Column(Integer)
    # waist_id = Column(Integer)
    # boots_id = Column(Integer)
    # skin_id = Column(Integer)
    # aura_id = Column(Integer)
    # weapon_skin_id = Column(Integer)

class Traits(Base):

    __tablename__ = 'traits'

    id = Column(Integer, primary_key=True, index=True)
    characters_id = Column(Integer, ForeignKey('characters.id'))

    trait_JSON = Column(JSON)

class Skills(Base):
    
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, index=True)
    characters_id = Column(Integer, ForeignKey('characters.id'))

    skill_JSON = Column(JSON)

# class Cards(Base):
#     __tablename__ = 'cards'

#     id = Column(Integer, primary_key=True, index=True)
#     card_name = Column(String(50))
#     card_value = Column(Integer)
#     card_upgrade = Column(Integer)
#     card_id = Column(Integer, ForeignKey='cards.id')


# class Stats(Base):
#     __tablename__ = 'stats'

#     id = Column(Integer, primary_key=True, index=True)
#     strangth = Column(Integer)
#     intelligence = Column(Integer)
#     vitality = Column(Integer)
#     mentalitiy = Column(Integer)





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

