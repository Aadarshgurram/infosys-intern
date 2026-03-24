from fastapi.testclient import TestClient
from main import app
import requests

client = TestClient(app)

def test_pnr_intent():
    res = client.post("/process-intent", data={"SpeechResult": "check pnr"})
    assert res.status_code == 200
    assert "/ask-pnr" in res.text
    
def test_train_intent():
    res = client.post("/process-intent", data={"SpeechResult": "train status"})
    assert res.status_code == 200
    assert "/ask-train" in res.text
    
def test_load_voice():
    for _ in range(5):
        res = requests.post("http://127.0.0.1:8000/voice")
        assert res.status_code == 200
        
def test_empty_input():
    res = client.post("/process-intent", data={})
    assert res.status_code == 200