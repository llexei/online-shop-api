from pydantic import BaseModel,EmailStr,Field,ConfigDict
from datetime import datetime


class UserOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username:str
    id:int
    email:EmailStr
    role:str
    is_active:bool
    created_at:datetime|None=None

