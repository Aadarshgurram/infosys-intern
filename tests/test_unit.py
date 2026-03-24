from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["message"] == "Server Running"
    
def test_voice():
    res = client.post("/voice")
    assert res.status_code == 200
    assert "<Say>" in res.text
    
def test_language_selection():
    res = client.post("/language", data={"Digits": "1"})
    assert res.status_code == 200
    assert "<Gather" in res.text