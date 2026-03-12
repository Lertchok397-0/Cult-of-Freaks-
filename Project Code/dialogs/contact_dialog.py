from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils import UIUtils

class ContactDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact ME!!!")
        self.setModal(True)
        self.setStyleSheet(UIUtils.get_gothic_stylesheet())
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Contact Information")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ff6b6b; margin-bottom: 20px;")
        layout.addWidget(title)

        # Profile picture above contact info
        profile_pixmap = QPixmap(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\WanWan.jpg")
        profile_label = QLabel()
        if not profile_pixmap.isNull():
            scaled_profile = profile_pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            profile_label.setPixmap(scaled_profile)
        else:
            profile_label.setText("Profile Picture")
            profile_label.setStyleSheet("color: #666; font-size: 12px;")
        profile_label.setAlignment(Qt.AlignCenter)
        profile_label.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(profile_label)

        # Contact info
        contact_info = QLabel("""
Get in touch with ME!

Email:Lertchok.s@kkumail.com
Instagram: bloodyluckthislife.15 (mostly active)
Phone: 0984903235
ID:673050397-0

hi, my name is Lertchok Sriwattanasub, but u can call me Buck! feel free to get in touch :D
        """)
        contact_info.setFont(QFont("Arial", 14))
        contact_info.setAlignment(Qt.AlignCenter)
        contact_info.setStyleSheet("color: #ffffff; line-height: 1.5;")
        layout.addWidget(contact_info)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.resize(400, 350)