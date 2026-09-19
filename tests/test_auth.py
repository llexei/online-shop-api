from sqlalchemy import select
from app.models.cart import CartItemOrm
from app.models.order import OrderOrm
from app.models.user import UserOrm
from app.schemas.product import ProductInSchema
from main import app

def test_register_ok(client):
    res=client.post(
        '/api/auth/register',
        json={'username':'user','email':'user@mail.com','password':'secret_123'}
    )
    data=res.json()
    assert res.status_code==200
    assert data['username'] =='user'
    assert 'password' not in data
    assert 'hashed_password' not in data
    assert 'email' in data


def test_register_identical_username(client):
    user1=client.post(
        '/api/auth/register',
        json={'username':'user','email':'user1@mail.com','password':'secret_123'}
    )
    user2=client.post(
        '/api/auth/register',
        json={'username':'user','email':'user2@mail.com','password':'secret_123'}
    )
    assert user1.status_code==200
    assert user2.status_code==400


def test_register_identical_email(client):
    user1=client.post(
        '/api/auth/register',
        json={'username':'user','email':'user@mail.com','password':'secret_123'}
    )
    user2=client.post(
        '/api/auth/register',
        json={'username':'user1','email':'user@mail.com','password':'secret_123'}
    )
    assert user1.status_code==200
    assert user2.status_code==400


def test_login_ok(client):
    client.post(
        '/api/auth/register',
        json={'username':'user','email':'user@mail.com','password':'secret_123'}
    )
    res=client.post(
        '/api/auth/login',
        data={'username':'user','password':'secret_123'}
    )
    data=res.json()
    assert res.status_code==200
    assert all(x in data for x in ('access_token','refresh_token','token_type'))


def test_login_bad_password(client):
    client.post(
        '/api/auth/register',
        json={'username':'user','email':'user@mail.com','password':'secret_123'}
    )
    res=client.post(
        '/api/auth/login',
        data={'username':'user','password':'incorrect_password'}
    )
    assert res.status_code==401
    assert res.json()['detail']=='Incorrect username or password'

def test_read_me_ok(client,auth):
    res=client.get(
        '/api/auth/me',
       headers=auth["headers"]
    )
    data = res.json()
    assert res.status_code==200
    assert data["username"] == "user"
    assert "password" not in data
    assert "hashed_password" not in data


def test_read_me_bad(client):
    res=client.get('/api/auth/me')
    assert res.status_code==401
    assert res.json()['detail']=='Not authenticated'


def test_read_me_broken_token(client,auth):
    broken=auth["access_token"] + "x"
    res=client.get(
        "/api/auth/me",
        headers={"Authorization":f"Bearer {broken}"},
    )
    assert res.status_code==401


def test_user_banned(client,db,auth):
    user=db.scalar(select(UserOrm).where(UserOrm.username == "user"))
    user.is_active=False
    db.commit()

    res=client.get(
        '/api/auth/me',
        headers=auth["headers"]
    )
    assert res.status_code==403
    assert res.json()['detail']=='User is banned'


def test_refresh_ok(client,auth):
    res=client.post(
        '/api/auth/refresh',
        json={'refresh_token':auth['refresh_token']},
        headers=auth['headers']
    )
    data=res.json()
    assert res.status_code==200
    assert 'access_token' in data
    assert data['access_token'] != auth['access_token']


def test_old_access(client,auth):
    logout=client.post(
        '/api/auth/logout',
        headers=auth['headers'],
        json={
            'refresh_token':auth['refresh_token']
        }
    )
    res=client.get("/api/auth/me", headers=auth["headers"])
    assert logout.status_code==200
    assert res.status_code==401


def test_logout(client,auth):
    res=client.post(
        '/api/auth/logout',
        headers=auth['headers'],
        json={
            'refresh_token':auth['refresh_token']
        }
    )
    assert res.status_code==200
    assert res.json()['msg']=='Successfully logged out'