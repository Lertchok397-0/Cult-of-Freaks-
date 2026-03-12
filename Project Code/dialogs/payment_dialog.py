import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from utils import UIUtils
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PaymentDialog(QDialog):
    def __init__(self, main_app, cart_items, total_amount, subtotal, vat_amount, order_id):
        super().__init__()
        self.main_app = main_app
        self.cart_items = cart_items
        self.total_amount = total_amount
        self.subtotal = subtotal
        self.vat_amount = vat_amount
        self.order_id = order_id  # Will be None initially, set when order is created
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Payment")
        self.setModal(True)
        self.setStyleSheet(UIUtils.get_gothic_stylesheet())

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Complete Your Payment")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtotal
        subtotal_label = QLabel(f"Subtotal: {self.subtotal:,.0f} ฿ THB")
        subtotal_label.setFont(QFont("Arial", 14))
        subtotal_label.setAlignment(Qt.AlignCenter)
        subtotal_label.setStyleSheet("color: #ffffff; margin: 5px 0;")
        layout.addWidget(subtotal_label)

        # VAT
        vat_label = QLabel(f"VAT (7%): {self.vat_amount:,.0f} ฿ THB")
        vat_label.setFont(QFont("Arial", 14))
        vat_label.setAlignment(Qt.AlignCenter)
        vat_label.setStyleSheet("color: #ff6b6b; margin: 5px 0;")
        layout.addWidget(vat_label)

        # Total amount
        total_label = QLabel(f"Total Amount: {self.total_amount:,.0f} ฿ THB")
        total_label.setFont(QFont("Arial", 16, QFont.Bold))
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #ff6b6b; margin: 10px 0;")
        layout.addWidget(total_label)

        # QR Code
        qr_label = QLabel("Scan QR Code to Pay:")
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)

        qr_display = QLabel("QR Code loading...")
        qr_display.setAlignment(Qt.AlignCenter)
        qr_display.setStyleSheet("color: #999;")
        layout.addWidget(qr_display)

        # Load QR in a try block
        try:
            qr_path = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\QR2.jpg"
            if os.path.exists(qr_path):
                qr_pixmap = QPixmap(qr_path)
                if not qr_pixmap.isNull():
                    qr_display.setPixmap(qr_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    qr_display.setAlignment(Qt.AlignCenter)
                else:
                    qr_display.setText("QR Code invalid")
            else:
                qr_display.setText("QR Code not found")
        except Exception as e:
            qr_display.setText(f"Error loading QR: {str(e)}")

        # PromptPay number
        pp_label = QLabel("Or use PromptPay Number: 0984903235")
        pp_label.setFont(QFont("Arial", 14, QFont.Bold))
        pp_label.setAlignment(Qt.AlignCenter)
        pp_label.setStyleSheet("color: #ff6b6b; margin: 10px 0;")
        layout.addWidget(pp_label)

        # Upload proof
        upload_btn = QPushButton("Upload Payment Proof")
        upload_btn.clicked.connect(self.upload_proof)
        layout.addWidget(upload_btn)

        # Cancel
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

    def upload_proof(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Payment Proof Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # First, create the order from cart
            success, message, order_id = self.main_app.db.create_order_from_cart(self.main_app.current_user[0])
            if not success:
                msg = UIUtils.create_themed_message_box(self)
                msg.setWindowTitle("Order Creation Failed")
                msg.setText(f"Failed to create order: {message}")
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return

            self.order_id = order_id  # Set the order_id now that order is created

            # Copy to payment_proofs with order_id as filename
            proof_dir = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\payment_proofs"
            os.makedirs(proof_dir, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            filename = f"{self.order_id}{ext}"
            dest_path = os.path.join(proof_dir, filename)
            import shutil
            shutil.copy(file_path, dest_path)

            # Save to db and update order status to completed
            self.main_app.db.save_payment_proof(self.order_id, dest_path)

            # Log the action
            self.main_app.db.log_user_action(self.main_app.current_user[0], "payment_uploaded", f"Payment proof uploaded for order #{self.order_id}")

            # Generate PDF receipt automatically
            self.generate_pdf_receipt(self.order_id, self.cart_items, self.subtotal, self.vat_amount, self.total_amount)

            self.main_app.db.conn.commit()

            msg = UIUtils.create_themed_message_box(self)
            msg.setWindowTitle("Payment Submitted")
            msg.setText(f"Your payment proof has been submitted. Your Order Number is {self.order_id}. Order will be processed.")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            self.accept()

    def generate_pdf_receipt(self, order_id, cart_items, subtotal, vat_amount, total_amount):
        """Generate PDF receipt automatically when order is completed"""
        try:
            # Register Thai font (you'll need to provide the path to a Thai font file)
            # For now, we'll use a fallback approach with UTF-8 encoding
            try:
                # Try to register a Thai font if available
                thai_font_path = r"C:\Windows\Fonts\tahoma.ttf"  # Common Thai font
                if os.path.exists(thai_font_path):
                    pdfmetrics.registerFont(TTFont('ThaiFont', thai_font_path))
                    thai_font_name = 'ThaiFont'
                else:
                    thai_font_name = 'Helvetica'  # Fallback
            except:
                thai_font_name = 'Helvetica'  # Fallback

            # Get user profile
            user_profile = self.main_app.db.get_user_profile(self.main_app.current_user[0])
            if user_profile:
                username, email, address, phone_number, role, user_created_at, _ = user_profile
            else:
                username, email, address, phone_number = "Unknown", "N/A", "N/A", "N/A"

            # Get order date
            cursor = self.main_app.db.conn.cursor()
            cursor.execute('SELECT created_at FROM orders WHERE id = ?', (order_id,))
            order_date = cursor.fetchone()[0]

            # Create PDF path
            receipt_dir = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\payment_proofs"
            os.makedirs(receipt_dir, exist_ok=True)
            pdf_path = os.path.join(receipt_dir, f"receipt_{order_id}.pdf")

            doc = SimpleDocTemplate(pdf_path, pagesize=letter, encoding='utf-8')
            styles = getSampleStyleSheet()

            # Custom styles with Thai font support
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1,  # Center
                textColor=colors.HexColor('#8b0000'),
                fontName=thai_font_name,
                encoding='utf-8'
            )

            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                fontName=thai_font_name,
                encoding='utf-8'
            )

            # Content
            content = []

            # Title
            content.append(Paragraph("ORDER RECEIPT", title_style))
            content.append(Spacer(1, 12))

            # Order info
            content.append(Paragraph(f"<b>Order ID:</b> #{order_id}", normal_style))
            content.append(Paragraph(f"<b>Order Date:</b> {order_date}", normal_style))
            content.append(Paragraph(f"<b>Status:</b> COMPLETED", normal_style))
            content.append(Spacer(1, 12))

            # Customer info
            content.append(Paragraph("<b>Customer Information:</b>", normal_style))
            content.append(Paragraph(f"Name: {username}", normal_style))
            content.append(Paragraph(f"Email: {email}", normal_style))
            content.append(Paragraph(f"Phone: {phone_number}", normal_style))
            content.append(Paragraph(f"Address: {address}", normal_style))
            content.append(Spacer(1, 12))

            # Items table
            content.append(Paragraph("<b>Order Details:</b>", normal_style))

            # Table data
            table_data = [['Product', 'Qty', 'Price', 'Size', 'Total']]
            for item in cart_items:
                name, quantity, price, total, size = item[2], item[4], item[3], item[6], item[8]
                size_str = size if size else "N/A"
                table_data.append([name, str(quantity), f"{price:,.0f} THB", size_str, f"{total:,.0f} THB"])

            # Add totals
            table_data.append(['', '', '', 'Subtotal:', f"{subtotal:,.0f} THB"])
            table_data.append(['', '', '', 'VAT (7%):', f"{vat_amount:,.0f} THB"])
            table_data.append(['', '', '', 'Total:', f"{total_amount:,.0f} THB"])

            # Create table
            table = Table(table_data, colWidths=[2.5*inch, 0.5*inch, 1*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b0000')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), thai_font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -3), (-1, -1), thai_font_name),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -4), thai_font_name),  # Product names and data
            ]))

            content.append(table)
            content.append(Spacer(1, 24))

            # Footer
            content.append(Paragraph("Thank you for your purchase!", normal_style))
            content.append(Paragraph("Cult of FREAKS - Gothic Accessories", normal_style))

            # Build PDF with UTF-8 encoding
            doc.build(content)

        except Exception as e:
            print(f"Error generating PDF receipt: {e}")