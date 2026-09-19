from fastapi import Body, Depends, HTTPException,status, APIRouter,dependencies
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from jose import JWTError,jwt
import time
from app.core.deps import DbSession, CurrentUser,oauth2_scheme
from app.core.redis import RedisClient
from app.core.limiting import rate_limit
from app.services.auth_service import register_service,login_service,read_me_service,logout_service,refresh_service
from app.models.user import UserOrm
from app.schemas.user import UserOutSchema
from app.schemas.auth import TokenOutSchema,RefreshInSchema,RegisterInSchema


router=APIRouter()


@router.post('/register',response_model=UserOutSchema,dependencies=[Depends(rate_limit(10,60))])
def register(user_in:RegisterInSchema,db:DbSession,):
    return register_service(user_in, db)

@router.post('/login',response_model=TokenOutSchema)
def login(credentials:Annotated[OAuth2PasswordRequestForm,Depends()],db:DbSession):
    return login_service(credentials,db)

@router.get('/me',response_model=UserOutSchema)
def read_me(current_user:CurrentUser):
    return read_me_service(current_user)

@router.post('/logout')
def logout(redis:RedisClient,access_token:Annotated[str,Depends(oauth2_scheme)],refresh_token:str=Body(...,embed=True)):
    return logout_service(redis,access_token,refresh_token)

@router.post('/refresh',dependencies=[Depends(rate_limit(10,60))])
def refresh(redis:RedisClient,request:RefreshInSchema,db:DbSession,access_token:Annotated[str,Depends(oauth2_scheme)]):
    return refresh_service(redis,request,db,access_token)