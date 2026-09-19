import pytest

@pytest.mark.parametrize("method, url", [
    ("get", "/api/admin/users"),
    ("post", "/api/admin/products"),
    ("post", "/api/admin/categories"),
])
def test_user_forbidden_on_admin_routes(client,auth,method,url):
    res = getattr(client, method)(url, headers=auth["headers"])
    assert res.status_code==403

def test_get_all_users(client,admin_auth,auth):
    res=client.get(
        '/api/admin/users',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]==admin_auth['json']
    assert res.json()[1]==auth['json']


def test_change_role_ok(client,admin_auth,auth):
    res=client.patch(
        f'/api/admin/users/{auth["json"]["id"]}/role',
        headers=admin_auth['headers'],
        params={'new_role':'manager'}
    )
    assert res.status_code==200
    assert res.json()['msg']=='Ok'


def test_change_role_self_bad(client,admin_auth):
    res=client.patch(
        f'/api/admin/users/{admin_auth["json"]["id"]}/role',
        headers=admin_auth['headers'],
        params={'new_role':'manager'}
    )
    assert res.status_code==403
    assert res.json()['detail']=="Admin can't change self role"


def test_change_role_user_not_found(client,admin_auth):
    res=client.patch(
        f'/api/admin/users/{9999}/role',
        headers=admin_auth['headers'],
        params={'new_role':'manager'}
    )
    assert res.status_code==404
    assert res.json()['detail']=='User not found'


def test_change_role_invalid_role(client,admin_auth,auth):
    res=client.patch(
        f'/api/admin/users/{auth["json"]["id"]}/role',
        headers=admin_auth['headers'],
        params={'new_role':'Incorrect'}
    )
    assert res.status_code==400
    assert res.json()['detail']=='Invalid role'


def test_is_active_user_ok(client,admin_auth,auth):
    res=client.patch(
        f'/api/admin/users/{auth["json"]["id"]}/is_active',
        headers=admin_auth['headers'],
        params={'is_active':False}
    )
    assert res.status_code==200
    assert res.json()['msg']=='Ok'


def test_is_active_user_self_bad(client,admin_auth):
    res=client.patch(
        f'/api/admin/users/{admin_auth["json"]["id"]}/is_active',
        headers=admin_auth['headers'],
        params={'is_active':False}
    )
    assert res.status_code==403
    assert res.json()['detail']=="Admin can't change self is_active"


def test_is_active_user_not_found_bad(client,admin_auth):
    res=client.patch(
        f'/api/admin/users/{9999}/is_active',
        headers=admin_auth['headers'],
        params={'is_active':False}
    )
    assert res.status_code==404
    assert res.json()['detail']=='User not found'


def test_get_all_products_ok(client,admin_auth,category,product):
    pr=client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json={
            'name':'Milk',
            'price':100,
            'stock':10,
            'category_id':category['id'],
            'is_active':False
        }
    )
    res=client.get(
        '/api/admin/products',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]['is_active']==product['is_active']
    assert res.json()[1]['is_active']==pr.json()['is_active']

def test_get_all_products_bad(client,admin_auth):
    res=client.get(
        '/api/admin/products',
        headers=admin_auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Products not found'


def test_add_product_ok(client,admin_auth,category):
    data={
        'name':'Something',
        'description':'Some text',
        'price':1000,
        'stock':100,
        'category_id':category['id'],
        'is_active':True
    }
    res=client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==200
    assert res.json()['name']==data['name']
    assert int(res.json()['price'][:4])==data['price']
    assert res.json()["category_id"]==category["id"]


def test_add_product_service_bad(client,admin_auth):
    data={
        'name':'Something',
        'description':'Some text',
        'price':1000,
        'stock':100,
        'category_id':999,
        'is_active':True
    }
    res=client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==404
    assert res.json()['detail']=='Category not found'


def test_update_product_ok(client,admin_auth,product):
    data={
        'name':'Something',
        'price':1000,
        'stock':10
    }
    res=client.patch(
        f'/api/admin/products/{product["id"]}',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==200
    assert res.json()['name']==data['name']
    assert int(res.json()['price'])==data['price']


def test_update_product_not_found(client,admin_auth):
    data={
        'name':'Something',
        'price':1000,
        'stock':10
    }
    res=client.patch(
        f'/api/admin/products/{999}',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==404
    assert res.json()['detail']=='Product not found'


def test_update_product_no_fields(client,admin_auth,product):
    res=client.patch(
        f'/api/admin/products/{product["id"]}',
        headers=admin_auth['headers'],
        json={}
    )
    assert res.status_code==400
    assert res.json()['detail']=='No fields to update'


def test_delete_product_ok(client,admin_auth,product):
    res=client.delete(
        f'/api/admin/products/{product["id"]}',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()['msg']=='Ok'


def test_delete_product_bad(client,admin_auth):
    res=client.delete(
        f'/api/admin/products/{999}',
        headers=admin_auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Product not found'


def test_get_all_categories(client,admin_auth,category):
    data={
        'name':'iPhone',
        'slug':'Phones',
        'is_active':False
    }

    client.post(
        '/api/admin/categories',
        headers=admin_auth['headers'],
        json=data
    )
    res=client.get(
        '/api/admin/categories',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]['name']==category['name']
    assert res.json()[1]['name']==data['name']


def test_get_all_categories_bad(client,admin_auth):
    res=client.get(
        '/api/admin/categories',
        headers=admin_auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Categories not found'


def test_add_category_ok(client,admin_auth):
    data={
        'name':'Some',
        'slug':'Some',
        'is_active':True
    }
    res=client.post(
        '/api/admin/categories',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==200
    assert res.json()['name']==data['name']
    assert res.json()['slug']==data['slug']
    assert res.json()['is_active']==data['is_active']


def test_add_category_bad(client,admin_auth,category):
    #Категория та же,что и в фикстуре
    data={
        'name':'Smth',
        'slug':'smth',
        'is_active':True
    }
    res=client.post(
        '/api/admin/categories',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==409
    assert res.json()['detail']=='Category name or slug has already used'    


def test_update_category_ok(client,admin_auth,category):
    data={
        'name':'Smth',
        'slug':'smth',
        'is_active':True
    }
    res=client.patch(
        f'/api/admin/categories/{category["id"]}',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==200
    assert res.json()['name']==data['name']
    assert res.json()['slug']==data['slug']
    assert res.json()['is_active']==data['is_active']


def test_update_category_no_fields(client,admin_auth,category):
    res=client.patch(
        f'/api/admin/categories/{category["id"]}',
        headers=admin_auth['headers'],
        json={}
    )
    assert res.status_code==400
    assert res.json()['detail']=='No fields to update'


def test_update_category_not_found_category(client,admin_auth):
    data={
        'name':'Smth',
        'slug':'smth',
        'is_active':True
    }
    res=client.patch(
        f'/api/admin/categories/{99999}',
        headers=admin_auth['headers'],
        json=data
    )
    assert res.status_code==404
    assert res.json()['detail']=='Category not found'


def test_delete_category_ok(client,admin_auth,category):
    res=client.delete(
        f'/api/admin/categories/{category["id"]}',
        headers=admin_auth['headers']
    )
    assert res.status_code==200
    assert res.json()['msg']=='Ok'


def test_delete_category_has_products(client,admin_auth,category,product):
    res=client.delete(
        f'/api/admin/categories/{category["id"]}',
        headers=admin_auth['headers']
    )
    assert res.status_code==400
    assert res.json()['detail']=='Category has products'


def test_delete_category_not_found(client,admin_auth):
    res=client.delete(
        f'/api/admin/categories/{9999}',
        headers=admin_auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Category not found'


