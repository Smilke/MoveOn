from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_upload_video():
    file_content = b"fake video content"
    files = {"file": ("test.mp4", file_content, "video/mp4")}

    data = {"patient_id": "test_p", "exercise_id": "test_ex"}
    resp = client.post("/api/upload/video", files=files, data=data)
    assert resp.status_code == 201
    data = resp.json()
    assert "filename" in data
    assert data["filename"].endswith(".mp4") or data["filename"] != ""
