def test_get_active_categories_ok(client,auth,category):
    res=client.get(
        '/api/categories/',
        headers=auth['headers']
    )
    assert res.status_code==200
    assert res.json()[0]==category


def test_get_active_categories_bad(client,auth):
    res=client.get(
        '/api/categories/',
        headers=auth['headers']
    )
    assert res.status_code==404
    assert res.json()['detail']=='Categories not found'