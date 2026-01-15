from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_test():
    resp = client.post("/api/login", json={"email": "paciente@moveon.com", "senha": "Senha124"})
    print("status_code:", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)

if __name__ == '__main__':
    run_test()
