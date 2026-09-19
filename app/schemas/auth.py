from pydantic import BaseModel,ConfigDict,Field,EmailStr


class RegisterInSchema(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6)

class TokenOutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshInSchema(BaseModel):
    refresh_token: str