from pydantic import BaseModel, Field
from pydantic.networks import HttpUrl

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, BigInteger
from app.database import Base



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    charId = Column(String(50));
    serverId = Column(String(50));
    adventureName = Column(String(50));
    guildName = Column(String(50));
    jobName: str = Column(String(50));
    jobGrowName = Column(String(50));
    fame = Column(Integer);
    deal = Column(BigInteger);
    buff = Column(Integer)




class Image(BaseModel):
    url: HttpUrl    
    name: str

class UserBase(BaseModel):
    name: str
    charId: str
    serverId: str
    adventureName: str
    guildName: str
    jobName: str
    jobGrowName: str
    fame: int
    deal: int
    buff: int

    


class Item(BaseModel):
    name: str = Field(...)
    description: str | None = Field(
        None, title="The description of the item", example="A very nice Item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero", example=1.67)  
    tax: float | None = None
    tags: list[str] = []
    image: Image | None = None
  

