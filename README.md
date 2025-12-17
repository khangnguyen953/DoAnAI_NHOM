# Hệ Thống Cảnh Báo Tài Xế Ngủ Gật (Drowsiness Detection)

## Mô tả
Hệ thống sử dụng camera để theo dõi mắt và tư thế đầu của tài xế. Nếu phát hiện mắt nhắm quá lâu hoặc gục đầu, hệ thống sẽ phát âm thanh cảnh báo.

## Công nghệ sử dụng
- Python 3.8+
- OpenCV - Xử lý video
- MediaPipe - Nhận diện khuôn mặt và landmarks
- Tkinter - Giao diện Desktop
- Pygame - Phát âm thanh cảnh báo

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy chương trình

```bash
python main.py
```

## Phân chia công việc nhóm
1. **Bạn 1**: Model nhận diện khuôn mặt/mắt (`face_detector.py`)
2. **Bạn 2**: Logic cảnh báo và tối ưu FPS (`alert_system.py`)
3. **Bạn 3**: Giao diện và tích hợp (`gui.py`, `main.py`)

## Cấu trúc thư mục
```
AI_Group/
├── main.py              # Entry point
├── face_detector.py     # Module nhận diện khuôn mặt
├── alert_system.py      # Module cảnh báo
├── gui.py               # Giao diện Tkinter
├── assets/
│   └── alert.wav        # Âm thanh cảnh báo
└── requirements.txt
```

