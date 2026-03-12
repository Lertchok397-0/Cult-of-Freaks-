import os
import shutil
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QPushButton, QMessageBox
from PyQt5.QtCore import QLocale
from utils import UIUtils

class ProductDialog(QDialog):
    def __init__(self, main_app, product=None):
        super().__init__()
        self.main_app = main_app
        self.product = product  # None for add, tuple for edit
        self.selected_image_path = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Add Product" if self.product is None else "Edit Product")
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                background: #000000;
                color: #ffffff;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background: rgba(0, 0, 0, 0.9);
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        layout = QVBoxLayout()

        # Form fields
        form_layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Product name")
        form_layout.addWidget(QLabel("Name:"))
        form_layout.addWidget(self.name_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Price (THB)")
        form_layout.addWidget(QLabel("Price:"))
        form_layout.addWidget(self.price_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Product description")
        self.description_input.setMaximumHeight(100)
        form_layout.addWidget(QLabel("Description:"))
        form_layout.addWidget(self.description_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(["chokers", "cuffs", "other"])
        form_layout.addWidget(QLabel("Category:"))
        form_layout.addWidget(self.category_combo)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 10000)
        self.stock_input.setLocale(QLocale(QLocale.English))
        form_layout.addWidget(QLabel("Stock:"))
        form_layout.addWidget(self.stock_input)

        # Image upload
        image_layout = QHBoxLayout()
        self.image_path_label = QLabel("No image selected")
        image_layout.addWidget(self.image_path_label)

        upload_btn = QPushButton("Upload Image")
        upload_btn.clicked.connect(self.upload_image)
        image_layout.addWidget(upload_btn)

        form_layout.addWidget(QLabel("Image:"))
        form_layout.addLayout(image_layout)

        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_product)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        # Load data if editing
        if self.product:
            self.load_product_data()

        self.setLayout(layout)
        self.resize(500, 400)

    def load_product_data(self):
        self.name_input.setText(self.product[1])
        self.price_input.setText(str(self.product[2]))
        self.description_input.setText(self.product[3] or "")
        self.category_combo.setCurrentText(self.product[5])
        self.stock_input.setValue(self.product[6])
        self.selected_image_path = self.product[4]
        if self.selected_image_path:
            self.image_path_label.setText(os.path.basename(self.selected_image_path))
        else:
            self.image_path_label.setText("No image selected")

    def upload_image(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Product Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Copy to products directory
            products_dir = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\products"
            os.makedirs(products_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            filename = f"{self.name_input.text().replace(' ', '_')}_{int(self.main_app.db.conn.execute('SELECT last_insert_rowid()').fetchone()[0]) + 1}{ext}" if not self.product else f"{self.product[0]}{ext}"
            dest_path = os.path.join(products_dir, filename)
            shutil.copy(file_path, dest_path)
            self.selected_image_path = dest_path
            self.image_path_label.setText(os.path.basename(dest_path))

    def save_product(self):
        name = self.name_input.text().strip()
        try:
            price = float(self.price_input.text())
        except ValueError:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Invalid Price")
            msg.setText("Please enter a valid price.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        description = self.description_input.toPlainText().strip()
        category = self.category_combo.currentText()
        stock = self.stock_input.value()

        if not name:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Missing Name")
            msg.setText("Product name is required.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if self.product:
            # Update
            self.main_app.db.update_product(self.product[0], name, price, description, category, stock, self.selected_image_path)
        else:
            # Add
            self.main_app.db.add_product(name, price, description, category, stock, self.selected_image_path)

        self.accept()