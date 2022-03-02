from flask import session


def test_login(client, auth):
    assert client.get('/account/login').status_code == 200
    response = auth.login()

    # assert response.status_code == 302

    # with client:
    #     assert client.get('/employee/master').status_code == 200
    #     assert session['e_id'] == 1
    #     assert g.user['username'] == 'test'


def test_master_page(client):
    """Test without login can not access master page"""
    assert client.get('/employee/master').status_code == 302

