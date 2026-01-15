"""Orchestrator: uses processor + rules to analyze a submitted video and produce feedback logs."""
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime
from .processor import YOLOPoseWrapper
from .rules import count_reps, segment_reps


def analyze_video(
    patient_id: str,
    exercise_id: str,
    video_path: str,
    processor: YOLOPoseWrapper = None,
    min_reps: int = 2,
    progress_cb: Optional[Callable[[int, int, int], None]] = None,
) -> Dict[str, Any]:
    """Analyze video and return structured feedback.

    - processor.detect_joint_angles should return list of (timestamp, angle)
    - rules.count_reps will count repetitions
    """
    if processor is None:
        processor = YOLOPoseWrapper()

    # attempt to get angle sequence (timestamp, angle_degrees)
    seq: List[Tuple[float, float]] = processor.detect_joint_angles(video_path, joint="knee", progress_cb=progress_cb)

    rep_segments = segment_reps(seq, down_threshold=90.0, up_threshold=160.0)
    reps = len(rep_segments)

    status = "Sucesso" if reps >= min_reps else "Falha"
    observations: List[str] = []

    # per-repetition details and observations
    rep_details: List[Dict[str, Any]] = []
    for idx, seg in enumerate(rep_segments, start=1):
        min_a = seg.get("min_angle")
        max_a = seg.get("max_angle")
        start = seg.get("start")
        bottom = seg.get("bottom")
        end = seg.get("end")

        ok_amplitude = (min_a is not None and max_a is not None and min_a <= 90.0 and max_a >= 160.0)
        note = "Amplitude adequada" if ok_amplitude else f"Amplitude reduzida (min={min_a}, max={max_a})"

        rep_details.append({
            "rep_index": idx,
            "start_time": start,
            "bottom_time": bottom,
            "end_time": end,
            "min_angle": min_a,
            "max_angle": max_a,
            "note": note,
        })

        observations.append(f"Rep {idx}: {note}")

    if reps < min_reps:
        observations.insert(0, f"Repetições insuficientes: {reps} (<{min_reps})")
    else:
        observations.insert(0, f"Repetições detectadas: {reps}")

    feedback = {
        "ID_Paciente": patient_id,
        "ID_Exercicio": exercise_id,
        "Timestamp": datetime.utcnow().isoformat() + "Z",
        "Status_Execucao": status,
        "Observacoes_Tecnicas": observations,
        "Repetitions": reps,
        "Rep_Details": rep_details,
    }
    return feedback
