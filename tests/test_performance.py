import requests

def test_load_root():
    for _ in range(10):
        res = requests.get("http://127.0.0.1:8000/")
        assert res.status_code == 200
        
def test_load_voice():
    for _ in range(5):
        res = requests.post("http://127.0.0.1:8000/voice")
        assert res.status_code == 200