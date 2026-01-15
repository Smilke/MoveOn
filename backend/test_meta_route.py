from app.main import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

data = {
    "patient_id": "12345678901",
    "physiotherapist_id": 1,
    "description": "Teste Final",
    "success_criteria": "Criterio",
    "start_date": "2026-01-15",
    "end_date": "2026-02-15"
}

try:
    response = client.post("/api/metas", json=data)
    print("Status:", response.status_code)
    print("Body:", response.json())
except Exception as e:
    print("Exception:", e)
    import traceback
    traceback.print_exc()
