from db_connection import *
from datetime import datetime

def add_stock(product_id, amount, notes=""):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Update product quantity
            update_query = "UPDATE products SET quantity = quantity + %s WHERE product_id = %s"
            cursor.execute(update_query, (amount, product_id))
            
            # Log the inventory change
            log_query = """
            INSERT INTO inventory_log 
            (product_id, change_type, amount, notes)
            VALUES (%s, 'add', %s, %s)
            """
            cursor.execute(log_query, (product_id, amount, notes))
            
            conn.commit()
            print(f"Added {amount} units to product ID {product_id}")
            return True
        except Error as e:
            print(f"Error adding stock: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False

def remove_stock(product_id, amount, notes=""):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # First check current stock
            cursor.execute("SELECT quantity FROM products WHERE product_id = %s", (product_id,))
            current_stock = cursor.fetchone()[0]
            
            if current_stock < amount:
                print("Error: Not enough stock to remove")
                return False
                
            # Update product quantity
            update_query = "UPDATE products SET quantity = quantity - %s WHERE product_id = %s"
            cursor.execute(update_query, (amount, product_id))
            
            # Log the inventory change
            log_query = """
            INSERT INTO inventory_log 
            (product_id, change_type, amount, notes)
            VALUES (%s, 'remove', %s, %s)
            """
            cursor.execute(log_query, (product_id, amount, notes))
            
            conn.commit()
            print(f"Removed {amount} units from product ID {product_id}")
            return True
        except Error as e:
            print(f"Error removing stock: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False

def record_sale(product_id, quantity, sale_price):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # First check current stock
            cursor.execute("SELECT quantity FROM products WHERE product_id = %s", (product_id,))
            current_stock = cursor.fetchone()[0]
            
            if current_stock < quantity:
                print("Error: Not enough stock for this sale")
                return False
                
            # Update product quantity
            update_query = "UPDATE products SET quantity = quantity - %s WHERE product_id = %s"
            cursor.execute(update_query, (quantity, product_id))
            
            # Record the sale
            sale_query = """
            INSERT INTO sales 
            (product_id, quantity, sale_price)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sale_query, (product_id, quantity, sale_price))
            
            # Log the inventory change
            log_query = """
            INSERT INTO inventory_log 
            (product_id, change_type, amount, notes)
            VALUES (%s, 'remove', %s, 'Sale recorded')
            """
            cursor.execute(log_query, (product_id, quantity))
            
            conn.commit()
            print(f"Recorded sale of {quantity} units of product ID {product_id}")
            return True
        except Error as e:
            print(f"Error recording sale: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False

def get_inventory_status():
    conn = create_db_connection()
    inventory = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT p.*, 
                   (p.quantity * p.cost_price) AS total_cost_value,
                   (p.quantity * p.selling_price) AS total_sale_value,
                   CASE 
                       WHEN p.quantity <= p.min_stock_level THEN 'Low Stock'
                       ELSE 'In Stock'
                   END AS stock_status
            FROM products p
            ORDER BY product_id, p.name
            """
            cursor.execute(query)
            inventory = cursor.fetchall()
        except Error as e:
            print(f"Error fetching inventory status: {e}")
        finally:
            close_db_connection(conn)
    return inventory