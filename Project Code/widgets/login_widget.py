from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QLineEdit, QPushButton, QLabel, QMessageBox, QFrame
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtCore import QUrl, Qt, QSizeF, QSize
from PyQt5.QtGui import QPixmap, QBrush, QFont, QPalette, QMovie
from utils import UIUtils

class LoginWidget(QWidget):
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
        self.scene.setBackgroundBrush(QBrush(Qt.black))
        self.view.setScene(self.scene)
        main_layout.addWidget(self.view)

        # Overlay widget for login form (transparent background)
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

        # Logo image only
        logo_pixmap = QPixmap(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\icon.png")
        logo_label = QLabel()
        if not logo_pixmap.isNull():
            # Scale logo to appropriate size (e.g., 150x150 pixels)
            scaled_logo = logo_pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            # Fallback if logo can't be loaded
            logo_label.setText("🔺")
            logo_label.setStyleSheet("font-size: 60px; color: #8b0000;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent; margin-bottom: 30px;")
        overlay_layout.addWidget(logo_label)

        # Login form with dark semi-transparent background
        form_widget = QFrame()
        form_widget.setMaximumWidth(450)
        form_layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        form_layout.addWidget(self.password_input)

        # Buttons
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

        register_btn = QPushButton("Register New Account")
        register_btn.clicked.connect(self.show_register)
        form_layout.addWidget(register_btn)

        # Forgot password button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8b0000;
                text-decoration: underline;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #a00000;
            }
        """)
        forgot_btn.clicked.connect(self.show_forgot_password)
        form_layout.addWidget(forgot_btn)

        # Contact information
        contact_label = QLabel("Contact: LINE 0864739813 | IG bloodyluckthislife.15")
        contact_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 10px;")
        contact_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(contact_label)

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

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Please fill in all fields")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        user = self.main_app.db.login_user(username, password)
        if user:
            self.main_app.current_user = user
            self.main_app.db.log_user_action(user[0], "login", f"User {username} logged in")
            self.main_app.show_store()
        else:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Invalid username or password")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def show_register(self):
        self.main_app.show_register()

    def show_forgot_password(self):
        from dialogs.forgot_password_dialog import ForgotPasswordDialog
        dialog = ForgotPasswordDialog(self.main_app)
        dialog.exec_()