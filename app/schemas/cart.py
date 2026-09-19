from pydantic import BaseModel, ConfigDict,Field


class CartItemOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    product_id:int
    quantity:int

class CartItemInSchema(BaseModel):
    product_id:int
    quantity:int=Field(gt=0, default=1)

class CartItemUpdateSchema(BaseModel):
    quantity: int = Field(gt=0)