import os
import tempfile
import pytest

from pathlib import Path

from organization import create_app, db
from organization.models import Employee, ContactAddress, City


test_folder_location = Path(__file__).parent
test_db_location = Path(test_folder_location,"test_employee_data.sqlite")


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/account/login',
            data=dict(username=username, password=password)
        )

    def logout(self):
        return self._client.get('/account/logout')


@pytest.fixture
def app():
    # db_fd, db_path = tempfile.mkstemp()
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///temp_test.db',
        'SECRET_KEY': '3c1f2177abdd1702bcd57cd26db3fb48891bdfc9',
    }
    app = create_app(test_config)
    with app.app_context():
        db.create_all()
        yield app

    base_dir = Path(__file__).parent.parent
    test_db_path = Path(base_dir, 'organization/temp_test.db')
    os.remove(test_db_path)


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

