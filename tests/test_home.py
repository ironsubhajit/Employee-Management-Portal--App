from organization import create_app


def test_config():
    """test config var 'TESTING: True' """
    assert create_app({'TESTING': True}).testing


