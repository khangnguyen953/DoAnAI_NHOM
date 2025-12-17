# -*- coding: utf-8 -*-
"""
He Thong Canh Bao Tai Xe Ngu Gat (Drowsiness Detection System)
Entry point cua ung dung
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from face_detector import FaceDetector
from alert_system import AlertSystem
from gui import DrowsinessGUI


def main():
    print("=" * 50)
    print("  DROWSINESS DETECTION SYSTEM")
    print("  He Thong Canh Bao Tai Xe Ngu Gat v1.0")
    print("=" * 50)
    print("\nDang khoi tao...")
    
    # Khoi tao cac module
    face_detector = FaceDetector()
    print("[OK] Module nhan dien khuon mat da san sang")
    
    alert_system = AlertSystem()
    print("[OK] Module canh bao da san sang")
    
    # Khoi tao va chay GUI
    app = DrowsinessGUI(face_detector, alert_system)
    print("[OK] Giao dien da san sang")
    print("\nUng dung dang chay...")
    
    app.run()


if __name__ == "__main__":
    main()
