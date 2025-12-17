"""
Module nhan dien khuon mat va tinh toan EAR (Eye Aspect Ratio)
Su dung Dlib
"""

import cv2
import numpy as np
import dlib
from scipy.spatial import distance as dist
import os


class FaceDetector:
    def __init__(self):
        # Dlib face detector va predictor
        self.detector = dlib.get_frontal_face_detector()
        
        model_path = os.path.join(os.path.dirname(__file__), "assets", "shape_predictor_68_face_landmarks.dat")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.predictor = dlib.shape_predictor(model_path)
        
        # Landmark indices cho mat (dlib 68 points)
        self.LEFT_EYE = list(range(42, 48))
        self.RIGHT_EYE = list(range(36, 42))
        
        # Landmark indices cho mieng (de phat hien ngap)
        self.MOUTH_OUTER = list(range(48, 60))
        self.MOUTH_INNER = list(range(60, 68))
        
    def calculate_ear(self, eye):
        """Tinh Eye Aspect Ratio (EAR)"""
        # Khoang cach doc
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        # Khoang cach ngang
        C = dist.euclidean(eye[0], eye[3])
        
        if C == 0:
            return 0.3
        
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_mar(self, mouth):
        """Tinh Mouth Aspect Ratio (MAR) - phat hien ngap"""
        # Khoang cach doc (3 diem)
        A = dist.euclidean(mouth[2], mouth[10])  # 50 - 58
        B = dist.euclidean(mouth[4], mouth[8])   # 52 - 56
        # Khoang cach ngang
        C = dist.euclidean(mouth[0], mouth[6])   # 48 - 54
        
        if C == 0:
            return 0
        
        mar = (A + B) / (2.0 * C)
        return mar
    
    def calculate_head_pose(self, shape):
        """Tinh goc nghieng dau don gian"""
        nose = shape[30]  # Mui
        chin = shape[8]   # Cam
        
        dy = chin[1] - nose[1]
        if dy == 0:
            return 0
        
        # Uoc tinh goc nghieng
        dx = chin[0] - nose[0]
        pitch = abs(dx) / dy * 20  # Don gian hoa
        
        return pitch
    
    def detect(self, frame):
        """
        Phat hien khuon mat va tra ve thong tin
        Returns: (ear, mar, head_pitch, face_detected, annotated_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        ear = 0.3
        mar = 0.0
        head_pitch = 0
        face_detected = False
        
        faces = self.detector(gray, 0)
        
        if len(faces) > 0:
            face_detected = True
            face = faces[0]
            
            shape = self.predictor(gray, face)
            shape = np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)])
            
            # Lay toa do mat
            left_eye = shape[self.LEFT_EYE]
            right_eye = shape[self.RIGHT_EYE]
            
            # Lay toa do mieng
            mouth = shape[self.MOUTH_OUTER]
            
            # Tinh EAR
            left_ear = self.calculate_ear(left_eye)
            right_ear = self.calculate_ear(right_eye)
            ear = (left_ear + right_ear) / 2.0
            
            # Tinh MAR (Mouth Aspect Ratio)
            mar = self.calculate_mar(mouth)
            
            # Tinh goc dau
            head_pitch = self.calculate_head_pose(shape)
            
            # Ve mat (xanh la)
            for point in left_eye:
                cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
            for point in right_eye:
                cv2.circle(frame, tuple(point), 2, (0, 255, 0), -1)
            
            # Ve mieng (xanh duong)
            for point in mouth:
                cv2.circle(frame, tuple(point), 2, (255, 0, 0), -1)
            
            # Ve khung mat
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
        return ear, mar, head_pitch, face_detected, frame
    
    def release(self):
        """Giai phong tai nguyen"""
        pass
