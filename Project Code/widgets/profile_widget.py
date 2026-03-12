import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QLineEdit, QMessageBox, QFileDialog, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils import UIUtils

class ProfileWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()

    def setup_ui(self):
        # บังคับ background ทั้งหน้า
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #111111;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #8b0000;
                border: none;
                border-radius: 5px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QHBoxLayout()
        title = QLabel("User Profile")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        header.addWidget(title)
        header.addStretch()
        back_btn = QPushButton("← Back to Store")
        back_btn.clicked.connect(self.main_app.show_store)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        header.addWidget(back_btn)
        layout.addLayout(header)

        # Profile picture in the center above details
        profile_pic_container = QHBoxLayout()
        profile_pic_container.addStretch()

        # Profile picture frame
        self.profile_pic_frame = QFrame()
        self.profile_pic_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 4px solid #8b0000;
                border-radius: 25px;
            }
        """)

        pic_layout = QVBoxLayout()
        pic_layout.setContentsMargins(0, 0, 0, 0)
        pic_layout.setAlignment(Qt.AlignCenter)

        # Profile picture label - made really big
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setAlignment(Qt.AlignCenter)
        self.profile_pic_label.setStyleSheet("""
            QLabel {
                background: #333;
                border: 3px solid #555;
                border-radius: 15px;
            }
        """)
        self.profile_pic_label.setAlignment(Qt.AlignCenter)
        self.profile_pic_label.setText("No Profile Picture")
        pic_layout.addWidget(self.profile_pic_label)

        # Upload button
        upload_btn = QPushButton("Upload Picture")
        upload_btn.clicked.connect(self.upload_profile_picture)
        upload_btn.setStyleSheet("""
            QPushButton {
                background: #8b0000;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        pic_layout.addWidget(upload_btn, alignment=Qt.AlignCenter)

        self.profile_pic_frame.setLayout(pic_layout)
        profile_pic_container.addWidget(self.profile_pic_frame)
        profile_pic_container.addStretch()

        layout.addLayout(profile_pic_container)

        # Profile details below the picture
        details_frame = QFrame()
        details_frame.setMaximumWidth(600)
        details_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid #555;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        details_layout = QFormLayout()
        details_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        details_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(15, 15, 15, 15)

        # Username (read-only)
        self.username_input = QLineEdit()
        self.username_input.setReadOnly(True)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: #333;
                color: #ccc;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        details_layout.addRow("Username:", self.username_input)

        # Email (editable)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 13px;
            }
        """)
        details_layout.addRow("Email:", self.email_input)

        # Address (editable)
        self.address_input = QLineEdit()
        self.address_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 13px;
            }
        """)
        details_layout.addRow("Address:", self.address_input)

        # Phone number (editable)
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                color: white;
                font-size: 13px;
            }
        """)
        self.phone_input.textChanged.connect(lambda text: UIUtils.validate_phone_input(self.phone_input, text))
        details_layout.addRow("Phone Number:", self.phone_input)

        # Role (read-only)
        self.role_input = QLineEdit()
        self.role_input.setReadOnly(True)
        self.role_input.setStyleSheet("""
            QLineEdit {
                background: #333;
                color: #ccc;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        details_layout.addRow("Role:", self.role_input)

        # Created at (read-only)
        self.created_input = QLineEdit()
        self.created_input.setReadOnly(True)
        self.created_input.setStyleSheet("""
            QLineEdit {
                background: #333;
                color: #ccc;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        details_layout.addRow("Member Since:", self.created_input)

        details_frame.setLayout(details_layout)

        # Center the details frame
        details_container = QHBoxLayout()
        details_container.addStretch()
        details_container.addWidget(details_frame)
        details_container.addStretch()

        layout.addLayout(details_container)

        # Buttons at bottom
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 30, 0, 0)
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_profile)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #8b0000;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_profile()

    def load_profile(self):
        profile = self.main_app.db.get_user_profile(self.main_app.current_user[0])
        if profile:
            self.username_input.setText(profile[0])
            self.email_input.setText(profile[1])
            self.address_input.setText(profile[2] or "")
            self.phone_input.setText(profile[3] or "")
            self.role_input.setText(profile[4])
            self.created_input.setText(profile[5])

            # Load profile picture
            profile_picture_path = profile[6] if len(profile) > 6 else None
            if profile_picture_path and os.path.exists(profile_picture_path):
                pixmap = QPixmap(profile_picture_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.profile_pic_label.setPixmap(scaled_pixmap)
                else:
                    self.profile_pic_label.setText("Invalid Image")
            else:
                self.profile_pic_label.setText("No Profile Picture")

    def upload_profile_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Create profile_pictures directory if it doesn't exist
            profile_dir = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\profile_pictures"
            os.makedirs(profile_dir, exist_ok=True)

            # Copy file with user ID as filename
            ext = os.path.splitext(file_path)[1]
            filename = f"{self.main_app.current_user[0]}{ext}"
            dest_path = os.path.join(profile_dir, filename)
            shutil.copy(file_path, dest_path)

            # Update database
            current_profile = self.main_app.db.get_user_profile(self.main_app.current_user[0])
            if current_profile:
                username, email, address, phone_number, role, created_at, _ = current_profile
                self.main_app.db.update_user_data(self.main_app.current_user[0], username, email, "", address, phone_number, role, dest_path)

            # Update UI
            pixmap = QPixmap(dest_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.profile_pic_label.setPixmap(scaled_pixmap)
            else:
                self.profile_pic_label.setText("Invalid Image")

            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Success")
            msg.setText("Profile picture updated successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()

    def save_profile(self):
        address = self.address_input.text()
        phone_number = self.phone_input.text()
        email = self.email_input.text().strip()

        if not address:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Address cannot be empty")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if not email:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Email cannot be empty")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if phone_number and len(phone_number) < 10:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Phone number must be at least 10 digits")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Check email uniqueness (excluding current user)
        cursor = self.main_app.db.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, self.main_app.current_user[0]))
        if cursor.fetchone():
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Email already exists")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Get current user data
        current_profile = self.main_app.db.get_user_profile(self.main_app.current_user[0])
        if current_profile:
            username, current_email, current_address, current_phone, role, created_at, profile_picture = current_profile
            # For profile updates, we keep the existing password and profile picture
            self.main_app.db.update_user_data(self.main_app.current_user[0], username, email, "", address, phone_number, role, profile_picture)
            self.main_app.db.log_user_action(self.main_app.current_user[0], "profile_update", "Updated profile information")
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Success")
            msg.setText("Profile updated successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()