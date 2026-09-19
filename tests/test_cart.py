def test_get_cart_ok(client,auth,product,item):
    res=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]['quantity']==2
    assert res.json()[0]['product_id']==product['id']


def test_get_cart_bad(client,auth):
    res=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()==[]


def test_add_item_to_cart_ok(client,auth,product,item):
    res=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]['quantity']==2
    assert res.json()[0]['product_id']==product['id']


def test_update_item_ok(client,auth,product,item):
    update=client.patch(
        f'/api/cart/items/{item["id"]}',
        headers=auth['headers'],
        json={'item_id':item['id'],'quantity':10}
    )
    assert update.status_code==200

    res=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]['quantity']==10
    assert res.json()[0]['product_id']==product['id']


def test_update_item_too_quantity(client,auth,item):
    res=client.patch(
        f'/api/cart/items/{item["id"]}',
        headers=auth['headers'],
        json={'item_id':item['id'],'quantity':11}
    )
    assert res.status_code==400
    assert res.json()['detail']=='Not enough stock'


def test_delete_item_ok(client,auth,item):
    res=client.delete(
        f'/api/cart/items/{item["id"]}',
        headers=auth['headers'],
    )
    assert res.status_code==200
    assert res.json()['msg']=='The product has been deleted'
    cart=client.get(
        '/api/cart/',
        headers=auth['headers']
    )
    assert cart.json()==[]


def test_delete_item_bad(client,auth):
    res=client.delete(
        f'/api/cart/items/{7}',
        headers=auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Cart item not found'


def test_clear_cart_ok(client,auth,item):
    res=client.delete(
        '/api/cart/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()['msg']=='The cart has been cleared'