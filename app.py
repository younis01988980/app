import cv2
import numpy as np
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class CameraApp(App):
    def build(self):
        self.img = Image()
        self.capture = cv2.VideoCapture(1)  # فتح الكاميرا
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # تحديث كل 1/30 ثانية
        return self.img

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # تحويل إلى الأبيض والأسود
            blurred = cv2.GaussianBlur(gray, (11, 11), 3)  # تقليل الضوضاء بشكل أكبر

            # كشف الدوائر باستخدام HoughCircles مع ضبط الحساسية
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.5, minDist=50,
                                       param1=100, param2=50, minRadius=15, maxRadius=40)

            count = 0
            if circles is not None:
                circles = np.uint16(np.around(circles))
                count = len(circles[0, :])  # عدد الدوائر
                for (x, y, r) in circles[0, :]:
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # رسم الدائرة
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)  # نقطة المركز

            # عرض العدد على الشاشة
            cv2.putText(frame, f'Circles: {count}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # تحويل الصورة إلى Kivy texture
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture

    def on_stop(self):
        self.capture.release()

if __name__ == '__main__':
    CameraApp().run()
