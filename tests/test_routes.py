def test_landing_page(client):
    """
    Asserts root landing page yields 200 and loads standard text headings.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"BloodBank" in response.data

def test_login_page(client):
    """
    Asserts login form renders successfully.
    """
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Email Address" in response.data

def test_register_page(client):
    """
    Asserts register form renders successfully.
    """
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b"Create Account" in response.data

def test_admin_dashboard_redirects_unauthenticated(client):
    """
    Asserts unauthenticated access redirects.
    """
    response = client.get('/admin/dashboard')
    assert response.status_code == 302
    assert 'auth/login' in response.headers['Location']
