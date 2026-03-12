import re
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QLineEdit, QPushButton, QLabel, QMessageBox, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QMovie
from utils import UIUtils

class RegisterWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()
        self.setup_video_background()

    def setup_ui(self):
        # Main layout with no margins for fullscreen video
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Graphics view & scene for video background
        self.view = QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: black;")
        self.scene = QGraphicsScene()
        from PyQt5.QtGui import QBrush
        self.scene.setBackgroundBrush(QBrush(Qt.black))
        self.view.setScene(self.scene)
        main_layout.addWidget(self.view)

        # Overlay widget for register form
        self.overlay_widget = QWidget(self)
        self.overlay_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #ffffff;
            }
            QLineEdit {
                background: rgba(0, 0, 0, 0.9);
                border: 2px solid #8b0000;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: white;
            }
            QPushButton {
                background: rgba(139, 0, 0, 0.8);
                border: 2px solid #8b0000;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: rgba(160, 0, 0, 0.9);
                border: 2px solid #a00000;
            }
            QLabel {
                color: #ffffff;
                font-size: 16px;
                background: transparent;
            }
            QFrame {
                background: rgba(0, 0, 0, 0.6);
                border: 2px solid #8b0000;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        overlay_layout = QVBoxLayout()
        overlay_layout.setAlignment(Qt.AlignCenter)


        # Title
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("""
            color: #ffffff;
            background: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        """)
        overlay_layout.addWidget(title)

        # Register form
        form_widget = QFrame()
        form_widget.setMaximumWidth(450)
        form_layout = QVBoxLayout()

        form_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose username")
        form_layout.addWidget(self.username_input)

        form_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        form_layout.addWidget(self.email_input)

        form_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose password")
        form_layout.addWidget(self.password_input)

        form_layout.addWidget(QLabel("Confirm Password:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        form_layout.addWidget(self.confirm_password_input)

        form_layout.addWidget(QLabel("Address:"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter your address")
        form_layout.addWidget(self.address_input)

        form_layout.addWidget(QLabel("Phone Number:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter your phone number (numbers only)")
        self.phone_input.setMaxLength(10)  # Thai phone numbers are typically 10 digits
        self.phone_input.textChanged.connect(lambda text: UIUtils.validate_phone_input(self.phone_input, text))
        form_layout.addWidget(self.phone_input)

        # Buttons
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.clicked.connect(self.main_app.show_login)
        form_layout.addWidget(back_btn)

        form_widget.setLayout(form_layout)
        overlay_layout.addWidget(form_widget)
        self.overlay_widget.setLayout(overlay_layout)

    def setup_video_background(self):
        # GIF background using QLabel and QMovie
        self.gif_label = QLabel()
        self.gif_label.setScaledContents(True)
        self.gif_label.setStyleSheet("background: black;")

        # Create QMovie for GIF
        self.movie = QMovie(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\truesky.gif")
        self.movie.setScaledSize(QSize(1280, 720))  # Initial size, will be resized
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        # Add to scene
        self.scene.addWidget(self.gif_label)

    # Removed loop_video method as GIF loops automatically

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'gif_label') and hasattr(self, 'view'):
            w = self.width()
            h = self.height()

            # Update scene and GIF size efficiently
            self.scene.setSceneRect(0, 0, w, h)
            self.gif_label.setGeometry(0, 0, w, h)
            self.movie.setScaledSize(QSize(w, h))

            # Use more efficient view fitting
            self.view.setGeometry(0, 0, w, h)
            self.view.resetTransform()
            self.view.scale(1.0, 1.0)

            # Position overlay widget
            if hasattr(self, 'overlay_widget'):
                self.overlay_widget.setGeometry(0, 0, w, h)

    def showEvent(self, event):
        super().showEvent(event)
        # Ensure GIF starts properly when widget is shown
        if hasattr(self, 'movie'):
            self.movie.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        # Stop GIF when widget is hidden to prevent lag
        if hasattr(self, 'movie'):
            self.movie.stop()

    def register(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        address = self.address_input.text()
        phone_number = self.phone_input.text()

        if not all([username, email, password, confirm_password, address, phone_number]):
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Please fill in all fields")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Validate username: English only (letters, numbers, underscores)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Username must contain only English letters, numbers, and underscores")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Validate email: must contain @ and English only (ASCII characters)
        if '@' not in email:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Email must contain @ symbol")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if not email.isascii():
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Email must contain only English characters")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if password != confirm_password:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Passwords do not match")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Validate password: English only (ASCII characters) and at least one uppercase letter
        if not password.isascii():
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Password must contain only English characters")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if not re.search(r'[A-Z]', password):
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Password must contain at least one uppercase letter")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if len(password) < 6:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Password must be at least 6 characters")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if len(phone_number) < 10:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Phone number must be at least 10 digits")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if self.main_app.db.register_user(username, email, password, address, phone_number):
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Success")
            msg.setText("Account created successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            self.main_app.show_login()
        else:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Username or email already exists")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()