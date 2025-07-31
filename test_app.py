import pytest
from app.main import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome!" in response.data
    assert b"Jenkins Python App" in response.data
    assert b"Powered by Flask & Jenkins" in response.data
