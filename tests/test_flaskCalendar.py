import os
import tempfile

import pytest

from flask_calendar import app
from flask_calendar.db import init_db

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({'TESTING': True, 'DATABASE': db_path})
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
        
    os.close(db_fd)
    os.unlink(db_path)
