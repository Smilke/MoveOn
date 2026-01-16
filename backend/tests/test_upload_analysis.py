import io
from fastapi.testclient import TestClient
from unittest import mock

from app.main import app


client = TestClient(app)


def fake_detect(self, video_path: str, joint: str = "knee"):
    # synthetic sequence that yields 2 reps
    return [
        (0.0, 170.0),
        (0.4, 80.0),
        (0.8, 170.0),
        (1.2, 75.0),
        (1.6, 165.0),
    ]


def test_upload_and_analysis_endpoint(monkeypatch):
    monkeypatch.setattr("app.analysis.processor.YOLOPoseWrapper.detect_joint_angles", fake_detect, raising=True)

    file_bytes = io.BytesIO(b"fake video content")
    files = {"file": ("test.mp4", file_bytes, "video/mp4")}
    data = {"patient_id": "test_patient", "exercise_id": "squat"}

    resp = client.post("/api/upload/video", files=files, data=data)
    assert resp.status_code == 201
    body = resp.json()
    assert "analysis" in body
    analysis = body["analysis"]
    assert analysis["ID_Paciente"] == "test_patient"
    assert analysis["ID_Exercicio"] == "squat"
    assert analysis["Status_Execucao"] in ("Sucesso", "Falha", "Pendente", "Erro")
    # since our fake returns 2 reps, we expect Sucesso
    assert analysis["Repetitions"] >= 2
