from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_call_flow():
    # Step 1: Start call
    res = client.post("/voice")
    assert res.status_code == 200

    # Step 2: Select English
    res = client.post("/language", data={"Digits": "1"})
    assert res.status_code == 200

    # Step 3: Ask for PNR
    res = client.post("/process-intent", data={"SpeechResult": "pnr"})
    assert res.status_code == 200
    
def test_booking_flow():
    res = client.post("/process-intent", data={"SpeechResult": "book ticket"})
    assert res.status_code == 200
    assert "/ask-origin" in res.text