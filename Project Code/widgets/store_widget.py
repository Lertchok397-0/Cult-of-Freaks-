from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QScrollArea, QGridLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from utils import UIUtils
from dialogs.product_details_dialog import ProductDetailsDialog
from dialogs.contact_dialog import ContactDialog

class StoreWidget(QWidget):
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
            QFrame {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 5px;
            }
            QScrollArea {
                border: none;
                background: #000000;
            }
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar (red navigation)
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b0000, stop:1 #660000);
                color: white;
            }
            QPushButton {
                background: transparent;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QLabel {
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo area with just image in sidebar
        sidebar_logo_pixmap = QPixmap(r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\icon.png")
        sidebar_logo_label = QLabel()
        if not sidebar_logo_pixmap.isNull():
            scaled_sidebar_logo = sidebar_logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sidebar_logo_label.setPixmap(scaled_sidebar_logo)
        else:
            sidebar_logo_label.setText("🔺")
            sidebar_logo_label.setStyleSheet("font-size: 32px; color: white;")
        sidebar_logo_label.setAlignment(Qt.AlignCenter)
        sidebar_logo_label.setStyleSheet("background: transparent; padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.2);")
        sidebar_layout.addWidget(sidebar_logo_label)

        # User info
        user_info = QLabel(f"Welcome, {self.main_app.current_user[1]}")
        user_info.setStyleSheet("padding: 15px 20px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.2);")
        sidebar_layout.addWidget(user_info)

        # Navigation buttons
        nav_buttons = [
            ("Chokers", self.show_chokers),
            ("Cuffs", self.show_cuffs),
            ("Other", self.show_other),
            ("Shop All", self.show_all),
            ("My Orders", self.show_orders),
            ("My Profile", self.show_profile)
        ]

        # Check if admin
        profile = self.main_app.db.get_user_profile(self.main_app.current_user[0])
        if profile and profile[4] == 'admin':
            nav_buttons.append(("Admin Panel", self.show_admin))

        nav_buttons.append(("About Me", self.show_contact))

        for btn_text, btn_func in nav_buttons:
            nav_btn = QPushButton(btn_text)
            nav_btn.clicked.connect(btn_func)
            sidebar_layout.addWidget(nav_btn)

        sidebar_layout.addStretch()

        # Logout button at bottom
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #4a0000;
                margin: 20px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #600000;
            }
        """)
        sidebar_layout.addWidget(logout_btn)

        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)

        # Main content area
        content_area = QWidget()
        content_area.setStyleSheet("background: #000000;")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Header with search and cart
        header = QHBoxLayout()

        # Title
        self.page_title = QLabel("Gothic Collection - Dark Accessories")
        self.page_title.setFont(QFont("Arial", 24, QFont.Bold))
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        self.page_title.setStyleSheet("color: white; background: transparent; margin-bottom: 20px;")
        header.addWidget(self.page_title)

        header.addStretch()

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setFixedWidth(200)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: white;
                font-size: 14px;
            }
        """)
        header.addWidget(self.search_input)

        # Search button
        search_btn = QPushButton("Search")
        search_btn.setFixedSize(80, 40)
        search_btn.clicked.connect(self.search_products)
        search_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        header.addWidget(search_btn)

        store_btn = QPushButton("All Items")
        store_btn.setFixedSize(80, 40)
        store_btn.clicked.connect(self.show_all)
        store_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        header.addWidget(store_btn)

        cart_btn = QPushButton("Cart")
        cart_btn.setFixedSize(60, 40)
        cart_btn.clicked.connect(self.show_cart)
        cart_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: #555;
            }
        """)
        header.addWidget(cart_btn)

        # Update cart count
        self.update_cart_count()

        content_layout.addLayout(header)

        # Products scroll area
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

        self.scroll_widget = QWidget()
        self.products_layout = QGridLayout()
        self.products_layout.setSpacing(20)

        # Load all products initially
        self.current_category = "all"
        self.search_query = ""
        self.load_products()

        self.scroll_widget.setLayout(self.products_layout)
        scroll.setWidget(self.scroll_widget)
        content_layout.addWidget(scroll)

        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area)

        self.setLayout(main_layout)

    def load_products(self):
        # Clear existing products
        for i in reversed(range(self.products_layout.count())):
            self.products_layout.itemAt(i).widget().setParent(None)

        # Get products from database
        products = self.main_app.db.get_products()

        # Filter by category if needed
        if self.current_category != "all":
            products = [p for p in products if p[5] == self.current_category]
        else:
            # Sort products: cuffs first, then chokers, then others
            category_order = {'cuffs': 0, 'chokers': 1, 'other': 2}
            products.sort(key=lambda p: category_order.get(p[5], 3))

        # Filter by search query
        if self.search_query:
            products = [p for p in products if self.search_query in p[1].lower()]

        # Create product cards in grid
        row = 0
        col = 0
        for product in products:
            product_card = self.create_product_card(product)
            self.products_layout.addWidget(product_card, row, col)
            col += 1
            if col >= 3:  # 3 products per row
                col = 0
                row += 1

    def create_product_card(self, product):
        card = QFrame()
        card.setFixedSize(280, 400)
        card.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 10px;
            }
            QFrame:hover {
                border: 2px solid #8b0000;
                background: #222;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Product image
        image_label = QLabel()
        image_label.setFixedSize(240, 180)
        image_label.setStyleSheet("border: 1px solid #555; border-radius: 5px; background: #333;")
        image_label.setAlignment(Qt.AlignCenter)
        if product[4]:  # image_path
            pixmap = QPixmap(product[4])
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(240, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("Image not found")
        else:
            image_label.setText("📸")
        layout.addWidget(image_label)

        # Product name
        name_label = QLabel(product[1])
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: white; margin: 10px 0 5px 0;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Price in Thai Baht style
        price_label = QLabel(f"{product[2]:,.0f} ฿ THB")
        price_label.setFont(QFont("Arial", 16, QFont.Bold))
        price_label.setStyleSheet("color: #ff6b6b; margin-bottom: 5px;")
        layout.addWidget(price_label)

        # Stock info
        stock_quantity = product[6] if len(product) > 6 else 0
        stock_label = QLabel(f"Stock: {stock_quantity}")
        stock_label.setStyleSheet("color: #ff6b6b;" if stock_quantity < 5 else "color: #6bff6b;")
        layout.addWidget(stock_label)

        # View Details button
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(lambda: self.view_product_details(product))
        view_btn.setStyleSheet("""
            QPushButton {
                background: #8b0000;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #a00000;
            }
        """)
        layout.addWidget(view_btn)

        card.setLayout(layout)
        return card

    def show_chokers(self):
        self.current_category = "chokers"
        self.page_title.setText("Chokers Collection")
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        self.search_query = ""
        self.search_input.clear()
        self.load_products()

    def show_cuffs(self):
        self.current_category = "cuffs"
        self.page_title.setText("Cuffs & Bracelets")
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        self.search_query = ""
        self.search_input.clear()
        self.load_products()

    def show_other(self):
        self.current_category = "other"
        self.page_title.setText("Other Accessories")
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        self.search_query = ""
        self.search_input.clear()
        self.load_products()

    def show_all(self):
        self.current_category = "all"
        self.page_title.setText("Gothic Collection - Dark Accessories")
        self.page_title.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        self.search_query = ""
        self.search_input.clear()
        self.load_products()

    def search_products(self):
        self.search_query = self.search_input.text().lower()
        self.load_products()

    def view_product_details(self, product):
        dialog = ProductDetailsDialog(self.main_app, product)
        dialog.exec_()
        self.update_cart_count()

    def show_cart(self):
        self.main_app.show_cart()

    def update_cart_count(self):
        # This method could update a cart badge counter if needed
        try:
            cart_items = self.main_app.db.get_cart_items(self.main_app.current_user[0])
            # Could add a badge showing number of items here
            pass
        except Exception as e:
            print(f"Error updating cart count: {e}")

    def show_orders(self):
        self.main_app.show_orders()

    def show_profile(self):
        self.main_app.show_profile()

    def show_admin(self):
        self.main_app.show_admin()

    def show_contact(self):
        dialog = ContactDialog()
        dialog.exec_()

    def logout(self):
        self.main_app.current_user = None
        self.main_app.show_login()