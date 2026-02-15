import cv2
import numpy as np
import os
from typing import Generator, Tuple

class VideoReader:
    def __init__(self, video_path: str):
        self.video_path = video_path
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
    def get_info(self) -> dict:
        return {
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "total_frames": self.total_frames
        }

    def __iter__(self) -> Generator[np.ndarray, None, None]:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame
            
    def close(self):
        self.cap.release()

class VideoWriter:
    def __init__(self, output_path: str, fps: float, width: int, height: int):
        self.output_path = output_path
        self.fps = fps
        self.width = width
        self.height = height
        # Use mp4v codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
    def write_frame(self, frame: np.ndarray):
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))
        self.writer.write(frame)
        
    def close(self):
        self.writer.release()
