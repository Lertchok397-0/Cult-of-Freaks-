from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QAbstractButton, QLabel, QPushButton, QLineEdit, QComboBox, QDialog, QMessageBox, QFrame, QDateEdit, QScrollArea
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap
import os
from utils import UIUtils
from dialogs.product_dialog import ProductDialog

class AdminWidget(QWidget):
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
                color: #ffffff;
            }
            QTableWidget {
                background: #1a1a1a;
                border: 1px solid #333;
                gridline-color: #333;
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
            }
            QTabWidget::pane {
                border: none; solid #333;
                background: #000000;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #000000;
                color: #ffffff;
                padding: 10px 25px;
                margin: 0px;
                border: 1px solid #444;
                border-bottom: none;
                font-weight: bold;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #222222;
                color: #ffffff;
                border-bottom: 2px solid #8b0000;
            }
            QTabBar::tab:hover {
                background: #333333;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        header.addWidget(title)
        header.addStretch()
        back_btn = QPushButton("← Back to Store")
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

        # Tabs for Users, Orders and Logs
        self.tab_widget = QTabWidget()
        self.setup_users_tab()
        self.setup_orders_tab()
        self.setup_logs_tab()
        self.setup_products_tab()
        self.setup_trading_summary_tab()
        self.setup_product_stats_tab()
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

    def setup_users_tab(self):
        users_tab = QWidget()
        layout = QVBoxLayout()

        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Password", "Address", "Phone", "Role", "Created"])
        self.users_table.verticalHeader().setVisible(False)
        UIUtils.apply_table_styling(self.users_table)
        self.users_table.itemDoubleClicked.connect(self.edit_user_from_table)
        self.load_users()
        layout.addWidget(self.users_table)

        users_tab.setLayout(layout)
        self.tab_widget.addTab(users_tab, "Users")

    def setup_orders_tab(self):
        orders_tab = QWidget()
        layout = QVBoxLayout()

        # Search and refresh
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Order by ID:"))
        self.order_search_input = QLineEdit()
        self.order_search_input.setPlaceholderText("Enter Order ID")
        self.order_search_input.textChanged.connect(self.load_orders)
        search_layout.addWidget(self.order_search_input)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_orders)
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "User ID", "Total Amount", "Status", "Created At"])
        self.orders_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.orders_table)
        self.orders_table.itemDoubleClicked.connect(self.on_order_double_clicked)
        self.load_orders()
        layout.addWidget(self.orders_table)

        orders_tab.setLayout(layout)
        self.tab_widget.addTab(orders_tab, "Order")

    def setup_logs_tab(self):
        logs_tab = QWidget()
        logs_tab.setStyleSheet("""
            QWidget {
                background: #000000;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
        """)
        layout = QVBoxLayout()

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(["ID", "User ID", "Action", "Details", "Timestamp"])
        self.logs_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.logs_table)
        self.load_logs()
        layout.addWidget(self.logs_table)

        logs_tab.setLayout(layout)
        self.tab_widget.addTab(logs_tab, "Logs")

    def setup_products_tab(self):
        products_tab = QWidget()
        layout = QVBoxLayout()

        # Buttons for product management
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit Product")
        edit_btn.clicked.connect(self.edit_product)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Product")
        delete_btn.clicked.connect(self.delete_product)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Description", "Image Path", "Category", "Stock"])
        self.products_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.products_table)
        self.products_table.itemDoubleClicked.connect(self.on_product_double_clicked)
        self.load_products()
        layout.addWidget(self.products_table)

        products_tab.setLayout(layout)
        self.tab_widget.addTab(products_tab, "Product")

    def load_users(self):
        users = self.main_app.db.get_all_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            for col in range(8):
                self.users_table.setItem(row, col, QTableWidgetItem(str(user[col])))

    def load_orders(self):
        search_text = self.order_search_input.text().strip()
        cursor = self.main_app.db.conn.cursor()
        if search_text:
            try:
                search_id = int(search_text)
                cursor.execute('SELECT id, user_id, total_amount, status, created_at FROM orders WHERE id = ? ORDER BY created_at DESC', (search_id,))
                orders = cursor.fetchall()
            except ValueError:
                # If not a number, no results
                orders = []
        else:
            cursor.execute('SELECT id, user_id, total_amount, status, created_at FROM orders ORDER BY created_at DESC')
            orders = cursor.fetchall()
        self.orders_table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            order_id = order[0]
            if order_id <= 0:
                continue
            for col in range(5):
                data = order[col]
                if col == 2:  # total_amount
                    self.orders_table.setItem(row, col, QTableWidgetItem(f"{data:,.0f} THB"))
                else:
                    self.orders_table.setItem(row, col, QTableWidgetItem(str(data)))

    def load_logs(self):
        logs = self.main_app.db.get_user_logs()
        self.logs_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            for col, data in enumerate(log):
                self.logs_table.setItem(row, col, QTableWidgetItem(str(data)))

    def on_order_double_clicked(self, item):
        row = item.row()
        order_id_item = self.orders_table.item(row, 0)
        if order_id_item:
            order_id = int(order_id_item.text())
            self.view_order_details(order_id)

    def edit_user_from_table(self, item):
        row = item.row()
        user_id = int(self.users_table.item(row, 0).text())
        self.edit_user(user_id)

    def edit_user(self, user_id):
        # Get current user data
        users = self.main_app.db.get_all_users()
        user_data = next((u for u in users if u[0] == user_id), None)
        if not user_data:
            return

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit User")
        dialog.setModal(True)
        dialog.setStyleSheet(UIUtils.get_gothic_stylesheet())
        layout = QVBoxLayout()

        # Fields
        username_edit = QLineEdit(user_data[1])
        email_edit = QLineEdit(user_data[2])
        password_edit = QLineEdit(user_data[3])
        address_edit = QLineEdit(user_data[4] or "")
        phone_edit = QLineEdit(user_data[5] or "")
        phone_edit.textChanged.connect(lambda text: UIUtils.validate_phone_input(phone_edit, text))
        role_combo = QComboBox()
        role_combo.addItems(["user", "admin"])
        role_combo.setCurrentText(user_data[6])

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(username_edit)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(email_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(password_edit)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(address_edit)
        layout.addWidget(QLabel("Phone Number:"))
        layout.addWidget(phone_edit)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(role_combo)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_user_edit(dialog, user_id, username_edit.text(), email_edit.text(), password_edit.text(), address_edit.text(), phone_edit.text(), role_combo.currentText()))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.resize(500, 600)  # Make dialog bigger by default
        dialog.exec_()

    def save_user_edit(self, dialog, user_id, username, email, password, address, phone_number, role):
        self.main_app.db.update_user_data(user_id, username, email, password, address, phone_number, role)
        self.load_users()
        dialog.accept()

    def view_order_details(self, order_id):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Order Details - Order #{order_id}")
        dialog.setModal(True)
        dialog.setStyleSheet(UIUtils.get_gothic_stylesheet())
        dialog.resize(800, 900)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Get order information
        cursor = self.main_app.db.conn.cursor()
        cursor.execute('SELECT o.id, o.user_id, o.total_amount, o.status, o.created_at FROM orders o WHERE o.id = ?', (order_id,))
        order = cursor.fetchone()
        if not order:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Order Not Found")
            msg.setText(f"Order #{order_id} not found.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        order_id, user_id, total_amount, status, created_at = order

        # Get customer information
        user_profile = self.main_app.db.get_user_profile(user_id)
        if user_profile:
            username, email, address, phone_number, role, user_created_at, _ = user_profile
        else:
            username, email, address, phone_number = "Unknown", "N/A", "N/A", "N/A"

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #000000;
            }
            QScrollBar:vertical {
                background: #333;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #8b0000;
                border-radius: 6px;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Header with order details
        header_label = QLabel(f"""
========================================
          ORDER DETAILS
========================================

Order ID: {order_id}
Order Date: {created_at}
Status: {status}
        """)
        header_label.setFont(QFont("Courier New", 12))
        header_label.setStyleSheet("color: #ff6b6b; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;")
        scroll_layout.addWidget(header_label)

        # Customer information
        customer_label = QLabel(f"""
Customer Information:
Name: {username}
Email: {email}
Phone Number: {phone_number}
Address: {address}
        """)
        customer_label.setFont(QFont("Courier New", 10))
        customer_label.setStyleSheet("background: rgba(255,255,255,0.03); padding: 10px; border-radius: 5px;")
        scroll_layout.addWidget(customer_label)

        # Order details
        details_label = QLabel("Order Details:")
        details_label.setFont(QFont("Arial", 14, QFont.Bold))
        details_label.setStyleSheet("color: #6bff6b; margin-top: 20px;")
        scroll_layout.addWidget(details_label)

        separator = QLabel("----------------------------------------")
        separator.setFont(QFont("Courier New", 10))
        separator.setStyleSheet("color: #666;")
        scroll_layout.addWidget(separator)

        # Order items with images
        items = self.main_app.db.get_order_items(int(order_id))
        for item in items:
            name, quantity, price, total, size = item
            size_str = f" (Size: {size})" if size else ""

            # Get product image
            cursor.execute('SELECT image_path FROM products WHERE id = (SELECT product_id FROM order_items WHERE order_id = ? AND product_id = (SELECT id FROM products WHERE name = ?))', (int(order_id), name))
            image_result = cursor.fetchone()
            image_path = image_result[0] if image_result and image_result[0] else None

            item_frame = QFrame()
            item_frame.setStyleSheet("background: rgba(255,255,255,0.02); border: 1px solid #444; border-radius: 5px; padding: 10px; margin: 5px 0;")
            item_layout = QHBoxLayout()

            # Product image
            image_label = QLabel()
            image_label.setFixedSize(80, 80)
            image_label.setStyleSheet("border: 1px solid #555; border-radius: 3px;")
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("📷")
                    image_label.setAlignment(Qt.AlignCenter)
            else:
                image_label.setText("📷")
                image_label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(image_label)

            # Item details
            item_details = QLabel(f"""
Product: {name}
Quantity: {quantity}{size_str}
Unit Price: {price:,.0f} THB
Subtotal: {total:,.0f} THB
            """)
            item_details.setFont(QFont("Courier New", 10))
            item_layout.addWidget(item_details)

            item_frame.setLayout(item_layout)
            scroll_layout.addWidget(item_frame)

            separator2 = QLabel("----------------------------------------")
            separator2.setFont(QFont("Courier New", 10))
            separator2.setStyleSheet("color: #666;")
            scroll_layout.addWidget(separator2)

        # Subtotal
        subtotal_label = QLabel(f"""
Subtotal: {total_amount * 0.93:,.0f} THB
VAT (7%): {total_amount * 0.07:,.0f} THB
Total Amount: {total_amount:,.0f} THB
        """)
        subtotal_label.setFont(QFont("Courier New", 12, QFont.Bold))
        subtotal_label.setStyleSheet("color: #ff6b6b; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;")
        scroll_layout.addWidget(subtotal_label)

        # Payment proof
        cursor.execute('SELECT image_path FROM payment_proofs WHERE order_id = ?', (int(order_id),))
        proof = cursor.fetchone()
        if proof and proof[0] and os.path.exists(proof[0]):
            proof_label = QLabel("Payment Proof:")
            proof_label.setFont(QFont("Arial", 12, QFont.Bold))
            proof_label.setStyleSheet("color: #6bff6b; margin-top: 20px;")
            scroll_layout.addWidget(proof_label)

            # View Payment Proof button
            proof_btn = QPushButton("View Payment Proof")
            proof_btn.setStyleSheet("""
                QPushButton {
                    background: #8b0000;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: white;
                }
                QPushButton:hover {
                    background: #a00000;
                }
            """)
            proof_btn.clicked.connect(lambda: self.view_payment_proof(order_id))
            scroll_layout.addWidget(proof_btn)

            # Receipt buttons layout
            receipt_btn_layout = QHBoxLayout()

            # View Receipt button
            receipt_btn = QPushButton("View Receipt")
            receipt_btn.setStyleSheet("""
                QPushButton {
                    background: #8b0000;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: white;
                }
                QPushButton:hover {
                    background: #a00000;
                }
            """)
            receipt_btn.clicked.connect(lambda: self.view_receipt(order_id))
            receipt_btn_layout.addWidget(receipt_btn)

            # Download PDF button
            download_pdf_btn = QPushButton("Save PDF")
            download_pdf_btn.setStyleSheet("""
                QPushButton {
                    background: #333;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    color: white;
                }
                QPushButton:hover {
                    background: #555;
                }
            """)
            download_pdf_btn.clicked.connect(lambda: self.download_receipt_pdf(order_id))
            receipt_btn_layout.addWidget(download_pdf_btn)

            scroll_layout.addLayout(receipt_btn_layout)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #8b0000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        dialog.setLayout(layout)
        dialog.exec_()

    def view_receipt(self, order_id):
        """View the PDF receipt directly"""
        import os
        pdf_path = os.path.join(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\payment_proofs", f"receipt_{order_id}.pdf")
        if os.path.exists(pdf_path):
            # Open PDF directly with default system viewer
            try:
                os.startfile(pdf_path)
            except Exception as e:
                msg = UIUtils.create_themed_message_box(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Could not open PDF: {str(e)}")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
        else:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Receipt Not Found")
            msg.setText(f"Receipt for order #{order_id} not found.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def view_payment_proof(self, order_id):
        """View payment proof image"""
        UIUtils.show_payment_proof_dialog(self, self.main_app.db, order_id)

    def download_receipt_pdf(self, order_id):
        """Download a copy of the existing PDF receipt"""
        try:
            pdf_path = os.path.join(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\payment_proofs", f"receipt_{order_id}.pdf")

            if not os.path.exists(pdf_path):
                msg = UIUtils.create_themed_message_box(self)
                msg.setWindowTitle("Error")
                msg.setText("PDF receipt not found.")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return

            from PyQt5.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Receipt PDF", f"receipt_{order_id}.pdf", "PDF Files (*.pdf)")
            if file_path:
                try:
                    # Use binary mode for file copy to avoid encoding issues
                    with open(pdf_path, 'rb') as src_file:
                        with open(file_path, 'wb') as dst_file:
                            dst_file.write(src_file.read())

                    msg = UIUtils.create_themed_message_box(self)
                    msg.setWindowTitle("Success")
                    msg.setText(f"PDF receipt saved to {file_path}")
                    msg.setIcon(QMessageBox.Information)
                    msg.exec_()
                except Exception as copy_error:
                    msg = UIUtils.create_themed_message_box(self)
                    msg.setWindowTitle("Error")
                    msg.setText(f"Failed to save PDF: {str(copy_error)}")
                    msg.setIcon(QMessageBox.Warning)
                    msg.exec_()

        except Exception as e:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to save PDF: {str(e)}")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def load_products(self):
        products = self.main_app.db.get_products()
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col in range(7):
                if col == 2:  # Price column
                    self.products_table.setItem(row, col, QTableWidgetItem(f"{product[col]:,.0f} THB"))
                else:
                    self.products_table.setItem(row, col, QTableWidgetItem(str(product[col])))

    def add_product(self):
        dialog = ProductDialog(self.main_app, None)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()

    def edit_product(self):
        current_row = self.products_table.currentRow()
        if current_row < 0:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("No Selection")
            msg.setText("Please select a product to edit.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        product_id = int(self.products_table.item(current_row, 0).text())
        products = self.main_app.db.get_products()
        product = next((p for p in products if p[0] == product_id), None)
        if product:
            dialog = ProductDialog(self.main_app, product)
            if dialog.exec_() == QDialog.Accepted:
                self.load_products()

    def delete_product(self):
        current_row = self.products_table.currentRow()
        if current_row < 0:
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("No Selection")
            msg.setText("Please select a product to delete.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        product_id = int(self.products_table.item(current_row, 0).text())
        product_name = self.products_table.item(current_row, 1).text()

        msg = UIUtils.create_themed_message_box(self)
        msg.setWindowTitle("Confirm Delete")
        msg.setText(f"Are you sure you want to delete '{product_name}'?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            self.main_app.db.delete_product(product_id)
            self.load_products()

    def on_product_double_clicked(self, item):
        self.edit_product()

    def setup_trading_summary_tab(self):
        trading_tab = QWidget()
        layout = QVBoxLayout()

        # Header with refresh button
        header_layout = QHBoxLayout()
        title = QLabel("Trading Summary")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_trading_summary)
        refresh_btn.setStyleSheet("""
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
        """)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Create tab widget for different periods
        self.trading_tabs = QTabWidget()
        self.trading_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none; solid #333;
                background: #000000;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #000000;
                color: #ffffff;
                padding: 10px 25px;
                margin: 0px;
                border: 1px solid #444;
                border-bottom: none;
                font-weight: bold;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #222222;
                color: #ffffff;
                border-bottom: 2px solid #8b0000;
            }
            QTabBar::tab:hover {
                background: #333333;
            }
        """)

        # Daily summary tab
        self.setup_daily_summary_tab()

        # Monthly summary tab
        self.setup_monthly_summary_tab()

        # Yearly summary tab
        self.setup_yearly_summary_tab()

        layout.addWidget(self.trading_tabs)
        trading_tab.setLayout(layout)
        self.tab_widget.addTab(trading_tab, "Selling Summary")
        self.refresh_trading_summary()

    def setup_daily_summary_tab(self):
        daily_tab = QWidget()
        layout = QVBoxLayout()

        # Date selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))

        self.trading_daily_day_combo = QComboBox()
        self.trading_daily_day_combo.addItems([f"{i:02d}" for i in range(1, 32)])
        current_day = QDate.currentDate().day()
        self.trading_daily_day_combo.setCurrentText(f"{current_day:02d}")
        date_layout.addWidget(self.trading_daily_day_combo)

        date_layout.addWidget(QLabel("Month:"))
        self.trading_daily_month_combo = QComboBox()
        self.trading_daily_month_combo.addItems(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
        current_month = QDate.currentDate().month()
        self.trading_daily_month_combo.setCurrentIndex(current_month - 1)  # 0-based index
        date_layout.addWidget(self.trading_daily_month_combo)

        date_layout.addWidget(QLabel("Year:"))
        self.trading_daily_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.trading_daily_year_combo.addItem(str(year))
        self.trading_daily_year_combo.setCurrentText(str(current_year))
        date_layout.addWidget(self.trading_daily_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Daily products table
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(3)
        self.daily_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.daily_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.daily_table)
        self.daily_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.daily_table.setColumnWidth(0, 300)
        self.daily_table.setColumnWidth(1, 150)

        layout.addWidget(self.daily_table)

        # Footer with totals
        daily_footer = QFrame()
        daily_footer.setStyleSheet("background: #1a1a1a; border: 1px solid #8b0000; border-radius: 10px; padding: 15px;")
        daily_footer_layout = QVBoxLayout()

        # Subtotal
        self.daily_subtotal_label = QLabel("Subtotal: 0.00 ฿ THB")
        self.daily_subtotal_label.setFont(QFont("Arial", 14))
        self.daily_subtotal_label.setStyleSheet("color: #ffffff;")
        daily_footer_layout.addWidget(self.daily_subtotal_label)

        # VAT
        self.daily_vat_label = QLabel("VAT (7%): 0.00 ฿ THB")
        self.daily_vat_label.setFont(QFont("Arial", 14))
        self.daily_vat_label.setStyleSheet("color: #ff6b6b;")
        daily_footer_layout.addWidget(self.daily_vat_label)

        # Total
        self.daily_total_label = QLabel("Total: 0.00 ฿ THB")
        self.daily_total_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.daily_total_label.setStyleSheet("color: #ff6b6b; margin-top: 10px;")
        daily_footer_layout.addWidget(self.daily_total_label)

        daily_footer.setLayout(daily_footer_layout)
        layout.addWidget(daily_footer)

        daily_tab.setLayout(layout)
        self.trading_tabs.addTab(daily_tab, "Daily")

    def setup_monthly_summary_tab(self):
        monthly_tab = QWidget()
        layout = QVBoxLayout()

        # Month and year selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Month:"))

        self.trading_monthly_month_combo = QComboBox()
        self.trading_monthly_month_combo.addItems(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
        current_month = QDate.currentDate().month()
        self.trading_monthly_month_combo.setCurrentIndex(current_month - 1)  # 0-based index
        date_layout.addWidget(self.trading_monthly_month_combo)

        date_layout.addWidget(QLabel("Year:"))
        self.trading_monthly_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.trading_monthly_year_combo.addItem(str(year))
        self.trading_monthly_year_combo.setCurrentText(str(current_year))
        date_layout.addWidget(self.trading_monthly_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Monthly products table
        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(3)
        self.monthly_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.monthly_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.monthly_table)
        self.monthly_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.monthly_table.setColumnWidth(0, 300)
        self.monthly_table.setColumnWidth(1, 150)

        layout.addWidget(self.monthly_table)

        # Footer with totals
        monthly_footer = QFrame()
        monthly_footer.setStyleSheet("background: #1a1a1a; border: 1px solid #8b0000; border-radius: 10px; padding: 15px;")
        monthly_footer_layout = QVBoxLayout()

        # Subtotal
        self.monthly_subtotal_label = QLabel("Subtotal: 0.00 ฿ THB")
        self.monthly_subtotal_label.setFont(QFont("Arial", 14))
        self.monthly_subtotal_label.setStyleSheet("color: #ffffff;")
        monthly_footer_layout.addWidget(self.monthly_subtotal_label)

        # VAT
        self.monthly_vat_label = QLabel("VAT (7%): 0.00 ฿ THB")
        self.monthly_vat_label.setFont(QFont("Arial", 14))
        self.monthly_vat_label.setStyleSheet("color: #ff6b6b;")
        monthly_footer_layout.addWidget(self.monthly_vat_label)

        # Total
        self.monthly_total_label = QLabel("Total: 0.00 ฿ THB")
        self.monthly_total_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.monthly_total_label.setStyleSheet("color: #ff6b6b; margin-top: 10px;")
        monthly_footer_layout.addWidget(self.monthly_total_label)

        monthly_footer.setLayout(monthly_footer_layout)
        layout.addWidget(monthly_footer)

        monthly_tab.setLayout(layout)
        self.trading_tabs.addTab(monthly_tab, "Monthly")

    def setup_yearly_summary_tab(self):
        yearly_tab = QWidget()
        layout = QVBoxLayout()

        # Year selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Year:"))
        self.trading_yearly_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 10, current_year + 1):
            self.trading_yearly_year_combo.addItem(str(year))
        self.trading_yearly_year_combo.setCurrentText(str(current_year))

        date_layout.addWidget(self.trading_yearly_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Yearly products table
        self.yearly_table = QTableWidget()
        self.yearly_table.setColumnCount(3)
        self.yearly_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.yearly_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.yearly_table)
        self.yearly_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.yearly_table.setColumnWidth(0, 300)
        self.yearly_table.setColumnWidth(1, 150)

        layout.addWidget(self.yearly_table)

        # Footer with totals
        yearly_footer = QFrame()
        yearly_footer.setStyleSheet("background: #1a1a1a; border: 1px solid #8b0000; border-radius: 10px; padding: 15px;")
        yearly_footer_layout = QVBoxLayout()

        # Subtotal
        self.yearly_subtotal_label = QLabel("Subtotal: 0.00 ฿ THB")
        self.yearly_subtotal_label.setFont(QFont("Arial", 14))
        self.yearly_subtotal_label.setStyleSheet("color: #ffffff;")
        yearly_footer_layout.addWidget(self.yearly_subtotal_label)

        # VAT
        self.yearly_vat_label = QLabel("VAT (7%): 0.00 ฿ THB")
        self.yearly_vat_label.setFont(QFont("Arial", 14))
        self.yearly_vat_label.setStyleSheet("color: #ff6b6b;")
        yearly_footer_layout.addWidget(self.yearly_vat_label)

        # Total
        self.yearly_total_label = QLabel("Total: 0.00 ฿ THB")
        self.yearly_total_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.yearly_total_label.setStyleSheet("color: #ff6b6b; margin-top: 10px;")
        yearly_footer_layout.addWidget(self.yearly_total_label)

        yearly_footer.setLayout(yearly_footer_layout)
        layout.addWidget(yearly_footer)

        yearly_tab.setLayout(layout)
        self.trading_tabs.addTab(yearly_tab, "Yearly")

    def refresh_trading_summary(self):
        # Load daily products
        selected_year = int(self.trading_daily_year_combo.currentText())
        selected_month = int(self.trading_daily_month_combo.currentText())
        selected_day = int(self.trading_daily_day_combo.currentText())
        selected_date = f"{selected_year:04d}-{selected_month:02d}-{selected_day:02d}"
        daily_data = self.main_app.db.get_all_daily_products(selected_date)
        self.daily_table.setRowCount(len(daily_data))
        for row, (name, quantity, revenue) in enumerate(daily_data):
            self.daily_table.setItem(row, 0, QTableWidgetItem(name))
            self.daily_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))

        # Calculate daily totals
        daily_subtotal = sum(revenue for _, _, revenue in daily_data)
        daily_vat = daily_subtotal * 0.07
        daily_total = daily_subtotal + daily_vat
        self.daily_subtotal_label.setText(f"Subtotal: {daily_subtotal:,.0f} ฿ THB")
        self.daily_vat_label.setText(f"VAT (7%): {daily_vat:,.0f} ฿ THB")
        self.daily_total_label.setText(f"Total: {daily_total:,.0f} ฿ THB")

        # Load monthly products
        selected_year = int(self.trading_monthly_year_combo.currentText())
        selected_month = int(self.trading_monthly_month_combo.currentText())
        monthly_data = self.main_app.db.get_all_monthly_products(selected_year, selected_month)
        self.monthly_table.setRowCount(len(monthly_data))
        for row, (name, quantity, revenue) in enumerate(monthly_data):
            self.monthly_table.setItem(row, 0, QTableWidgetItem(name))
            self.monthly_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.monthly_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))

        # Calculate monthly totals
        monthly_subtotal = sum(revenue for _, _, revenue in monthly_data)
        monthly_vat = monthly_subtotal * 0.07
        monthly_total = monthly_subtotal + monthly_vat
        self.monthly_subtotal_label.setText(f"Subtotal: {monthly_subtotal:,.0f} ฿ THB")
        self.monthly_vat_label.setText(f"VAT (7%): {monthly_vat:,.0f} ฿ THB")
        self.monthly_total_label.setText(f"Total: {monthly_total:,.0f} ฿ THB")

        # Load yearly products
        selected_year = int(self.trading_yearly_year_combo.currentText())
        yearly_data = self.main_app.db.get_all_yearly_products(selected_year)
        self.yearly_table.setRowCount(len(yearly_data))
        for row, (name, quantity, revenue) in enumerate(yearly_data):
            self.yearly_table.setItem(row, 0, QTableWidgetItem(name))
            self.yearly_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.yearly_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))

        # Calculate yearly totals
        yearly_subtotal = sum(revenue for _, _, revenue in yearly_data)
        yearly_vat = yearly_subtotal * 0.07
        yearly_total = yearly_subtotal + yearly_vat
        self.yearly_subtotal_label.setText(f"Subtotal: {yearly_subtotal:,.0f} ฿ THB")
        self.yearly_vat_label.setText(f"VAT (7%): {yearly_vat:,.0f} ฿ THB")
        self.yearly_total_label.setText(f"Total: {yearly_total:,.0f} ฿ THB")

    def setup_product_stats_tab(self):
        product_stats_tab = QWidget()
        layout = QVBoxLayout()

        # Header with refresh button
        header_layout = QHBoxLayout()
        title = QLabel("Top Selling Products")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 10px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_product_stats)
        refresh_btn.setStyleSheet("""
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
        """)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Create tab widget for different periods
        self.product_stats_tabs = QTabWidget()
        self.product_stats_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none; solid #333;
                background: #000000;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #000000;
                color: #ffffff;
                padding: 10px 25px;
                margin: 0px;
                border: 1px solid #444;
                border-bottom: none;
                font-weight: bold;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #222222;
                color: #ffffff;
                border-bottom: 2px solid #8b0000;
            }
            QTabBar::tab:hover {
                background: #333333;
            }
        """)

        # Daily products tab
        self.setup_daily_products_tab()

        # Monthly products tab
        self.setup_monthly_products_tab()

        # Yearly products tab
        self.setup_yearly_products_tab()

        layout.addWidget(self.product_stats_tabs)
        product_stats_tab.setLayout(layout)
        self.tab_widget.addTab(product_stats_tab, "Top 5 of selling")
        self.refresh_product_stats()

    def setup_daily_products_tab(self):
        daily_tab = QWidget()
        layout = QVBoxLayout()

        # Date selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Day:"))

        self.daily_day_combo = QComboBox()
        self.daily_day_combo.addItems([f"{i:02d}" for i in range(1, 32)])
        current_day = QDate.currentDate().day()
        self.daily_day_combo.setCurrentText(f"{current_day:02d}")
        date_layout.addWidget(self.daily_day_combo)

        date_layout.addWidget(QLabel("Month:"))
        self.daily_month_combo = QComboBox()
        self.daily_month_combo.addItems(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
        current_month = QDate.currentDate().month()
        self.daily_month_combo.setCurrentIndex(current_month - 1)  # 0-based index
        date_layout.addWidget(self.daily_month_combo)

        date_layout.addWidget(QLabel("Year:"))
        self.daily_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.daily_year_combo.addItem(str(year))
        self.daily_year_combo.setCurrentText(str(current_year))
        date_layout.addWidget(self.daily_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Daily products table
        self.daily_products_table = QTableWidget()
        self.daily_products_table.setColumnCount(3)
        self.daily_products_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.daily_products_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.daily_products_table)
        self.daily_products_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.daily_products_table.setColumnWidth(0, 300)
        self.daily_products_table.setColumnWidth(1, 150)

        layout.addWidget(self.daily_products_table)
        daily_tab.setLayout(layout)
        self.product_stats_tabs.addTab(daily_tab, "Daily")

    def setup_monthly_products_tab(self):
        monthly_tab = QWidget()
        layout = QVBoxLayout()

        # Month and year selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Month:"))

        self.monthly_month_combo = QComboBox()
        self.monthly_month_combo.addItems(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
        current_month = QDate.currentDate().month()
        self.monthly_month_combo.setCurrentIndex(current_month - 1)  # 0-based index
        date_layout.addWidget(self.monthly_month_combo)

        date_layout.addWidget(QLabel("Year:"))
        self.monthly_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.monthly_year_combo.addItem(str(year))
        self.monthly_year_combo.setCurrentText(str(current_year))
        date_layout.addWidget(self.monthly_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Monthly products table
        self.monthly_products_table = QTableWidget()
        self.monthly_products_table.setColumnCount(3)
        self.monthly_products_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.monthly_products_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.monthly_products_table)
        self.monthly_products_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.monthly_products_table.setColumnWidth(0, 300)
        self.monthly_products_table.setColumnWidth(1, 150)

        layout.addWidget(self.monthly_products_table)
        monthly_tab.setLayout(layout)
        self.product_stats_tabs.addTab(monthly_tab, "Monthly")

    def setup_yearly_products_tab(self):
        yearly_tab = QWidget()
        layout = QVBoxLayout()

        # Year selector
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Year:"))
        self.yearly_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 10, current_year + 1):
            self.yearly_year_combo.addItem(str(year))
        self.yearly_year_combo.setCurrentText(str(current_year))
        date_layout.addWidget(self.yearly_year_combo)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Yearly products table
        self.yearly_products_table = QTableWidget()
        self.yearly_products_table.setColumnCount(3)
        self.yearly_products_table.setHorizontalHeaderLabels(["Product Name", "Total Quantity", "Total Sales (฿)"])
        self.yearly_products_table.verticalHeader().setVisible(False)

        UIUtils.apply_table_styling(self.yearly_products_table)
        self.yearly_products_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        self.yearly_products_table.setColumnWidth(0, 300)
        self.yearly_products_table.setColumnWidth(1, 150)

        layout.addWidget(self.yearly_products_table)
        yearly_tab.setLayout(layout)
        self.product_stats_tabs.addTab(yearly_tab, "Yearly")

    def refresh_product_stats(self):
        # Load daily products
        selected_year = int(self.daily_year_combo.currentText())
        selected_month = int(self.daily_month_combo.currentText())
        selected_day = int(self.daily_day_combo.currentText())
        selected_date = f"{selected_year:04d}-{selected_month:02d}-{selected_day:02d}"
        daily_data = self.main_app.db.get_top_daily_products(selected_date)
        self.daily_products_table.setRowCount(len(daily_data))
        for row, (name, quantity, revenue) in enumerate(daily_data):
            self.daily_products_table.setItem(row, 0, QTableWidgetItem(name))
            self.daily_products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.daily_products_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))

        # Load monthly products
        selected_year = int(self.monthly_year_combo.currentText())
        selected_month = int(self.monthly_month_combo.currentText())
        monthly_data = self.main_app.db.get_top_monthly_products(selected_year, selected_month)
        self.monthly_products_table.setRowCount(len(monthly_data))
        for row, (name, quantity, revenue) in enumerate(monthly_data):
            self.monthly_products_table.setItem(row, 0, QTableWidgetItem(name))
            self.monthly_products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.monthly_products_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))

        # Load yearly products
        selected_year = int(self.yearly_year_combo.currentText())
        yearly_data = self.main_app.db.get_top_yearly_products(selected_year)
        self.yearly_products_table.setRowCount(len(yearly_data))
        for row, (name, quantity, revenue) in enumerate(yearly_data):
            self.yearly_products_table.setItem(row, 0, QTableWidgetItem(name))
            self.yearly_products_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.yearly_products_table.setItem(row, 2, QTableWidgetItem(f"{revenue:,.0f}"))