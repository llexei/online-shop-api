def test_create_order_ok(client,auth,item,product):
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


def test_create_order_empty_cart(client,auth):
    res=client.post(
        '/api/orders/',
        headers=auth['headers']
    )
    assert res.status_code==400
    assert res.json()['detail']=='Cart is empty'

def test_get_orders_ok(client,auth,order):
    res=client.get(
        '/api/orders/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]==order


def test_get_orders_empty(client,auth):
    res=client.get(
        '/api/orders/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()==[]


def test_get_order_id_ok(client,auth,order):
    res=client.get(
        f'/api/orders/{order["id"]}',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()==order


def test_get_order_id_bad(client,auth):
    res=client.get(
        f'/api/orders/{7}',
        headers=auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Order not found'

def test_update_status_bad_status(client,admin_auth,order_admin):
    res=client.patch(
        f'/api/orders/{order_admin["id"]}/status',
        headers=admin_auth['headers'],
        json={'status':'Smth'}
    )
    print(res.status_code,res.json())
    assert res.status_code==400
    assert res.json()['detail']=='Invalid status transition'


def test_update_status_ok(client,admin_auth,order_admin):
    res=client.patch(
        f'/api/orders/{order_admin["id"]}/status',
        headers=admin_auth['headers'],
        json={'status':'assembled'}
    )
    assert res.status_code==200
    assert res.json()['msg']=='Ok'


def test_update_status_not_permission(client,auth,order):
    res=client.patch(
        f'/api/orders/{order["id"]}/status',
        headers=auth['headers'],
        json={'status':'assembled'}
    )
    assert res.status_code==403
    assert res.json()['detail']=='Not enough permissions'


def test_cancel_order_ok(client,auth,order):
    cancel=client.post(
        f'/api/orders/{order["id"]}/cancelled',
        headers=auth['headers']
    )
    assert cancel.status_code==200
    res=client.get(
        f"/api/orders/{order['id']}", 
        headers=auth["headers"]
    )
    assert res.json()['status']=='cancelled'
    assert cancel.json()['msg']=='Ok'

