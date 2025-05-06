# remove_bg_gui.py
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap
from rembg import remove
from PIL import Image
import sys
import io

class BackgroundRemover(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إزالة خلفية الصورة")
        self.layout = QVBoxLayout()
        
        self.select_button = QPushButton("اختيار صورة")
        self.select_button.clicked.connect(self.select_image)

        self.label = QLabel("لم يتم اختيار صورة")
        self.label.setScaledContents(True)

        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    input_data = f.read()
                output_data = remove(input_data)

                image = Image.open(io.BytesIO(output_data)).convert("RGBA")
                temp_path = "output.png"
                image.save(temp_path)

                pixmap = QPixmap(temp_path)
                self.label.setPixmap(pixmap)
                self.label.setFixedSize(pixmap.width(), pixmap.height())

            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل إزالة الخلفية:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackgroundRemover()
    window.show()
    sys.exit(app.exec())
