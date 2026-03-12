import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QAbstractButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils import UIUtils

class OrdersWidget(QWidget):
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
                background: transparent;
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

        title = QLabel("Order History")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAttribute(Qt.WA_TranslucentBackground)
        title.setStyleSheet("color: white; background: transparent; margin-bottom: 20px;")
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

        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Date", "Status", "Total", "View Receipt"])
        self.orders_table.setStyleSheet("""
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
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setStyleSheet(self.orders_table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #222;
            }
        """)

        # Hide the corner button
        corner_button = self.orders_table.findChild(QAbstractButton)
        if corner_button:
            corner_button.setVisible(False)

        # Set row height
        self.orders_table.verticalHeader().setDefaultSectionSize(60)

        # Set column widths
        self.orders_table.setColumnWidth(0, 100)  # Order ID
        self.orders_table.setColumnWidth(1, 120)  # Date
        self.orders_table.setColumnWidth(2, 120)  # Status
        self.orders_table.setColumnWidth(3, 120)  # Total
        self.orders_table.setColumnWidth(4, 120)  # View Receipt

        self.load_orders()
        layout.addWidget(self.orders_table)

        self.setLayout(layout)

    def load_orders(self):
        # Get orders from database
        orders = self.main_app.db.get_user_orders(self.main_app.current_user[0])

        if not orders:
            self.orders_table.setRowCount(1)
            empty_item = QTableWidgetItem("No orders found")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setForeground(Qt.white)
            self.orders_table.setItem(0, 0, empty_item)
            self.orders_table.setSpan(0, 0, 1, 5)  # Span across all columns
            return

        self.orders_table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            order_id, total_amount, status, created_at = order

            # Order ID column
            order_id_item = QTableWidgetItem(f"#{order_id}")
            order_id_item.setTextAlignment(Qt.AlignCenter)
            order_id_item.setFont(QFont("Arial", 12, QFont.Bold))
            self.orders_table.setItem(row, 0, order_id_item)

            # Date column
            date_item = QTableWidgetItem(created_at.split(' ')[0])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.orders_table.setItem(row, 1, date_item)

            # Status column
            status_item = QTableWidgetItem(status.upper())
            status_item.setTextAlignment(Qt.AlignCenter)
            if status == "completed":
                status_item.setForeground(Qt.green)
            else:
                status_item.setForeground(Qt.red)
            self.orders_table.setItem(row, 2, status_item)

            # Total column
            total_item = QTableWidgetItem(f"{total_amount:,.0f} ฿")
            total_item.setTextAlignment(Qt.AlignCenter)
            total_item.setFont(QFont("Arial", 12, QFont.Bold))
            total_item.setForeground(Qt.red)
            self.orders_table.setItem(row, 3, total_item)

            # View Receipt column - main button with download icon
            if status == "completed":
                # Create a widget to hold button and download icon
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(2, 2, 2, 2)
                btn_layout.setSpacing(2)

                # View Receipt button (main button)
                receipt_btn = QPushButton("View Receipt")
                receipt_btn.setStyleSheet("""
                    QPushButton {
                        background: #8b0000;
                        border: none;
                        border-radius: 5px;
                        font-size: 11px;
                        color: white;
                        font-weight: bold;
                        padding: 8px 12px;
                    }
                    QPushButton:hover {
                        background: #a00000;
                    }
                """)
                receipt_btn.clicked.connect(lambda checked, oid=order_id: self.view_receipt(oid))
                btn_layout.addWidget(receipt_btn)

                # Download button
                download_btn = QPushButton("Save")
                download_btn.setFixedSize(80, 25)
                download_btn.setToolTip("Save PDF Receipt")
                download_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #333;
                        border: none;
                        border-radius: 5px;
                        font-size: 11px;
                        color: white;
                        font-weight: bold;
                        padding: 8px 12px;
                    }
                    QPushButton:hover {
                        background: #555;
                    }
                """)
                download_btn.clicked.connect(lambda checked, oid=order_id: self.download_receipt_pdf(oid))
                btn_layout.addWidget(download_btn)

                btn_widget.setLayout(btn_layout)
                self.orders_table.setCellWidget(row, 4, btn_widget)
            else:
                pending_item = QTableWidgetItem("N/A")
                pending_item.setTextAlignment(Qt.AlignCenter)
                pending_item.setForeground(Qt.gray)
                self.orders_table.setItem(row, 4, pending_item)

    def view_receipt(self, order_id):
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