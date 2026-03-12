import sqlite3
import os
import hashlib
import shutil
from datetime import datetime, timezone, timedelta

class DatabaseManager:
    def __init__(self):
        self.db_path = r"C:\Users\MSI\Desktop\project store\project-20251110T153441Z-1-001\project\Database\backup\Newest Backup\gothic_store_demo4test.db"
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                address TEXT,
                phone_number TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN phone_number TEXT')
        except sqlite3.OperationalError:
            pass  

        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT')
        except sqlite3.OperationalError:
            pass  

        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
            if cursor.fetchone()[0] == 0:
                
                cursor.execute('INSERT INTO users (username, email, password, address, phone_number, role) VALUES (?, ?, ?, ?, ?, ?)',
                               ('admin', 'admin@gothicstore.com', 'admin123', 'Store Address', '0864739813', 'admin'))

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                category TEXT,
                stock_quantity INTEGER DEFAULT 10
            )
        ''')

        
        cursor.execute('DROP TABLE IF EXISTS cart')
        cursor.execute('''
            CREATE TABLE cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                size TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                size TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            
            cursor.execute('INSERT INTO users (username, email, password, address, phone_number, role) VALUES (?, ?, ?, ?, ?, ?)',
                           ('admin', 'admin@gothicstore.com', 'admin123', 'Store Address', '0864739813', 'admin'))

        
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ('Resurrection Choker - Black Crucifix', 195.00, 'Gothic black leather choker with crucifix pendant and spikes', '', 'chokers', 5),
                ('Polaris Choker', 98.00, 'Spiked collar with hanging chains and O-ring', '', 'chokers', 8),
                ('Martingale Choker', 78.00, 'Chain choker with O-ring and leather details', '', 'chokers', 12),
                ('Thorn Crown Choker', 120.00, 'Barbed wire inspired gothic choker with thorns', '', 'chokers', 6),
                ('Vampire Bite Choker', 89.00, 'Red velvet choker with fang details', '', 'chokers', 10),
                ('Pentagram Collar', 145.00, 'Wide leather collar with pentagram centerpiece', '', 'chokers', 4),
                ('Leather Bondage Cuffs', 156.00, 'Heavy duty leather wrist cuffs with D-rings', '', 'cuffs', 7),
                ('Spiked Bracelet Set', 67.00, 'Pair of leather spiked bracelets', '', 'cuffs', 15),
                ('Chain Link Cuffs', 98.00, 'Metal chain cuffs with leather lining', '', 'cuffs', 9),
                ('Gothic Arm Guards', 234.00, 'Medieval style leather arm guards with buckles', '', 'cuffs', 3),
                ('Bat Wing Earrings', 45.00, 'Sterling silver bat wing gothic earrings', '', 'other', 20),
                ('Skull Ring Collection', 78.00, 'Set of 3 detailed skull rings in silver', '', 'other', 12),
                ('Coffin Bag', 167.00, 'Leather coffin-shaped handbag with chains', '', 'other', 5),
                ('Raven Feather Hair Clips', 34.00, 'Set of black feather hair accessories', '', 'other', 25),
                ('Gothic Cross Necklace', 123.00, 'Large inverted cross pendant on chain', '', 'other', 8),
                ('Blood Rose Brooch', 56.00, 'Dark red rose brooch with silver thorns', '', 'other', 14)
            ]
            cursor.executemany('INSERT INTO products (name, price, description, image_path, category, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)', sample_products)

        self.conn.commit()

    def register_user(self, username, email, password, address, phone_number):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password, address, phone_number) VALUES (?, ?, ?, ?, ?)',
                           (username, email, password, address, phone_number))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_user_address(self, user_id, address):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET address = ? WHERE id = ?', (address, user_id))
        self.conn.commit()

    def update_user_data(self, user_id, username, email, password, address, phone_number, role, profile_picture=None):
        cursor = self.conn.cursor()
        if password:  
            if profile_picture is not None:
                cursor.execute('UPDATE users SET username = ?, email = ?, password = ?, address = ?, phone_number = ?, role = ?, profile_picture = ? WHERE id = ?',
                               (username, email, password, address, phone_number, role, profile_picture, user_id))
            else:
                cursor.execute('UPDATE users SET username = ?, email = ?, password = ?, address = ?, phone_number = ?, role = ? WHERE id = ?',
                               (username, email, password, address, phone_number, role, user_id))
        else:  
            if profile_picture is not None:
                cursor.execute('UPDATE users SET username = ?, email = ?, address = ?, phone_number = ?, role = ?, profile_picture = ? WHERE id = ?',
                               (username, email, address, phone_number, role, profile_picture, user_id))
            else:
                cursor.execute('UPDATE users SET username = ?, email = ?, address = ?, phone_number = ?, role = ? WHERE id = ?',
                               (username, email, address, phone_number, role, user_id))
        self.conn.commit()

    def get_user_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, email, address, phone_number, role, created_at, profile_picture FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

    def log_user_action(self, user_id, action, details=""):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO user_logs (user_id, action, details) VALUES (?, ?, ?)', (user_id, action, details))
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username, email, password, address, phone_number, role, created_at FROM users')
        return cursor.fetchall()

    def get_user_logs(self, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute('SELECT * FROM user_logs WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
        else:
            cursor.execute('SELECT * FROM user_logs ORDER BY timestamp DESC')
        return cursor.fetchall()

    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?',
                       (username, password))
        return cursor.fetchone()

    def verify_user_for_password_reset(self, email, phone_number):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE email = ? AND phone_number = ?',
                       (email, phone_number))
        return cursor.fetchone()

    def update_user_password(self, user_id, new_password):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        self.conn.commit()

    def get_products(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products')
        return cursor.fetchall()

    def add_product(self, name, price, description, category, stock_quantity, image_path):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO products (name, price, description, category, stock_quantity, image_path) VALUES (?, ?, ?, ?, ?, ?)',
                       (name, price, description, category, stock_quantity, image_path))
        self.conn.commit()
        return cursor.lastrowid

    def update_product(self, product_id, name, price, description, category, stock_quantity, image_path):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE products SET name = ?, price = ?, description = ?, category = ?, stock_quantity = ?, image_path = ? WHERE id = ?',
                       (name, price, description, category, stock_quantity, image_path, product_id))
        self.conn.commit()

    def delete_product(self, product_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.conn.commit()

    def add_to_cart(self, user_id, product_id, quantity=1, size=""):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ? AND size = ?', (user_id, product_id, size))
        existing = cursor.fetchone()

        if existing:
            
            new_quantity = existing[1] + quantity
            cursor.execute('UPDATE cart SET quantity = ? WHERE id = ?', (new_quantity, existing[0]))
        else:
            
            cursor.execute('INSERT INTO cart (user_id, product_id, quantity, size) VALUES (?, ?, ?, ?)', (user_id, product_id, quantity, size))

        self.conn.commit()
        return True

    def get_cart_items(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.id, p.id, p.name, p.price, c.quantity, p.stock_quantity,
                   (p.price * c.quantity) as total_price, p.image_path, c.size
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        ''', (user_id,))
        return cursor.fetchall()

    def remove_from_cart(self, cart_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        self.conn.commit()

    def update_cart_quantity(self, cart_id, quantity):
        cursor = self.conn.cursor()
        if quantity <= 0:
            cursor.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        else:
            cursor.execute('UPDATE cart SET quantity = ? WHERE id = ?', (quantity, cart_id))
        self.conn.commit()

    def clear_cart(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def validate_checkout(self, user_id):
        cursor = self.conn.cursor()

        
        cart_items = self.get_cart_items(user_id)
        if not cart_items:
            return False, "Cart is empty", None, None, None

        
        for item in cart_items:
            if item[4] > item[5]:  
                return False, f"Insufficient stock for {item[2]}", None, None, None

        
        subtotal = sum(item[6] for item in cart_items)

        
        vat_rate = 0.07
        vat_amount = subtotal * vat_rate

        
        total_amount = subtotal + vat_amount

        return True, "Checkout validated successfully", total_amount, subtotal, vat_amount

    def create_order_from_cart(self, user_id):
        cursor = self.conn.cursor()

        
        cart_items = self.get_cart_items(user_id)
        if not cart_items:
            return False, "Cart is empty", None

        
        total_amount = sum(item[6] for item in cart_items)

        try:
            
            bangkok_tz = timezone(timedelta(hours=7))
            current_time = datetime.now(bangkok_tz).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO orders (user_id, total_amount, created_at) VALUES (?, ?, ?)', (user_id, total_amount, current_time))
            order_id = cursor.lastrowid

            
            for item in cart_items:
                cart_id, product_id, name, price, quantity, stock, total_price, image_path, size = item

                
                cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price, size) VALUES (?, ?, ?, ?, ?)',
                              (order_id, product_id, quantity, price, size))

                
                new_stock = stock - quantity
                cursor.execute('UPDATE products SET stock_quantity = ? WHERE id = ?', (new_stock, product_id))

            
            self.clear_cart(user_id)

            self.conn.commit()
            return True, f"Order #{order_id} created successfully!", order_id

        except Exception as e:
            self.conn.rollback()
            return False, f"Order creation failed: {str(e)}", None

    def get_user_orders(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT o.id, o.total_amount, o.status, o.created_at
            FROM orders o
            WHERE o.user_id = ? AND o.status = 'completed'
            ORDER BY o.created_at DESC
        ''', (user_id,))
        return cursor.fetchall()

    def get_order_items(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.name, oi.quantity, oi.price, (oi.quantity * oi.price) as total, oi.size
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        return cursor.fetchall()

    def save_payment_proof(self, order_id, image_path):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO payment_proofs (order_id, image_path) VALUES (?, ?)', (order_id, image_path))
        
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', ('completed', order_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_daily_sales_summary(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''')
        return cursor.fetchall()

    def get_monthly_sales_summary(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed'
            GROUP BY strftime('%Y-%m', created_at)
            ORDER BY month DESC
        ''')
        return cursor.fetchall()

    def get_yearly_sales_summary(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y', created_at) as year, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed'
            GROUP BY strftime('%Y', created_at)
            ORDER BY year DESC
        ''')
        return cursor.fetchall()

    def get_daily_sales_summary_for_date(self, date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed' AND DATE(created_at) = ?
            GROUP BY DATE(created_at)
        ''', (date,))
        return cursor.fetchone()

    def get_monthly_sales_summary_for_period(self, year, month):
        cursor = self.conn.cursor()
        month_str = f"{year:04d}-{month:02d}"
        cursor.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed' AND strftime('%Y-%m', created_at) = ?
            GROUP BY strftime('%Y-%m', created_at)
        ''', (month_str,))
        return cursor.fetchone()

    def get_yearly_sales_summary_for_year(self, year):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y', created_at) as year, COUNT(*) as orders_count, SUM(total_amount) as total_sales
            FROM orders
            WHERE status = 'completed' AND strftime('%Y', created_at) = ?
            GROUP BY strftime('%Y', created_at)
        ''', (str(year),))
        return cursor.fetchone()

    def get_top_daily_products(self, date=None):
        cursor = self.conn.cursor()
        if date is None:
            date_filter = "DATE('now', 'localtime')"
        else:
            date_filter = f"'{date}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE DATE(o.created_at) = {date_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
            LIMIT 5
        ''')
        return cursor.fetchall()

    def get_all_daily_products(self, date=None):
        cursor = self.conn.cursor()
        if date is None:
            date_filter = "DATE('now', 'localtime')"
        else:
            date_filter = f"'{date}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE DATE(o.created_at) = {date_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
        ''')
        return cursor.fetchall()

    def get_top_monthly_products(self, year=None, month=None):
        cursor = self.conn.cursor()
        if year is None or month is None:
            month_filter = "strftime('%Y-%m', 'now', 'localtime')"
        else:
            month_str = f"{year:04d}-{month:02d}"
            month_filter = f"'{month_str}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE strftime('%Y-%m', o.created_at) = {month_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
            LIMIT 5
        ''')
        return cursor.fetchall()

    def get_top_yearly_products(self, year=None):
        cursor = self.conn.cursor()
        if year is None:
            year_filter = "strftime('%Y', 'now', 'localtime')"
        else:
            year_filter = f"'{year:04d}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE strftime('%Y', o.created_at) = {year_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
            LIMIT 5
        ''')
        return cursor.fetchall()

    def get_all_monthly_products(self, year=None, month=None):
        cursor = self.conn.cursor()
        if year is None or month is None:
            month_filter = "strftime('%Y-%m', 'now', 'localtime')"
        else:
            month_str = f"{year:04d}-{month:02d}"
            month_filter = f"'{month_str}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE strftime('%Y-%m', o.created_at) = {month_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
        ''')
        return cursor.fetchall()

    def get_all_yearly_products(self, year=None):
        cursor = self.conn.cursor()
        if year is None:
            year_filter = "strftime('%Y', 'now', 'localtime')"
        else:
            year_filter = f"'{year:04d}'"
        cursor.execute(f'''
            SELECT p.name, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE strftime('%Y', o.created_at) = {year_filter}
            AND o.status = 'completed'
            GROUP BY oi.product_id, p.name
            ORDER BY total_quantity DESC
        ''')
        return cursor.fetchall()