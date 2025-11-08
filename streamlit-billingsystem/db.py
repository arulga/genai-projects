import sqlite3

def init_db():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()

    # Users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Products
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price REAL
        )
    ''')

    # Bills
    c.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            customer_name TEXT,
            total REAL,
            gst REAL,
            grand_total REAL,
            date TEXT
        )
    ''')

    # Bill Items
    c.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            product TEXT,
            quantity INTEGER,
            price REAL,
            total REAL
        )
    ''')

    conn.commit()
    conn.close()

# ---------- User ----------
def register_user(username, password):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def check_login(username, password):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()
    conn.close()
    return data

# ---------- Product ----------
def add_product(name, price):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO products (name, price) VALUES (?,?)", (name, price))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_products():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT name, price FROM products")
    data = c.fetchall()
    conn.close()
    return data

def delete_product(name):
    conn = sqlite3.connect("billing.db")
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE name=?", (name,))
    conn.commit()
    conn.close()

def update_product(old_name, new_name, new_price):
    conn = sqlite3.connect("billing.db")
    c = conn.cursor()
    c.execute("UPDATE products SET name=?, price=? WHERE name=?", (new_name, new_price, old_name))
    conn.commit()
    conn.close()
    
# ---------- Billing ----------
def save_bill(username, customer, items, total, gst, grand_total, date):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("INSERT INTO bills (username, customer_name, total, gst, grand_total, date) VALUES (?,?,?,?,?,?)",
              (username, customer, total, gst, grand_total, date))
    bill_id = c.lastrowid

    for i in items:
        c.execute("INSERT INTO bill_items (bill_id, product, quantity, price, total) VALUES (?,?,?,?,?)",
                  (bill_id, i['Product'], i['Quantity'], i['Unit Price'], i['Total']))

    conn.commit()
    conn.close()
    return bill_id

def get_bills():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT id, username, customer_name, total, gst, grand_total, date FROM bills ORDER BY date DESC")
    data = c.fetchall()
    conn.close()
    return data

def get_bill_items(bill_id):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute("SELECT product, quantity, price, total FROM bill_items WHERE bill_id=?", (bill_id,))
    data = c.fetchall()
    conn.close()
    return data
