from db_connection import *
from datetime import datetime

def get_sales_report(start_date=None, end_date=None):
    conn = create_db_connection()
    sales = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Convert string dates to datetime objects for validation
            if start_date and end_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError as e:
                    print(f"Invalid date format: {e}")
                    return sales
                
                # Add time to end_date to include the entire day
                end_date_with_time = f"{end_date} 23:59:59"
                
                query = """
                SELECT s.*, p.name, p.Pack, p.unit 
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                WHERE s.sale_date BETWEEN %s AND %s
                ORDER BY s.sale_date
                """
                cursor.execute(query, (start_date, end_date_with_time))
            else:
                query = """
                SELECT s.*, p.name, p.Pack, p.unit 
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                ORDER BY s.sale_date
                """
                cursor.execute(query)
                
            sales = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching sales report: {e}")
        finally:
            close_db_connection(conn)
    return sales

def get_inventory_changes_report(product_id=None, start_date=None, end_date=None):
    conn = create_db_connection()
    changes = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            base_query = """
            SELECT il.*, p.name, p.Pack, p.unit 
            FROM inventory_log il
            JOIN products p ON il.product_id = p.product_id
            """
            
            conditions = []
            params = []
            
            if product_id:
                conditions.append("il.product_id = %s")
                params.append(product_id)
                
            if start_date and end_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    end_date_with_time = f"{end_date} 23:59:59"
                    
                    conditions.append("il.log_date BETWEEN %s AND %s")
                    params.extend([start_date, end_date_with_time])
                except ValueError as e:
                    print(f"Invalid date format: {e}")
                    return changes
                
            if conditions:
                query = base_query + " WHERE " + " AND ".join(conditions) + " ORDER BY il.log_date ASC"
            else:
                query = base_query + " ORDER BY il.log_date ASC"
                
            cursor.execute(query, tuple(params))
            changes = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching inventory changes: {e}")
        finally:
            close_db_connection(conn)
    return changes

def get_sales_by_date(start_date, end_date):
    conn = create_db_connection()
    sales_data = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Convert string dates to datetime objects
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                end_date_with_time = f"{end_date} 23:59:59"
            except ValueError as e:
                print(f"Invalid date format: {e}")
                return sales_data
            
            query = """
            SELECT 
                DATE(sale_date) AS sale_day,
                SUM(quantity * sale_price) AS total_sales,
                COUNT(*) AS transaction_count
            FROM sales
            WHERE sale_date BETWEEN %s AND %s
            GROUP BY sale_day
            ORDER BY sale_day ASC
            """
            cursor.execute(query, (start_date, end_date_with_time))
            
            # Convert date objects to strings for consistency
            sales_data = []
            for row in cursor.fetchall():
                row['sale_day'] = row['sale_day'].strftime('%Y-%m-%d')  # Convert date to string
                sales_data.append(row)
                
        except Exception as e:
            print(f"Error fetching sales by date: {e}")
        finally:
            close_db_connection(conn)
    return sales_data

def get_low_stock_items():
    conn = create_db_connection()
    items = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT * FROM products 
            WHERE quantity <= min_stock_level
            ORDER BY (quantity/min_stock_level)
            """
            cursor.execute(query)
            items = cursor.fetchall()
        except Error as e:
            print(f"Error fetching low stock items: {e}")
        finally:
            close_db_connection(conn)
    return items