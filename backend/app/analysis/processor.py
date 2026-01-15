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
        Usa Ultralytics YOLO para extrair keypoints e calcular o ângulo do joelho ao longo do vídeo.
        """
        if self._model is None:
            raise NotImplementedError("Ultralytics YOLO model not available in this environment")

        import cv2
        import numpy as np
        from app.analysis.rules import compute_angle

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        results = []
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # YOLO inference
            yolo_results = self._model(frame)
            keypoints = None
            if hasattr(yolo_results, 'keypoints') and yolo_results.keypoints is not None:
                # Ultralytics >=8.0.0
                keypoints = yolo_results.keypoints.xy.cpu().numpy() if hasattr(yolo_results.keypoints, 'xy') else None
            elif hasattr(yolo_results[0], 'keypoints') and yolo_results[0].keypoints is not None:
                # Ultralytics <8.0.0
                keypoints = yolo_results[0].keypoints.xy.cpu().numpy() if hasattr(yolo_results[0].keypoints, 'xy') else None
            if keypoints is not None and len(keypoints) > 0:
                # Assume first person
                kp = keypoints[0]
                # COCO: 11=left_hip, 13=left_knee, 15=left_ankle
                #        12=right_hip, 14=right_knee, 16=right_ankle
                if joint == "knee":
                    # Média dos dois joelhos
                    angles = []
                    # Left
                    if kp.shape[0] >= 17:
                        a = tuple(kp[11])  # left_hip
                        b = tuple(kp[13])  # left_knee
                        c = tuple(kp[15])  # left_ankle
                        angle_left = compute_angle(a, b, c)
                        angles.append(angle_left)
                        a = tuple(kp[12])  # right_hip
                        b = tuple(kp[14])  # right_knee
                        c = tuple(kp[16])  # right_ankle
                        angle_right = compute_angle(a, b, c)
                        angles.append(angle_right)
                    if angles:
                        angle = float(np.mean(angles))
                        timestamp = frame_idx / fps
                        results.append((timestamp, angle))
            frame_idx += 1
        cap.release()
        return results
