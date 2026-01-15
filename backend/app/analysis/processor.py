"""Wrapper around Ultralytics YOLO pose estimation.

In production this would run inference on the video and return joint keypoints over time.
For testing we will mock `YOLOPoseWrapper.detect_joint_angles` to return synthetic sequences.
"""
from typing import List, Tuple, Optional
import datetime

try:
    from ultralytics import YOLO  # type: ignore
except Exception:
    YOLO = None  # tests can mock this


class YOLOPoseWrapper:
    def __init__(self, model: Optional[str] = None):
        self.model_name = model or "yolov8n-pose"
        self._model = None
        if YOLO is not None:
            try:
                self._model = YOLO(self.model_name)
            except Exception:
                self._model = None

    def detect_joint_angles(self, video_path: str, joint: str = "knee") -> List[Tuple[float, float]]:
        """Detect joint angle sequence for `joint` from a video.

        Returns list of (timestamp_seconds, angle_degrees).
        In production this reads frames and extracts pose keypoints using YOLO pose model.
        Here we raise NotImplementedError if model not available so tests must mock this method.
        """
        if self._model is None:
            raise NotImplementedError("Ultralytics YOLO model not available in this environment")

        # Pseudocode placeholder: real implementation would iterate frames and compute angles
        raise NotImplementedError("Real video processing not implemented in this environment")
