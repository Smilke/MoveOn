import pytest
from app.analysis import rules, engine


class FakeProcessor:
    def __init__(self, seq):
        # seq: list of (timestamp, angle)
        self._seq = seq

    def detect_joint_angles(self, video_path: str, joint: str = "knee"):
        return self._seq


def test_compute_angle_simple_right_triangle():
    a = (1.0, 0.0)
    b = (0.0, 0.0)
    c = (0.0, 1.0)
    angle = rules.compute_angle(a, b, c)
    # angle at origin
    assert pytest.approx(angle, rel=1e-2) == 90.0


def test_count_reps_detects_two_reps():
    # Build a synthetic angle sequence that goes: high->low->high->low->high
    seq = [
        (0.0, 170.0),
        (0.2, 140.0),
        (0.4, 80.0),  # down
        (0.6, 170.0),  # up -> rep1
        (0.8, 100.0),
        (1.0, 70.0),  # down
        (1.2, 165.0),  # up -> rep2
    ]
    reps = rules.count_reps(seq, down_threshold=90.0, up_threshold=160.0)
    assert reps == 2


def test_analyze_video_integration_success_and_failure():
    seq_success = [
        (0.0, 170.0),
        (0.5, 80.0),
        (1.0, 170.0),
        (1.5, 75.0),
        (2.0, 170.0),
    ]
    proc = FakeProcessor(seq_success)
    feedback = engine.analyze_video("p1", "ex1", "fake.mp4", processor=proc, min_reps=2)
    assert feedback["ID_Paciente"] == "p1"
    assert feedback["ID_Exercicio"] == "ex1"
    assert feedback["Status_Execucao"] == "Sucesso"
    assert feedback["Repetitions"] >= 2
    # Repetition details
    assert "Rep_Details" in feedback
    assert len(feedback["Rep_Details"]) >= 2
    for rep in feedback["Rep_Details"]:
        assert "min_angle" in rep and "max_angle" in rep and "note" in rep

    seq_fail = [
        (0.0, 170.0),
        (0.5, 100.0),
        (1.0, 170.0),
    ]
    proc2 = FakeProcessor(seq_fail)
    feedback2 = engine.analyze_video("p2", "ex2", "fake2.mp4", processor=proc2, min_reps=2)
    assert feedback2["Status_Execucao"] == "Falha"
    assert "Repetições insuficientes" in feedback2["Observacoes_Tecnicas"][0]
    # rep details may be empty or small
    assert "Rep_Details" in feedback2
