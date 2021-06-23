import os
import tempfile

import pytest

from flask_calendar import app as application
from flask_calendar.db import init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = application.create_app({'TESTING': True, 'DATABASE': db_path})
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
        
    os.close(db_fd)
    os.unlink(db_path)
    
def test_index(client):
    '''
        start with a blank database
    '''
    rv = client.get('/')
    assert b'Redirecting' in rv.data

def login(client, username, password):
    '''
        TODO: change user logic from json file to db
        so it'll throw error since users.json cannot be accessed from here
    '''
    return client.post('/do_login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_login(client):
    '''
        Make sure login works
    '''
    
    username = os.getenv("LTS_USERNAME")
    password = os.getenv("LTS_PASSWORD")
    rv = login(client, username, password)
    breakpoint()
    assert b'sample' in rv.data
    
    rv = login(client, username, password)
    assert rv.status_code == 200
    
    rv = login(client, f'{username}x', password)
    assert b'Login' in rv.data
    
    rv = login(client, username, f'{password}x')
    assert b'Login' in rv.data
