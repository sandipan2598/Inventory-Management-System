from db_connection import *
from datetime import date

def add_product(name, pack, category, quantity, unit, cost_price, selling_price, min_stock_level, supplier):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO products 
            (name, pack, category, quantity, unit, cost_price, selling_price, min_stock_level, supplier, date_added)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, pack, category, quantity, unit, cost_price, 
                                 selling_price, min_stock_level, supplier, date.today()))
            conn.commit()
            print("Product added successfully!")
            return True
        except Error as e:
            print(f"Error adding product: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False

def get_all_products():
    conn = create_db_connection()
    products = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products ORDER BY name")
            products = cursor.fetchall()
        except Error as e:
            print(f"Error fetching products: {e}")
        finally:
            close_db_connection(conn)
    return products

def update_product(product_id, name, pack, category, unit, cost_price, selling_price, min_stock_level, supplier):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE products 
            SET name=%s, pack=%s, category=%s, unit=%s, cost_price=%s, 
                selling_price=%s, min_stock_level=%s, supplier=%s 
            WHERE product_id=%s
            """
            cursor.execute(query, (name, pack, category, unit, cost_price, 
                                 selling_price, min_stock_level, supplier, product_id))
            conn.commit()
            print("Product updated successfully!")
            return True
        except Error as e:
            print(f"Error updating product: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False

def delete_product(product_id):
    conn = create_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
            conn.commit()
            print("Product deleted successfully!")
            return True
        except Error as e:
            print(f"Error deleting product: {e}")
            return False
        finally:
            close_db_connection(conn)
    return False