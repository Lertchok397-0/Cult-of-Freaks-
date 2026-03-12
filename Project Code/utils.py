import sys
import os
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QSize

class UIUtils:
    """Utility class for common UI operations"""

    @staticmethod
    def validate_phone_input(line_edit, text):
        """Validate phone number input - allow only digits"""
        if not text.isdigit() and text != "":
            cleaned_text = ''.join(filter(str.isdigit, text))
            line_edit.setText(cleaned_text)

    @staticmethod
    def create_themed_message_box(parent=None):
        """Create a themed QMessageBox with consistent styling"""
        msg = QMessageBox(parent)
        msg.setStyleSheet("""
            QMessageBox {
                background: #000000;
                color: #ffffff;
                border: 2px solid #8b0000;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QPushButton {
                background: #8b0000;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                color: white;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        return msg

    @staticmethod
    def apply_table_styling(table):
        """Apply consistent gothic styling to QTableWidget"""
        table.setStyleSheet("""
            QTableWidget {
                background: #1a1a1a;
                border: 1px solid #333;
                gridline-color: #333;
                selection-background-color: #333;
            }
            QTableWidget::item {
                background: #1a1a1a;
                padding: 5px;
                border-bottom: 1px solid #333;
                color: white;
            }
            QHeaderView::section {
                background: #333;
                padding: 5px;
                border: 1px solid #555;
                font-weight: bold;
                color: white;
                font-size: 12px;
            }
        """)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #222;
            }
        """)

    @staticmethod
    def get_gothic_stylesheet():
        """Get the main gothic stylesheet"""
        return """
            QWidget {
                background: #000000;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
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
            }
            QFrame {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 5px;
            }
        """

    @staticmethod
    def show_payment_proof_dialog(parent, db, order_id):
        """Utility method to show payment proof dialog - eliminates duplicate code"""
        cursor = db.conn.cursor()
        cursor.execute('SELECT image_path FROM payment_proofs WHERE order_id = ?', (int(order_id),))
        proof = cursor.fetchone()
        if proof and proof[0] and os.path.exists(proof[0]):
            dialog = QDialog(parent)
            dialog.setWindowTitle(f"Payment Proof - Order #{order_id}")
            dialog.setModal(True)
            dialog.setStyleSheet(UIUtils.get_gothic_stylesheet())
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)

            proof_image = QLabel()
            proof_image.setStyleSheet("border: 2px solid #666; border-radius: 5px;")
            pixmap = QPixmap(proof[0])
            if not pixmap.isNull():                
                max_size = QSize(800, 600)  
                scaled_pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                proof_image.setPixmap(scaled_pixmap)
            else:
                proof_image.setText("Payment proof image not available")
                proof_image.setAlignment(Qt.AlignCenter)
            layout.addWidget(proof_image)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn, alignment=Qt.AlignCenter)

            dialog.setLayout(layout)
            dialog.adjustSize() 
            dialog.exec_()
        else:
            msg = UIUtils.create_themed_message_box(parent)
            msg.setWindowTitle("Payment Proof Not Found")
            msg.setText(f"Payment proof for order #{order_id} not found.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()