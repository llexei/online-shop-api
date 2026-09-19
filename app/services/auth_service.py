from fastapi import HTTPException,status
from sqlalchemy import select
from jose import jwt,JWTError
import time
import logging
from app.core.config import settings
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token,revoke_token,is_revoked
from app.models.user import UserOrm
from app.schemas.auth import RefreshInSchema

logger = logging.getLogger(__name__)

def register_service(user_in, db):
    ex_user=select(UserOrm).where(
        (UserOrm.username==user_in.username) | (UserOrm.email==user_in.email)
        )
    if db.scalars(ex_user).one_or_none():
        logger.warning('username or email already registered')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='username or email has already registered'
        )
    
    user=UserOrm(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    logger.info('new user created id=%s username=%s', user.id,user.username)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_service(credentials,db):
    ex_user=db.scalar(select(UserOrm).where(UserOrm.username==credentials.username))
    if not ex_user or not verify_password(credentials.password, ex_user.hashed_password):
        logger.warning('incorrect username or password')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate':'Bearer'}
        )
    
    access_token=create_access_token(data={'sub':str(ex_user.id),'usename':ex_user.username})
    refresh_token=create_refresh_token(data={'sub':str(ex_user.id),'username':ex_user.username})
    logger.info('success login user_id=%s',ex_user.id)
    return{
        'access_token':access_token,
        'refresh_token':refresh_token,
        'token_type':'Bearer'
    }


def read_me_service(current_user):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return current_user


def logout_service(redis,access_token,refresh_token):
    credental_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate token',
                headers={'WWW-Authenticate':'Bearer'}
            )
    
    try:
        payload_access=jwt.decode(access_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        access_jti=payload_access.get('jti')
        access_exp=payload_access.get('exp')

        if access_jti and access_exp:
            revoke_token(redis=redis,token_type='access',jti=access_jti,ttl=max(access_exp-int(time.time()),0))

    except JWTError:
        raise credental_exception

    try:
        payload_refresh=jwt.decode(refresh_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        refresh_jti=payload_refresh.get('jti')
        refresh_exp=payload_refresh.get('exp')

        if refresh_jti and refresh_exp:
            revoke_token(redis=redis,token_type='refresh',jti=refresh_jti,ttl=max(refresh_exp-int(time.time()),0))
        
    except JWTError:
        raise credental_exception
    
    logger.info('tokens have been revoked')
    return{
        'msg':'Successfully logged out'
    }


def refresh_service(redis,request,db,access_token):
    credential_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate refresh token',
        headers={'WWW-Authenticate':'Bearer'}
    )

    try:
        refresh_payload=jwt.decode(request.refresh_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        username=refresh_payload.get('username')

        if username is None:
            raise credential_exception
        
        user=db.scalar(select(UserOrm).where(UserOrm.username==username))

        refresh_jti=refresh_payload.get('jti')

        if is_revoked(redis=redis, token_type='refresh', jti=refresh_jti) or refresh_jti is None:
            logger.warning('refresh token revoked user_id=%s', user.id)
            raise credential_exception
        
    except JWTError:
        logger.warning('refresh expired user_id=%s', user.id)
        raise credential_exception
    


    if user is None:
        raise credential_exception
    
    try:
        access_payload=jwt.decode(access_token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        access_jti=access_payload.get('jti')
        access_exp=access_payload.get('exp')
        
        if not is_revoked(redis=redis,token_type='access',jti=access_jti):
            revoke_token(redis=redis,token_type='access',jti=access_jti,ttl=max(access_exp-int(time.time()),0))

    except JWTError:
        pass

    new_access_token=create_access_token(data={'sub':str(user.id),'username':user.username})
    logger.info('new access user_id=%s',user.id)
    return{'access_token':new_access_token}
