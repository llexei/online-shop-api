from pydantic import BaseModel,ConfigDict,Field
from typing import Union


class CategoryOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    name:str
    slug:str
    is_active:bool

class CategoryInSchema(BaseModel):
    name:str
    slug:str
    is_active:bool = False

class CategoryUpdateSchema(BaseModel):
    name:str|None=None
    slug:str|None=None
    is_active:bool|None=False