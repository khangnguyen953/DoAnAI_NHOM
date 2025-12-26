"""
Module giao dien nguoi dung
Nguoi phu trach: Ban 3
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class DrowsinessGUI:
    def __init__(self, face_detector, alert_system):
        self.detector = face_detector
        self.alert = alert_system

        # 1️⃣ Tao cua so chinh TRUOC
        self.root = tk.Tk()
        self.root.title("He Thong Canh Bao Tai Xe Ngu Gat")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)

        # 2️⃣ SAU DO moi tao bien Tkinter
        self.mode_var = tk.StringVar(value="student")

        self.cap = None
        self.running = False
        
        # EAR history for graph
        self.ear_history = deque(maxlen=100)
        self.time_history = deque(maxlen=100)
        self.start_time = None
        
        # Blink detection
        self.blink_count = 0
        self.blink_start_time = time.time()
        self.last_ear = 0.3
        self.eye_closed = False
        self.blinks_per_minute = 0
        
        # Night mode
        self.night_mode = False
        
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabel', background='#1a1a2e', foreground='#eee', font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#00d4ff')
        style.configure('Status.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="He Thong Canh Bao Tai Xe Ngu Gat", style='Title.TLabel')
        title.pack(pady=(0, 10))
        
        # Content frame (video + graph side by side)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack()
        
        # Left side - Video
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, padx=5)
        
        self.video_label = tk.Label(left_frame, bg='#0f0f1a')
        self.video_label.pack()
        
        # Right side - Graph + Stats
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, padx=5)
        
        # EAR Graph
        self.fig, self.ax = plt.subplots(figsize=(4, 2.5), facecolor='#1a1a2e')
        self.ax.set_facecolor('#0f0f1a')
        self.ax.set_xlabel('Thoi gian (s)', color='#eee', fontsize=8)
        self.ax.set_ylabel('EAR', color='#eee', fontsize=8)
        self.ax.set_title('Do thi EAR Real-time', color='#00d4ff', fontsize=10)
        self.ax.tick_params(colors='#eee', labelsize=7)
        self.ax.set_ylim(0, 0.5)
        self.ax.axhline(y=0.21, color='#ff6b6b', linestyle='--', linewidth=1, label='Nguong')
        self.line, = self.ax.plot([], [], color='#00d4ff', linewidth=2)
        self.ax.legend(loc='upper right', fontsize=7)
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack()
        
        # Stats frame
        stats_frame = ttk.LabelFrame(right_frame, text="Thong ke", padding=5)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.blink_label = ttk.Label(stats_frame, text="Chop mat: 0 lan/phut")
        self.blink_label.pack(anchor=tk.W)
        
        self.yawn_label = ttk.Label(stats_frame, text="Ngap: 0 lan")
        self.yawn_label.pack(anchor=tk.W)
        
        self.mar_label = ttk.Label(stats_frame, text="MAR: --")
        self.mar_label.pack(anchor=tk.W)
        
        self.blink_status = ttk.Label(stats_frame, text="Trang thai: Binh thuong")
        self.blink_status.pack(anchor=tk.W)
        
        # Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Left info
        left_info = ttk.Frame(info_frame)
        left_info.pack(side=tk.LEFT, expand=True)
        
        self.status_label = ttk.Label(left_info, text="Nhan 'Bat dau' de khoi dong", style='Status.TLabel')
        self.status_label.pack()
        
        self.ear_label = ttk.Label(left_info, text="EAR: --")
        self.ear_label.pack()
        
        self.head_label = ttk.Label(left_info, text="Goc dau: --")
        self.head_label.pack()
        
        # Right info
        right_info = ttk.Frame(info_frame)
        right_info.pack(side=tk.RIGHT, expand=True)
        
        self.fps_label = ttk.Label(right_info, text="FPS: --")
        self.fps_label.pack()
        
        self.count_label = ttk.Label(right_info, text="So lan canh bao: 0")
        self.count_label.pack()
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Cai dat", padding=5)
        settings_frame.pack(fill=tk.X, pady=5)
        
        # EAR threshold
        ear_frame = ttk.Frame(settings_frame)
        ear_frame.pack(fill=tk.X, pady=3)
        ttk.Label(ear_frame, text="Nguong EAR:").pack(side=tk.LEFT)
        self.ear_scale = tk.Scale(ear_frame, from_=0.1, to=0.35, resolution=0.01, 
                                   orient=tk.HORIZONTAL, length=150, bg='#1a1a2e', fg='#eee',
                                   highlightthickness=0, command=self.update_thresholds)
        self.ear_scale.set(0.21)
        self.ear_scale.pack(side=tk.RIGHT)
        
        # Time threshold
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill=tk.X, pady=3)
        ttk.Label(time_frame, text="Thoi gian canh bao (s):").pack(side=tk.LEFT)
        self.time_scale = tk.Scale(time_frame, from_=0.5, to=5.0, resolution=0.5,
                                    orient=tk.HORIZONTAL, length=150, bg='#1a1a2e', fg='#eee',
                                    highlightthickness=0, command=self.update_thresholds)
        self.time_scale.set(2.0)
        self.time_scale.pack(side=tk.RIGHT)
        mode_frame = ttk.Frame(settings_frame)
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Label(mode_frame, text="Che do su dung:").pack(side=tk.LEFT)

        ttk.Radiobutton(
            mode_frame,
            text="Sinh vien (5s)",
            variable=self.mode_var,
            value="student",
            command=self.update_mode
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Tai xe (2s)",
            variable=self.mode_var,
            value="driver",
            command=self.update_mode
        ).pack(side=tk.LEFT, padx=5)

        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Bat dau", command=self.toggle_camera,
                                    bg='#00d4ff', fg='#000', font=('Segoe UI', 10, 'bold'),
                                    width=12, height=1, cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.night_btn = tk.Button(btn_frame, text="Ban dem: TAT", command=self.toggle_night_mode,
                                    bg='#4a4a6a', fg='#fff', font=('Segoe UI', 10, 'bold'),
                                    width=12, height=1, cursor='hand2')
        self.night_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_stats,
                                    bg='#ff6b6b', fg='#fff', font=('Segoe UI', 10, 'bold'),
                                    width=12, height=1, cursor='hand2')
        self.reset_btn.pack(side=tk.LEFT, padx=5)
    
    def toggle_night_mode(self):
        self.night_mode = not self.night_mode
        if self.night_mode:
            self.night_btn.config(text="Ban dem: BAT", bg='#ffa500')
        else:
            self.night_btn.config(text="Ban dem: TAT", bg='#4a4a6a')
    
    def apply_night_mode(self, frame):
        """Tang do sang va contrast cho che do ban dem"""
        if not self.night_mode:
            return frame
        
        # Tang do sang va contrast
        alpha = 1.5  # Contrast
        beta = 30    # Brightness
        adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        
        # Giam nhieu
        adjusted = cv2.GaussianBlur(adjusted, (3, 3), 0)
        
        return adjusted
    
    def detect_blink(self, ear):
        """Phat hien chop mat va dem so lan/phut"""
        threshold = self.ear_scale.get()
        
        # Phat hien mat nhap
        if ear < threshold and not self.eye_closed and self.last_ear >= threshold:
            self.eye_closed = True
        
        # Phat hien mat mo lai = 1 lan chop
        if ear >= threshold and self.eye_closed:
            self.eye_closed = False
            self.blink_count += 1
        
        self.last_ear = ear
        
        # Tinh so lan chop mat / phut
        elapsed = time.time() - self.blink_start_time
        if elapsed >= 10:  # Cap nhat moi 10 giay
            self.blinks_per_minute = int(self.blink_count * (60 / elapsed))
            self.blink_count = 0
            self.blink_start_time = time.time()
        
        return self.blinks_per_minute
    
    def get_blink_status(self, bpm):
        """Danh gia trang thai dua tren so lan chop mat"""
        if bpm < 10:
            return "Tap trung cao", "#00ff00"
        elif bpm < 20:
            return "Binh thuong", "#00d4ff"
        elif bpm < 30:
            return "Hoi met", "#ffa500"
        else:
            return "Rat met moi!", "#ff0000"
    
    def update_graph(self, ear):
        """Cap nhat do thi EAR"""
        if self.start_time is None:
            self.start_time = time.time()
        
        current_time = time.time() - self.start_time
        self.ear_history.append(ear)
        self.time_history.append(current_time)
        
        if len(self.ear_history) > 1:
            self.line.set_data(list(self.time_history), list(self.ear_history))
            self.ax.set_xlim(max(0, current_time - 10), current_time + 0.5)
            
            # Update threshold line
            self.ax.lines[0].set_ydata([self.ear_scale.get(), self.ear_scale.get()])
            
            self.canvas.draw_idle()
    
    def update_thresholds(self, _=None):
        self.alert.set_thresholds(
            ear_thresh=self.ear_scale.get(),
            time_thresh=self.time_scale.get()
        )
    
    def update_mode(self):
        mode = self.mode_var.get()
        self.alert.set_mode(mode)

        if mode == "student":
            self.status_label.config(
                text="Che do: Sinh vien (Canh bao sau 5s)",
                foreground="#00d4ff"
            )
        else:
            self.status_label.config(
                text="Che do: Tai xe (Canh bao sau 2s)",
                foreground="#ff6b6b"
            )

    def toggle_camera(self):
        if not self.running:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_label.config(text="Khong the mo camera!", foreground='#ff6b6b')
            return
        
        self.running = True
        self.start_time = None
        self.ear_history.clear()
        self.time_history.clear()
        self.start_btn.config(text="Dung", bg='#ff6b6b')
        self.update_frame()
    
    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(text="Bat dau", bg='#00d4ff')
        self.alert.stop_alerting()
    
    def update_frame(self):
        if not self.running:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # Mirror
            
            # Apply night mode
            frame = self.apply_night_mode(frame)
            
            # Detect face (now returns mar too)
            ear, mar, head_pitch, face_detected, annotated_frame = self.detector.detect(frame)
            
            # Update blink count
            bpm = self.detect_blink(ear)
            blink_status, blink_color = self.get_blink_status(bpm)
            
            # Update graph
            self.update_graph(ear)
            
            # Update FPS
            fps = self.alert.update_fps()
            
            # Get status (with mar for yawn detection)
            status_text, color = self.alert.get_status(ear, head_pitch, face_detected, mar)
            
            # Draw status on frame
            cv2.putText(annotated_frame, status_text, (10, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(annotated_frame, f"EAR: {ear:.2f}", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, f"Chop mat: {bpm}/phut", (10, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.putText(annotated_frame, f"MAR: {mar:.2f}", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            cv2.putText(
                annotated_frame,
                f"MODE: {self.mode_var.get().upper()}",
                (10, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                2
            )

            # Hien thi khi dang ngap
            if mar > 0.6:
                cv2.putText(annotated_frame, "DANG NGAP!", (10, 125),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            if self.night_mode:
                cv2.putText(annotated_frame, "BAN DEM", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
            
            # Convert to Tkinter format
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((400, 300))
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            
            # Update labels
            color_hex = '#{:02x}{:02x}{:02x}'.format(color[2], color[1], color[0])
            self.status_label.config(text=status_text, foreground=color_hex)
            self.ear_label.config(text=f"EAR: {ear:.3f}")
            self.head_label.config(text=f"Goc dau: {head_pitch:.1f}")
            self.fps_label.config(text=f"FPS: {fps}")
            self.count_label.config(text=f"So lan canh bao: {self.alert.drowsy_count}")
            
            # Update blink stats
            self.blink_label.config(text=f"Chop mat: {bpm} lan/phut")
            self.yawn_label.config(text=f"Ngap: {self.alert.yawn_count} lan")
            self.mar_label.config(text=f"MAR: {mar:.3f}")
            self.blink_status.config(text=f"Trang thai: {blink_status}", foreground=blink_color)
        
        self.root.after(10, self.update_frame)
    
    def reset_stats(self):
        self.alert.reset_stats()
        self.blink_count = 0
        self.blinks_per_minute = 0
        self.blink_start_time = time.time()
        self.ear_history.clear()
        self.time_history.clear()
        self.start_time = None
        self.count_label.config(text="So lan canh bao: 0")
        self.blink_label.config(text="Chop mat: 0 lan/phut")
        self.yawn_label.config(text="Ngap: 0 lan")
    
    def on_closing(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.alert.cleanup()
        self.detector.release()
        plt.close(self.fig)
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
