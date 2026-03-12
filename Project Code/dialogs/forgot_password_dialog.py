from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils import UIUtils

class ForgotPasswordDialog(QDialog):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Forgot Password")
        self.setModal(True)
        self.setStyleSheet(UIUtils.get_gothic_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Reset Password")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ff6b6b; margin-bottom: 20px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Enter your email and phone number to reset your password.")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #ccc; margin-bottom: 20px;")
        layout.addWidget(instructions)

        # Email input
        email_label = QLabel("Email:")
        layout.addWidget(email_label)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        layout.addWidget(self.email_input)

        # Phone input
        phone_label = QLabel("Phone Number:")
        layout.addWidget(phone_label)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter your phone number")
        self.phone_input.textChanged.connect(lambda text: UIUtils.validate_phone_input(self.phone_input, text))
        layout.addWidget(self.phone_input)

        # Buttons
        btn_layout = QHBoxLayout()
        verify_btn = QPushButton("Verify")
        verify_btn.clicked.connect(self.verify_user)
        btn_layout.addWidget(verify_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.resize(400, 300)

    def verify_user(self):
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        if not email or not phone:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Please fill in all fields")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        user = self.main_app.db.verify_user_for_password_reset(email, phone)
        if user:
            # Show password reset dialog
            reset_dialog = PasswordResetDialog(self.main_app, user[0])
            if reset_dialog.exec_() == QDialog.Accepted:
                msg = UIUtils.create_themed_message_box(self)
                msg.setWindowTitle("Success")
                msg.setText("Password updated successfully!")
                msg.setIcon(QMessageBox.Information)
                msg.exec_()
                self.accept()
        else:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("No account found with this email and phone number")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

class PasswordResetDialog(QDialog):
    def __init__(self, main_app, user_id):
        super().__init__()
        self.main_app = main_app
        self.user_id = user_id
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Reset Password")
        self.setModal(True)
        self.setStyleSheet(UIUtils.get_gothic_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Set New Password")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ff6b6b; margin-bottom: 20px;")
        layout.addWidget(title)

        # New password input
        password_label = QLabel("New Password:")
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter new password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Confirm password input
        confirm_label = QLabel("Confirm Password:")
        layout.addWidget(confirm_label)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm new password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        # Buttons
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Reset Password")
        reset_btn.clicked.connect(self.reset_password)
        btn_layout.addWidget(reset_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.resize(400, 250)

    def reset_password(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not password or not confirm:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Please fill in all fields")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if password != confirm:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Passwords do not match")
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

        self.main_app.db.update_user_password(self.user_id, password)
        self.main_app.db.log_user_action(self.user_id, "password_reset", "Password reset via forgot password")
        self.accept()