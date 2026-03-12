from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils import UIUtils

class ProductDetailsDialog(QDialog):
    def __init__(self, main_app, product):
        super().__init__()
        self.main_app = main_app
        self.product = product  # product tuple: id, name, price, description, image_path, category, stock_quantity
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Product Details")
        self.setModal(True)
        self.setStyleSheet(UIUtils.get_gothic_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Product image - centered
        image_container = QHBoxLayout()
        image_container.addStretch()

        image_label = QLabel()
        image_label.setFixedSize(300, 300)
        image_label.setStyleSheet("border: 1px solid #555; border-radius: 5px; background: #333;")
        image_label.setAlignment(Qt.AlignCenter)
        if self.product[4]:  # image_path
            pixmap = QPixmap(self.product[4])
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("Image not found")
        else:
            image_label.setText("📸")

        image_container.addWidget(image_label)
        image_container.addStretch()
        layout.addLayout(image_container)

        # Product name
        name_label = QLabel(self.product[1])
        name_label.setFont(QFont("Arial", 20, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #ff6b6b; margin: 10px 0;")
        layout.addWidget(name_label)

        # Price
        price_label = QLabel(f"Price: {self.product[2]:,.0f} ฿ THB")
        price_label.setFont(QFont("Arial", 16))
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(price_label)

        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(desc_label)

        description_text = QLabel(self.product[3] or "No description available.")
        description_text.setWordWrap(True)
        description_text.setStyleSheet("color: #ccc; margin-bottom: 20px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px;")
        layout.addWidget(description_text)

        # Size selection based on category
        self.size_group = QButtonGroup(self)
        category = self.product[5]
        if category in ['cuffs', 'chokers']:
            size_label = QLabel("Select Size:")
            size_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(size_label)

            sizes = ["6-8 inches", "Custom fits"] if category == 'cuffs' else ["12-16 inches", "17-21 inches", "Custom fits"]
            for size in sizes:
                radio = QRadioButton(size)
                self.size_group.addButton(radio)
                layout.addWidget(radio)

            self.custom_size_input = QLineEdit()
            self.custom_size_input.setPlaceholderText(f"Enter custom size (e.g., {'7' if category == 'cuffs' else '14'} inches)")
            self.custom_size_input.setEnabled(False)
            layout.addWidget(self.custom_size_input)

            # Connect custom radio to enable input
            for btn in self.size_group.buttons():
                if btn.text() == "Custom fits":
                    btn.clicked.connect(self.toggle_custom_input)

        # Stock info
        stock_quantity = self.product[6]
        stock_label = QLabel(f"Stock: {stock_quantity}")
        stock_label.setStyleSheet("color: #ff6b6b;" if stock_quantity < 5 else "color: #6bff6b;")
        layout.addWidget(stock_label)

        # Buttons
        btn_layout = QHBoxLayout()
        add_cart_btn = QPushButton("Add to Cart")
        add_cart_btn.clicked.connect(self.add_to_cart)
        btn_layout.addWidget(add_cart_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def toggle_custom_input(self):
        self.custom_size_input.setEnabled(True)
        self.custom_size_input.setFocus()

    def add_to_cart(self):
        category = self.product[5]
        if category in ['cuffs', 'chokers']:
            selected_button = self.size_group.checkedButton()
            if not selected_button:
                msg = UIUtils.create_themed_message_box(self)
                msg.setWindowTitle("Size Required")
                msg.setText("Please select a size.")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return
            selected_size_text = selected_button.text()
            if selected_size_text == "Custom fits":
                custom_text = self.custom_size_input.text().strip()
                if not custom_text:
                    msg = UIUtils.create_themed_message_box(self)
                    msg.setWindowTitle("Custom Size Required")
                    msg.setText("Please enter a custom size.")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()
                    return
                size = custom_text
            else:
                size = selected_size_text
        else:
            size = ""

        stock_quantity = self.product[6]
        if stock_quantity <= 0:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Out of Stock")
            msg.setText(f"{self.product[1]} is currently out of stock.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        success = self.main_app.db.add_to_cart(self.main_app.current_user[0], self.product[0], 1, size)
        if success:
            self.main_app.db.log_user_action(self.main_app.current_user[0], "add_to_cart", f"Added {self.product[1]} (Size: {size}) to cart")
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Added to Cart")
            msg.setText(f"{self.product[1]} has been added to your cart!")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            self.accept()
        else:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText("Failed to add item to cart.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()