def test_get_active_products_service_ok(client,admin_auth,category,product):
    client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json={
            'name':'Cheese',
            'price':1000,
            'stock':10,
            'category_id':category['id'],
            'is_active':False
        }
    )
    res=client.get('/api/products/')

    assert res.status_code==200
    names=[p['name'] for p in res.json()]
    assert product['name'] in names
    assert 'Cheese' not in names


def test_get_active_products_service_bad(client,admin_auth,category):
    res=client.get('/api/products/')
    assert res.status_code==200
    assert res.json() ==[]


def test_get_product_for_id_ok(client,auth,category,product):
    res=client.get(f'/api/products/{product["id"]}')
    assert res.status_code==200


def test_get_product_for_id_bad(client,admin_auth,category):
    client.post(
        '/api/admin/products',
        headers=admin_auth['headers'],
        json={
            'name':'Cheese',
            'price':1000,
            'stock':10,
            'category_id':category['id'],
            'is_active':False
        }
    )
    hidden=client.get('/api/products/1')
    assert hidden.status_code==404