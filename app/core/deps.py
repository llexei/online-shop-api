from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.config import settings
from app.core.database import get_db
from app.core.security import is_revoked
from app.core.database import DbSession
from app.core.redis import RedisClient
from app.models.user import UserOrm


oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/api/auth/login')

def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:DbSession,redis:RedisClient):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not valide credentials',
        headers={'WWW-Authenticate':'Bearer'}
    )

    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        sub=payload.get('sub')
        if sub is None:
            raise credentials_exception    
        user_id=int(sub)

    except (JWTError,ValueError):
        raise credentials_exception
    
    jti=payload.get('jti')
    if jti is not None and is_revoked(redis=redis,token_type='access',jti=jti):
        raise credentials_exception
    
    user=db.get(UserOrm,user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User is banned'
        )
    
    return user


CurrentUser=Annotated[UserOrm,Depends(get_current_user)]


def check_role(*roles):
    def checker(user:CurrentUser):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not enough permissions'
            )
        return user
    return checker


CheckStaff=Annotated[UserOrm,Depends(check_role('admin','manager'))]


def check_admin(user:CurrentUser):
    if user.role!='admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions'
        )
    return user

