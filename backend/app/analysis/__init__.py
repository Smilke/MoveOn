"""Video analysis package: processor (YOLO wrapper), rules (angle/reps), engine (orchestrator).

This package is designed to be testable: processor can be mocked by tests to return
precomputed angle sequences.
"""

from .engine import analyze_video
from .rules import compute_angle, count_reps
from .processor import YOLOPoseWrapper

__all__ = ["analyze_video", "compute_angle", "count_reps", "YOLOPoseWrapper"]
