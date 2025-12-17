"""
Module xu ly logic canh bao va toi uu FPS
Nguoi phu trach: Ban 2
"""

import time
import threading
import os

# Khoi tao pygame cho am thanh
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False
    print("Warning: pygame khong kha dung, se su dung beep thay the")


class AlertSystem:
    def __init__(self):
        # Nguong canh bao
        self.EAR_THRESHOLD = 0.21  # Nguong mat nham
        self.MAR_THRESHOLD = 0.6   # Nguong ngap (mieng mo rong)
        self.HEAD_PITCH_THRESHOLD = 15  # Nguong guc dau (do)
        self.DROWSY_TIME_THRESHOLD = 2.0  # Thoi gian (giay) truoc khi canh bao
        
        # Trang thai
        self.drowsy_start_time = None
        self.is_alerting = False
        self.alert_thread = None
        self.stop_alert = False
        
        # Thong ke
        self.drowsy_count = 0
        self.yawn_count = 0
        self.last_fps = 0
        self.frame_times = []
        
        # Phat hien ngap
        self.yawn_start_time = None
        self.is_yawning = False
        
        # Load am thanh canh bao
        self.alert_sound = None
        if PYGAME_AVAILABLE:
            sound_path = os.path.join(os.path.dirname(__file__), "assets", "alert.wav")
            if os.path.exists(sound_path):
                self.alert_sound = pygame.mixer.Sound(sound_path)
    
    def check_yawn(self, mar):
        """
        Kiem tra ngap
        Returns: (is_yawning, yawn_triggered)
        """
        yawn_triggered = False
        
        if mar > self.MAR_THRESHOLD:
            if not self.is_yawning:
                self.is_yawning = True
                self.yawn_start_time = time.time()
        else:
            if self.is_yawning:
                # Ket thuc ngap - dem 1 lan
                yawn_duration = time.time() - self.yawn_start_time
                if yawn_duration > 0.5:  # Ngap it nhat 0.5 giay
                    self.yawn_count += 1
                    yawn_triggered = True
                self.is_yawning = False
        
        return self.is_yawning, yawn_triggered
    
    def check_drowsiness(self, ear, head_pitch, mar=0):
        """
        Kiem tra trang thai buon ngu
        Returns: (is_drowsy, drowsy_duration, alert_triggered)
        """
        is_drowsy = ear < self.EAR_THRESHOLD or head_pitch > self.HEAD_PITCH_THRESHOLD
        drowsy_duration = 0
        alert_triggered = False
        
        if is_drowsy:
            if self.drowsy_start_time is None:
                self.drowsy_start_time = time.time()
            
            drowsy_duration = time.time() - self.drowsy_start_time
            
            if drowsy_duration >= self.DROWSY_TIME_THRESHOLD:
                if not self.is_alerting:
                    self.trigger_alert()
                    self.drowsy_count += 1
                    alert_triggered = True
        else:
            self.drowsy_start_time = None
            self.stop_alerting()
        
        return is_drowsy, drowsy_duration, alert_triggered
    
    def trigger_alert(self):
        """Kich hoat canh bao"""
        self.is_alerting = True
        self.stop_alert = False
        
        def play_alert():
            while not self.stop_alert:
                if self.alert_sound and PYGAME_AVAILABLE:
                    self.alert_sound.play()
                    time.sleep(0.5)
                else:
                    # Beep manh - tan so cao, ngan, lap lai nhanh
                    try:
                        import winsound
                        winsound.Beep(2500, 150)
                        winsound.Beep(3000, 150)
                        winsound.Beep(2500, 150)
                    except:
                        print("\a")
                time.sleep(0.3)
        
        self.alert_thread = threading.Thread(target=play_alert, daemon=True)
        self.alert_thread.start()
    
    def stop_alerting(self):
        """Dung canh bao"""
        self.stop_alert = True
        self.is_alerting = False
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()
    
    def update_fps(self):
        """Cap nhat FPS"""
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Giu lai 30 frame gan nhat de tinh FPS
        self.frame_times = [t for t in self.frame_times if current_time - t < 1.0]
        
        self.last_fps = len(self.frame_times)
        return self.last_fps
    
    def get_status(self, ear, head_pitch, face_detected, mar=0):
        """Tra ve trang thai dang text"""
        if not face_detected:
            return "Khong phat hien khuon mat", (128, 128, 128)
        
        # Kiem tra ngap
        is_yawning, _ = self.check_yawn(mar)
        
        is_drowsy, duration, _ = self.check_drowsiness(ear, head_pitch, mar)
        
        if self.is_alerting:
            return "CANH BAO: BUON NGU!", (0, 0, 255)
        elif is_yawning:
            return "Dang ngap...", (0, 165, 255)
        elif is_drowsy:
            return f"Dang buon ngu... ({duration:.1f}s)", (0, 165, 255)
        else:
            return "Tinh tao", (0, 255, 0)
    
    def set_thresholds(self, ear_thresh=None, head_thresh=None, time_thresh=None, mar_thresh=None):
        """Cap nhat nguong canh bao"""
        if ear_thresh is not None:
            self.EAR_THRESHOLD = ear_thresh
        if head_thresh is not None:
            self.HEAD_PITCH_THRESHOLD = head_thresh
        if time_thresh is not None:
            self.DROWSY_TIME_THRESHOLD = time_thresh
        if mar_thresh is not None:
            self.MAR_THRESHOLD = mar_thresh
    
    def reset_stats(self):
        """Reset thong ke"""
        self.drowsy_count = 0
        self.yawn_count = 0
        self.drowsy_start_time = None
        self.is_yawning = False
        self.stop_alerting()
    
    def cleanup(self):
        """Don dep tai nguyen"""
        self.stop_alerting()
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()
