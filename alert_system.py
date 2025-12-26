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
    def __init__(self, mode="student"):
        # =========================
        # CHE DO SU DUNG
        # =========================
        # mode: "student" | "driver"
        self.mode = mode

        # =========================
        # NGUONG CANH BAO (GIU NGUYEN)
        # =========================
        self.EAR_THRESHOLD = 0.21
        self.MAR_THRESHOLD = 0.6
        self.HEAD_PITCH_THRESHOLD = 15

        self.DROWSY_TIME_THRESHOLD = 2.0      # Tai xe
        self.STUDENT_TIME_THRESHOLD = 5.0     # Sinh vien

        # =========================
        # TRANG THAI
        # =========================
        self.drowsy_start_time = None
        self.is_alerting = False
        self.alert_thread = None
        self.stop_alert = False

        # =========================
        # THONG KE
        # =========================
        self.drowsy_count = 0
        self.yawn_count = 0
        self.last_fps = 0
        self.frame_times = []

        # =========================
        # PHAT HIEN NGAP
        # =========================
        self.yawn_start_time = None
        self.is_yawning = False

        # =========================
        # AM THANH
        # =========================
        self.alert_sound = None
        if PYGAME_AVAILABLE:
            sound_path = os.path.join(os.path.dirname(__file__), "assets", "alert.wav")
            if os.path.exists(sound_path):
                self.alert_sound = pygame.mixer.Sound(sound_path)

    # =========================
    # CHE DO
    # =========================
    def set_mode(self, mode):
        if mode in ["student", "driver"]:
            self.mode = mode
            self.drowsy_start_time = None
            self.stop_alerting()

    def get_drowsy_time_threshold(self):
        if self.mode == "driver":
            return self.DROWSY_TIME_THRESHOLD
        return self.STUDENT_TIME_THRESHOLD

    # =========================
    # NGAP
    # =========================
    def check_yawn(self, mar):
        yawn_triggered = False

        if mar > self.MAR_THRESHOLD:
            if not self.is_yawning:
                self.is_yawning = True
                self.yawn_start_time = time.time()
        else:
            if self.is_yawning:
                duration = time.time() - self.yawn_start_time
                if duration > 0.5:
                    self.yawn_count += 1
                    yawn_triggered = True
                self.is_yawning = False

        return self.is_yawning, yawn_triggered

    # =========================
    # BUON NGU
    # =========================
    def check_drowsiness(self, ear, head_pitch, mar=0):
        is_drowsy = ear < self.EAR_THRESHOLD or head_pitch > self.HEAD_PITCH_THRESHOLD
        drowsy_duration = 0
        alert_triggered = False

        threshold_time = self.get_drowsy_time_threshold()

        if is_drowsy:
            if self.drowsy_start_time is None:
                self.drowsy_start_time = time.time()

            drowsy_duration = time.time() - self.drowsy_start_time

            if drowsy_duration >= threshold_time:
                if not self.is_alerting:
                    self.trigger_alert()
                    self.drowsy_count += 1
                    alert_triggered = True
        else:
            self.drowsy_start_time = None
            self.stop_alerting()

        return is_drowsy, drowsy_duration, alert_triggered

    # =========================
    # CANH BAO
    # =========================
    def trigger_alert(self):
        self.is_alerting = True
        self.stop_alert = False

        def play_alert():
            while not self.stop_alert:
                if self.alert_sound and PYGAME_AVAILABLE:
                    self.alert_sound.play()
                    time.sleep(0.5)
                else:
                    try:
                        import winsound
                        winsound.Beep(2500, 150)
                        winsound.Beep(3000, 150)
                    except:
                        print("\a")
                time.sleep(0.3)

        self.alert_thread = threading.Thread(target=play_alert, daemon=True)
        self.alert_thread.start()

    def stop_alerting(self):
        self.stop_alert = True
        self.is_alerting = False
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()

    # =========================
    # FPS
    # =========================
    def update_fps(self):
        current_time = time.time()
        self.frame_times.append(current_time)
        self.frame_times = [t for t in self.frame_times if current_time - t < 1.0]
        self.last_fps = len(self.frame_times)
        return self.last_fps

    # =========================
    # TRANG THAI TEXT
    # =========================
    def get_status(self, ear, head_pitch, face_detected, mar=0):
        if not face_detected:
            return "Khong phat hien khuon mat", (128, 128, 128)

        self.check_yawn(mar)
        is_drowsy, duration, _ = self.check_drowsiness(ear, head_pitch, mar)

        if self.is_alerting:
            return "CANH BAO: BUON NGU!", (0, 0, 255)
        elif is_drowsy:
            return f"Dang buon ngu... ({duration:.1f}s)", (0, 165, 255)
        else:
            return "Tinh tao", (0, 255, 0)

    # =========================
    # RESET
    # =========================
    def reset_stats(self):
        self.drowsy_count = 0
        self.yawn_count = 0
        self.drowsy_start_time = None
        self.is_yawning = False
        self.stop_alerting()

    def cleanup(self):
        self.stop_alerting()
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()
