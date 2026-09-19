from pydantic import BaseModel,ConfigDict,Field
from decimal import Decimal
from datetime import datetime


class ProductOutSchema(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    name:str
    description:str|None = None
    price:Decimal
    stock:int = 0
    category_id:int
    is_active:bool = False
    created_at:datetime

class ProductInSchema(BaseModel):
    name:str
    description:str|None=None
    price:Decimal = Field(gt=0)
    stock:int = Field(ge=0)
    category_id:int
    is_active:bool = False

class ProductUpdateSchema(BaseModel):
    name:str|None=None
    description:str|None=None
    price:Decimal|None=Field(gt=0,default=None)
    stock:int|None=Field(ge=0,default=None)
    is_active:bool|None=False