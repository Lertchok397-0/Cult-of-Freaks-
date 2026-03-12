import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget, QMessageBox
from database import DatabaseManager
from widgets.login_widget import LoginWidget
from widgets.register_widget import RegisterWidget
from widgets.store_widget import StoreWidget
from widgets.cart_widget import CartWidget
from widgets.orders_widget import OrdersWidget
from widgets.profile_widget import ProfileWidget
from widgets.admin_widget import AdminWidget

class GothicStoreApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_user = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("cult of FREAKS")
        self.setGeometry(200, 100, 1280, 720)
        self.setStyleSheet("background: #000000;")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.login_page = LoginWidget(self)
        self.register_page = RegisterWidget(self)
        self.store_page = None 
        self.cart_page = None  
        self.orders_page = None 
        self.profile_page = None  
        self.admin_page = None  

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)

        self.show_login()

    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_page)

    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_page)

    def show_store(self):
        
        if self.store_page is None:
            self.store_page = StoreWidget(self)
            self.stacked_widget.addWidget(self.store_page)
        else:
            
            self.stacked_widget.removeWidget(self.store_page)
            self.store_page = StoreWidget(self)
            self.stacked_widget.addWidget(self.store_page)

        self.stacked_widget.setCurrentWidget(self.store_page)

    def show_cart(self):
        
        if self.cart_page is None:
            self.cart_page = CartWidget(self)
            self.stacked_widget.addWidget(self.cart_page)
        else:
            
            self.stacked_widget.removeWidget(self.cart_page)
            self.cart_page = CartWidget(self)
            self.stacked_widget.addWidget(self.cart_page)

        self.stacked_widget.setCurrentWidget(self.cart_page)

    def show_orders(self):
        
        if self.orders_page is None:
            self.orders_page = OrdersWidget(self)
            self.stacked_widget.addWidget(self.orders_page)
        else:
            
            self.stacked_widget.removeWidget(self.orders_page)
            self.orders_page = OrdersWidget(self)
            self.stacked_widget.addWidget(self.orders_page)

        self.stacked_widget.setCurrentWidget(self.orders_page)

    def show_profile(self):
        
        if self.profile_page is None:
            self.profile_page = ProfileWidget(self)
            self.stacked_widget.addWidget(self.profile_page)
        else:
            
            self.stacked_widget.removeWidget(self.profile_page)
            self.profile_page = ProfileWidget(self)
            self.stacked_widget.addWidget(self.profile_page)

        self.stacked_widget.setCurrentWidget(self.profile_page)

    def show_admin(self):
        
        profile = self.db.get_user_profile(self.current_user[0])
        if profile and profile[4] == 'admin':
            
            if self.admin_page is None:
                self.admin_page = AdminWidget(self)
                self.stacked_widget.addWidget(self.admin_page)
            else:
                
                self.stacked_widget.removeWidget(self.admin_page)
                self.admin_page = AdminWidget(self)
                self.stacked_widget.addWidget(self.admin_page)

            self.stacked_widget.setCurrentWidget(self.admin_page)
        else:
            from utils import UIUtils
            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Access Denied")
            msg.setText("You don't have admin privileges")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GothicStoreApp()
    window.show()
    sys.exit(app.exec_())