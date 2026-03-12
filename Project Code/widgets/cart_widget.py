from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QAbstractButton, QMessageBox, QDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils import UIUtils
from dialogs.payment_dialog import PaymentDialog

class CartWidget(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #000000;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            QPushButton {
                background: #8b0000;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #a00000;
            }
            QLabel {
                color: #000000;
            }
            QFrame {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()

        title = QLabel("Shopping Cart")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAttribute(Qt.WA_TranslucentBackground)
        title.setStyleSheet("color: white; background: transparent; margin-bottom: 20px;")
        header.addWidget(title)

        header.addStretch()

        back_btn = QPushButton("Back to Store")
        back_btn.clicked.connect(self.main_app.show_store)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        header.addWidget(back_btn)

        layout.addLayout(header)

        # Cart content as table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Size", "Price", "Stock", "Quantity", "Total"])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background: #1a1a1a;
                border: 1px solid #333;
                gridline-color: #333;
                selection-background-color: #333;
            }
            QTableWidget::item {
                background: #1a1a1a;
                padding: 8px;
                border-bottom: 1px solid #333;
                color: white;
            }
            QHeaderView::section {
                background: #333;
                padding: 12px;
                border: 1px solid #555;
                font-weight: bold;
                color: white;
                font-size: 12px;
            }
                QTableCornerButton::section {
                  background: #333;
                border: 1px solid #555;
            }
            QTableWidget QAbstractButton {
                background: #333;
                border: 1px solid #555;
            }
        """)
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setCornerButtonEnabled(True)
        self.cart_table.setStyleSheet(self.cart_table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #222;
            }
        """)

        # Hide the corner button
        corner_button = self.cart_table.findChild(QAbstractButton)
        if corner_button:
            corner_button.setVisible(False)

        # Set row height for bigger images
        self.cart_table.verticalHeader().setDefaultSectionSize(100)

        # Set column widths
        self.cart_table.setColumnWidth(0, 300)  # Product (wider for bigger image)
        self.cart_table.setColumnWidth(1, 120)  # Size
        self.cart_table.setColumnWidth(2, 120)  # Price
        self.cart_table.setColumnWidth(3, 100)  # Stock
        self.cart_table.setColumnWidth(4, 140)  # Quantity
        self.cart_table.setColumnWidth(5, 120)  # Total

        # Add context menu for removing items
        self.cart_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cart_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.cart_table)
        self.load_cart_items()

        # Footer with total and checkout
        footer = QFrame()
        footer.setStyleSheet("background: #1a1a1a; border: 1px solid #8b0000; border-radius: 10px; padding: 15px;")
        footer_layout = QVBoxLayout()

        # Subtotal
        self.subtotal_label = QLabel("Subtotal: 0.00 ฿ THB")
        self.subtotal_label.setFont(QFont("Arial", 14))
        self.subtotal_label.setStyleSheet("color: #ffffff;")
        footer_layout.addWidget(self.subtotal_label)

        # VAT
        self.vat_label = QLabel("VAT (7%): 0.00 ฿ THB")
        self.vat_label.setFont(QFont("Arial", 14))
        self.vat_label.setStyleSheet("color: #ff6b6b;")
        footer_layout.addWidget(self.vat_label)

        # Total
        self.total_label = QLabel("Total: 0.00 ฿ THB")
        self.total_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.total_label.setStyleSheet("color: #ff6b6b; margin-top: 10px;")
        footer_layout.addWidget(self.total_label)

        # Checkout button
        checkout_btn = QPushButton("Checkout")
        checkout_btn.clicked.connect(self.checkout)
        checkout_btn.setStyleSheet("""
            QPushButton {
                background: #8b0000;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        footer_layout.addWidget(checkout_btn)

        footer.setLayout(footer_layout)
        layout.addWidget(footer)

        self.setLayout(layout)
        self.update_total()

    def load_cart_items(self):
        # Clear existing items
        self.cart_table.setRowCount(0)

        # Get cart items from database
        cart_items = self.main_app.db.get_cart_items(self.main_app.current_user[0])

        if not cart_items:
            # Add empty row with message
            self.cart_table.setRowCount(1)
            empty_item = QTableWidgetItem("Your cart is empty")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setForeground(Qt.white)
            self.cart_table.setItem(0, 0, empty_item)
            self.cart_table.setSpan(0, 0, 1, 6)  # Span across all columns
            return

        self.cart_table.setRowCount(len(cart_items))

        for row, item in enumerate(cart_items):
            cart_id, product_id, name, price, quantity, stock, total_price, image_path, size = item

            # Product column with image and name
            product_widget = QWidget()
            product_layout = QHBoxLayout()
            product_layout.setContentsMargins(8, 8, 8, 8)
            product_layout.setSpacing(15)

            # Bigger thumbnail image
            image_label = QLabel()
            image_label.setFixedSize(80, 80)
            image_label.setStyleSheet("border: 1px solid #555; border-radius: 5px;")
            if image_path:
                from PyQt5.QtGui import QPixmap
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("No img")
                    image_label.setAlignment(Qt.AlignCenter)
                    image_label.setStyleSheet("color: #666; font-size: 10px;")
            else:
                image_label.setText("No img")
                image_label.setAlignment(Qt.AlignCenter)
                image_label.setStyleSheet("color: #666; font-size: 10px;")
            product_layout.addWidget(image_label)

            # Product name
            name_label = QLabel(name)
            name_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
            name_label.setWordWrap(True)
            product_layout.addWidget(name_label)

            product_widget.setLayout(product_layout)
            self.cart_table.setCellWidget(row, 0, product_widget)

            # Size column
            size_item = QTableWidgetItem(size if size else "N/A")
            size_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 1, size_item)

            # Price column
            price_item = QTableWidgetItem(f"{price:,.0f} ฿")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 2, price_item)

            # Stock column
            stock_item = QTableWidgetItem(str(stock))
            stock_item.setTextAlignment(Qt.AlignCenter)
            if stock < 5:
                stock_item.setForeground(Qt.red)
            else:
                stock_item.setForeground(Qt.green)
            self.cart_table.setItem(row, 3, stock_item)

            # Quantity column with controls
            qty_widget = QWidget()
            qty_layout = QHBoxLayout()
            qty_layout.setContentsMargins(5, 5, 5, 5)
            qty_layout.setSpacing(5)

            minus_btn = QPushButton("-")
            minus_btn.setFixedSize(25, 25)
            minus_btn.clicked.connect(lambda checked, cid=cart_id, q=quantity: self.update_quantity(cid, q - 1))
            qty_layout.addWidget(minus_btn)

            qty_label = QLabel(str(quantity))
            qty_label.setAlignment(Qt.AlignCenter)
            qty_label.setStyleSheet("color: white; font-weight: bold; min-width: 30px;")
            qty_layout.addWidget(qty_label)

            plus_btn = QPushButton("+")
            plus_btn.setFixedSize(25, 25)
            plus_btn.clicked.connect(lambda checked, cid=cart_id, q=quantity: self.update_quantity(cid, q + 1))
            qty_layout.addWidget(plus_btn)

            qty_widget.setLayout(qty_layout)
            self.cart_table.setCellWidget(row, 4, qty_widget)

            # Total column
            total_item = QTableWidgetItem(f"{total_price:,.0f} ฿")
            total_item.setTextAlignment(Qt.AlignCenter)
            total_item.setFont(QFont("Arial", 10, QFont.Bold))
            total_item.setForeground(Qt.red)
            self.cart_table.setItem(row, 5, total_item)


    def update_quantity(self, cart_id, new_quantity):
        self.main_app.db.update_cart_quantity(cart_id, new_quantity)
        self.load_cart_items()
        self.update_total()

    def show_context_menu(self, position):
        if self.cart_table.itemAt(position) is None:
            return

        row = self.cart_table.itemAt(position).row()
        if row < 0 or row >= len(self.main_app.db.get_cart_items(self.main_app.current_user[0])):
            return

        # Get cart_id from the current cart items
        cart_items = self.main_app.db.get_cart_items(self.main_app.current_user[0])
        if row < len(cart_items):
            cart_id = cart_items[row][0]

            from PyQt5.QtWidgets import QMenu
            menu = QMenu()
            remove_action = menu.addAction("Remove Item")
            remove_action.triggered.connect(lambda: self.remove_item(cart_id))

            menu.exec_(self.cart_table.mapToGlobal(position))

    def remove_item(self, cart_id):
        self.main_app.db.remove_from_cart(cart_id)
        self.load_cart_items()
        self.update_total()

    def update_total(self):
        cart_items = self.main_app.db.get_cart_items(self.main_app.current_user[0])
        subtotal = sum(item[6] for item in cart_items)
        vat_rate = 0.07
        vat_amount = subtotal * vat_rate
        total = subtotal + vat_amount

        self.subtotal_label.setText(f"Subtotal: {subtotal:,.0f} ฿ THB")
        self.vat_label.setText(f"VAT (7%): {vat_amount:,.0f} ฿ THB")
        self.total_label.setText(f"Total: {total:,.0f} ฿ THB")

    def show_themed_warning(self, title, message):
        msg = UIUtils.create_themed_message_box(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def checkout(self):
        # Check if cart is empty
        cart_items = self.main_app.db.get_cart_items(self.main_app.current_user[0])
        if not cart_items:
            self.show_themed_warning("Cart Empty", "Your cart is empty.")
            return

        # Validate checkout (check stock, calculate total with VAT)
        success, message, total_amount, subtotal, vat_amount = self.main_app.db.validate_checkout(self.main_app.current_user[0])
        if not success:
            self.show_themed_warning("Checkout Failed", message)
            return

        # Show payment dialog (no order created yet)
        payment_dialog = PaymentDialog(self.main_app, cart_items, total_amount, subtotal, vat_amount, None)
        if payment_dialog.exec_() == QDialog.Accepted:
            # Order will be created in PaymentDialog.upload_proof
            # Show social media popup
            social_msg = UIUtils.create_themed_message_box(self)
            social_msg.setWindowTitle("Follow Us!")
            social_msg.setText("Thank you for your purchase!\n\nPlease add our accounts for order updates and tracking:\n\nInstagram: bloodyluckthislife.15\nLINE: 0864739813\n\nChat with us directly to track your package!")
            social_msg.setIcon(QMessageBox.Information)
            social_msg.exec_()
            self.load_cart_items()
            self.update_total()
        else:
            # Payment canceled, no order created
            pass