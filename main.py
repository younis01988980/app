import flet as ft
import cv2
import numpy as np
import base64
import threading
from time import sleep

def main(page: ft.Page):
    # إعدادات النافذة
    page.title = "Circle Detection App"
    page.window_min_width = 800
    page.window_min_height = 600
    
    # عناصر الواجهة
    img = ft.Image(fit=ft.ImageFit.CONTAIN)
    count_text = ft.Text(value="Detected Circles: 0", size=20, color="green")
    
    # إضافة العناصر للصفحة
    page.add(
        ft.Column([
            ft.Container(img, expand=True),
            ft.Row([count_text], alignment="center")
        ], expand=True)
    )
    
    # تهيئة الكاميرا
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        count_text.value = "Error: Cannot access camera"
        page.update()
        return

    # دالة معالجة الإطار
    def process_frame(frame):
        # تحويل إلى تدرج رمادي
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # تقليل الضوضاء
        blurred = cv2.GaussianBlur(gray, (11, 11), 3)
        
        # كشف الدوائر
        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.5, minDist=50,
            param1=100, param2=50, minRadius=15, maxRadius=40
        )
        
        count = 0
        if circles is not None:
            circles = np.uint16(np.around(circles))
            count = len(circles[0, :])
            for (x, y, r) in circles[0, :]:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
        
        return frame, count

    # دالة التحديث التلقائي
    def update_loop():
        while True:
            ret, frame = capture.read()
            if not ret:
                continue
            
            # معالجة الإطار
            processed_frame, count = process_frame(frame)
            
            # تحويل الصورة إلى تنسيق base64
            _, buffer = cv2.imencode('.jpg', processed_frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            
            # تحديث العناصر
            count_text.value = f"Detected Circles: {count}"
            img.src_base64 = img_base64
            
            # طلب تحديث الواجهة
            page.update()
            sleep(0.03)

    # بدء التحديث في ثانٍ منفصل
    threading.Thread(target=update_loop, daemon=True).start()

    # إغلاق الكاميرا عند إغلاق التطبيق
    def on_close(e):
        capture.release()
    page.on_close = on_close

ft.app(target=main)
