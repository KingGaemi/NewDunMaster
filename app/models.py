from pydantic import BaseModel, Field
from pydantic.networks import HttpUrl

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from app.database import Base



class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), unique=True)
    body = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    age = Column(Integer)
    email = Column(String(50), unique=True)
    password = Column(String(50))
    is_active = Column(Boolean, default=True)


class Image(BaseModel):
    url: HttpUrl    
    name: str

class UserBase(BaseModel):
    id: int
    name: str
    age: int
    email: str
    password: str


class Item(BaseModel):
    name: str = Field(...)
    description: str | None = Field(
        None, title="The description of the item", example="A very nice Item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero", example=1.67)  
    tax: float | None = None
    tags: list[str] = []
    image: Image | None = None
  

