import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models.user import UserOrm
from app.core.deps import get_db
from app.core.config import settings
from main import app
from app.core.redis import get_redis
import sqlite3
from decimal import Decimal

sqlite3.register_adapter(Decimal, lambda d: str(d))
sqlite3.register_converter("NUMERIC", lambda b: Decimal(b.decode()))
engine=create_engine(
    'sqlite://',
    connect_args={'check_same_thread':False},
    poolclass=StaticPool
)
TestingSessionLocal=sessionmaker(bind=engine)


class FakeRedis:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value, ex=None):
        self._data[key] = value
        return True

    def exists(self, key):
        return 1 if key in self._data else 0

    def delete(self, *keys):
        for key in keys:
            self._data.pop(key, None)
        return True

    def close(self):
        pass


@pytest.fixture
def fake_redis():
    return FakeRedis()

@pytest.fixture
def db():
    Base.metadata.create_all(engine)
    db=TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def client(db,fake_redis):
    settings.testing = True


    def override_get_db():
        try:
            yield db
        finally:
            pass
    def override_get_redis():
        yield fake_redis

    app.dependency_overrides[get_redis]=override_get_redis
    app.dependency_overrides[get_db]=override_get_db
    
    with TestClient(app) as c:
        yield c 

    app.dependency_overrides.clear()
    settings.testing = False


@pytest.fixture
def auth(client):
    reg=client.post(
        '/api/auth/register',
        json={'username':'user','email':'user@mail.com','password':'secret_123'}
    )
    login=client.post(
        '/api/auth/login',
        data={'username':'user','password':'secret_123'}
    )
    tokens = login.json()
    return{ 
        'headers':{'Authorization': f'Bearer {tokens["access_token"]}'},
        'access_token':tokens['access_token'],
        'refresh_token':tokens['refresh_token'],
        'json':reg.json()
    }

@pytest.fixture
def admin_auth(client,db):
    client.post(
        '/api/auth/register',
        json={'username':'admin','email':'admin@mail.com','password':'secret_123'}
    )
    user=db.scalar(select(UserOrm).where(UserOrm.username=='admin'))
    user.role='admin'
    db.commit()
    login=client.post(
        '/api/auth/login',
        data={'username':'admin','password':'secret_123'}
    )
    tokens = login.json()
    res=client.get(
        '/api/auth/me',
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    return{ 
        'headers':{'Authorization': f'Bearer {tokens["access_token"]}'},
        'access_token':tokens['access_token'],
        'refresh_token':tokens['refresh_token'],
        'json':res.json()
    }


@pytest.fixture
def category(client,db,admin_auth):
    res=client.post(
        '/api/admin/categories',
        headers=admin_auth['headers'],
        json={
            'name':'Smth',
            'slug':'smth',
            'is_active':True
        }
    )
    return res.json()

@pytest.fixture
def product(client,db,admin_auth,category):
    res=client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json={
            'name':'Milk',
            'price':100,
            'stock':10,
            'category_id':category['id'],
            'is_active':True
        }
    )
    return res.json()


@pytest.fixture
def item(client,auth,product):
        res=client.post(
        '/api/cart/items',
        headers=auth['headers'],
        json={'product_id':product['id'],'quantity':2}
    )
        assert res.status_code==200
        return res.json()

@pytest.fixture
def item_admin(client,admin_auth,product):
        res=client.post(
        '/api/cart/items',
        headers=admin_auth['headers'],
        json={'product_id':product['id'],'quantity':2}
    )
        assert res.status_code==200
        return res.json()


@pytest.fixture
def order(client,auth,item,product):
    res=client.post(
        '/api/orders/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()['status']=='pending'
    assert res.json()['total_price']==item['quantity']*int(product['price'][:3])
    cart=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert cart.status_code==200
    assert cart.json()==[]
    return res.json()


@pytest.fixture
def order_admin(client,admin_auth,item_admin,product):
    res=client.post(
        '/api/orders/',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()['status']=='pending'
    assert res.json()['total_price']==item_admin['quantity']*int(product['price'][:3])
    cart=client.get(
        '/api/cart/',
        headers=admin_auth['headers']
    )
    assert cart.status_code==200
    assert cart.json()==[]
    return res.json()