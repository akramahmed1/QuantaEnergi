import pytest
from my_app import create_app, db
from my_app.models import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    testing_client = app.test_client()

    # Establish an application context
    with app.app_context():
        # Create all tables
        db.create_all()
        yield testing_client  # This is where the testing happens

    with app.app_context():
        # Drop all tables
        db.drop_all()

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', email='testuser@example.com')
    # Setting up user credentials
    user.set_password('password')
    return user

def test_register_and_login(test_client, new_user):
    # Register a new user
    response = test_client.post('/register', data={'username': new_user.username, 'email': new_user.email, 'password': 'password'})
    assert response.status_code == 200
    assert b'User registered successfully' in response.data

    # Login with the new user
    response = test_client.post('/login', data={'username': new_user.username, 'password': 'password'})
    assert response.status_code == 200
    assert b'Welcome' in response.data
