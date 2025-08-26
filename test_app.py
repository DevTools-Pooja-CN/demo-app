import pytest
from app.main import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to DevTools" in response.data or b"Hello DevOps Enthusiast" in response.data
    assert b"DevTools is a leading consulting" in response.data
    assert b"DevSecOps" in response.data
    assert b"Automation" in response.data
