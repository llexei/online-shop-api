from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OrderOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    user_id:int
    status:str
    total_price:int
    created_at:datetime

class UpdateStatusSchema(BaseModel):
    status:str