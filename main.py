import tkinter as tk
from tkinter import ttk, messagebox
from product_operations import get_all_products, add_product, update_product, delete_product
from inventory_operations import add_stock, remove_stock, record_sale, get_inventory_status
from reports import get_sales_report, get_inventory_changes_report, get_low_stock_items, get_sales_by_date
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import db_connection
from db_connection import *

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1200x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.header_frame, text="Desktop Inventory Management System", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Navigation buttons
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(self.nav_frame, text="Inventory", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Add Product", command=self.show_add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Add Stock", command=self.show_add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Record Sale", command=self.show_record_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.nav_frame, text="Reports", command=self.show_reports).pack(side=tk.LEFT, padx=5)
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.update_status("Ready")
        
        # Show inventory by default
        self.show_inventory()
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.after(5000, lambda: self.status_var.set("Ready") if message != "Ready" else None)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_inventory(self):
        self.clear_content()
        self.update_status("Loading inventory...")
        
        # Get inventory data
        inventory = get_inventory_status()
        low_stock = get_low_stock_items()
        
        # Create frames
        top_frame = ttk.Frame(self.content_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_frame, text="Current Inventory Status", style='Header.TLabel').pack(side=tk.LEFT)
        
        if low_stock:
            ttk.Label(top_frame, text=f"Warning: {len(low_stock)} items below minimum stock!", 
                     foreground='red').pack(side=tk.LEFT, padx=10)
        
        # Inventory Treeview
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create treeview
        columns = ("ID", "Name", "pack", "Category", "Quantity", "Unit", "Cost", "Price", 
                  "Min Stock", "Total Cost", "Total Value", "Status")
        self.inventory_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                          yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scroll.config(command=self.inventory_tree.yview)
        x_scroll.config(command=self.inventory_tree.xview)
        
        # Format columns
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=80, anchor=tk.CENTER)
        
        # Insert data
        for item in inventory:
            status = "Low Stock" if item['quantity'] <= item['min_stock_level'] else "In Stock"
            values = (
                item['product_id'],
                item['name'],
                item['pack'],
                item['category'],
                f"{item['quantity']:.2f}",
                item['unit'],
                f"${item['cost_price']:.2f}",
                f"${item['selling_price']:.2f}",
                f"{item['min_stock_level']:.2f}",
                f"${item['total_cost_value']:.2f}",
                f"${item['total_sale_value']:.2f}",
                status
            )
            tag = 'low' if status == "Low Stock" else ''
            self.inventory_tree.insert('', tk.END, values=values, tags=(tag,))
        
        # Configure tags
        self.inventory_tree.tag_configure('low', background='#ffdddd')
        
        # Add buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Refresh", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Details", command=self.view_product_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Product", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        
        self.update_status("Inventory loaded successfully")
    
    def view_product_details(self):
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        item = self.inventory_tree.item(selected)
        product_id = item['values'][0]
        
        # Get product details from database
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
                product = cursor.fetchone()
                
                # Get inventory changes
                cursor.execute("""
                SELECT * FROM inventory_log 
                WHERE product_id = %s 
                ORDER BY log_date DESC 
                LIMIT 10
                """, (product_id,))
                changes = cursor.fetchall()
                
                # Show details in a new window
                self.show_product_details_window(product, changes)
                
            except Error as e:
                messagebox.showerror("Error", f"Failed to get product details: {e}")
            finally:
                close_db_connection(conn)
    
    def show_product_details_window(self, product, changes):
        details_win = tk.Toplevel(self.root)
        details_win.title(f"Product Details - {product['name']} ({product['pack']})")
        details_win.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(details_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product info frame
        info_frame = ttk.LabelFrame(main_frame, text="Product Information")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create labels for product info
        info_labels = [
            ("ID:", product['product_id']),
            ("Name:", product['name']),
            ("pack:", product['pack']),
            ("Category:", product['category']),
            ("Current Quantity:", f"{product['quantity']} {product['unit']}"),
            ("Cost Price:", f"${product['cost_price']:.2f}"),
            ("Selling Price:", f"${product['selling_price']:.2f}"),
            ("Minimum Stock Level:", f"{product['min_stock_level']} {product['unit']}"),
            ("Supplier:", product['supplier']),
            ("Date Added:", product['date_added'].strftime('%Y-%m-%d')),
            ("Last Updated:", product['last_updated'].strftime('%Y-%m-%d %H:%M:%S'))
        ]
        
        for i, (label, value) in enumerate(info_labels):
            ttk.Label(info_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=value).grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Inventory changes frame
        changes_frame = ttk.LabelFrame(main_frame, text="Recent Inventory Changes")
        changes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for changes
        columns = ("Date", "Type", "Amount", "Notes")
        changes_tree = ttk.Treeview(changes_frame, columns=columns, show="headings")
        changes_tree.pack(fill=tk.BOTH, expand=True)
        
        for col in columns:
            changes_tree.heading(col, text=col)
            changes_tree.column(col, width=150, anchor=tk.CENTER)
        
        for change in changes:
            values = (
                change['log_date'].strftime('%Y-%m-%d %H:%M'),
                change['change_type'].capitalize(),
                f"{change['amount']} {product['unit']}",
                change['notes'] if change['notes'] else "-"
            )
            changes_tree.insert('', tk.END, values=values)
    
    def edit_product(self):
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        item = self.inventory_tree.item(selected)
        product_id = item['values'][0]
        
        # Get product details from database
        conn = create_db_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
                product = cursor.fetchone()
                
                # Show edit form
                self.show_product_form(product)
                
            except Error as e:
                messagebox.showerror("Error", f"Failed to get product details: {e}")
            finally:
                close_db_connection(conn)
    
    def delete_product(self):
        selected = self.inventory_tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a product first")
            return
        
        item = self.inventory_tree.item(selected)
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete '{product_name}'? This cannot be undone."):
            if delete_product(product_id):
                messagebox.showinfo("Success", "Product deleted successfully")
                self.show_inventory()
            else:
                messagebox.showerror("Error", "Failed to delete product")
    
    def show_add_product(self):
        self.clear_content()
        self.update_status("Adding new product...")
        self.show_product_form()
    
    def show_product_form(self, product=None):
        self.clear_content()
        
        is_edit = product is not None
        title = "Edit Product" if is_edit else "Add New Product"
        
        # Main form frame
        form_frame = ttk.LabelFrame(self.content_frame, text=title)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form fields
        fields = [
            ("Name:", "name", "entry"),
            ("pack:", "pack", "combobox",["45ml*25","45ml*36","50ml*25","60ml*25","60ml*30","65ml*25","70ml*20","70ml*25","70ml*27","80ml*12","80ml*20","90ml*20","90ml*24","100ml*12","105ml*16","110ml*12","110ml*16","125ml*10","500ml*2","700ml*1","700ml*2","750ml*2","4000ml*1"]),
            ("Category:", "category", "combobox", ["CUPS", "STICKS", "CONES", "MAGNUM", "BLOCKS","TUBS","GALLONS"]),
            ("Initial Quantity:", "quantity", "entry"),
            ("Unit:", "unit", "combobox", ["liters","units", "packs"]),
            ("Cost Price ($):", "cost_price", "entry"),
            ("Selling Price ($):", "selling_price", "entry"),
            ("Minimum Stock Level:", "min_stock_level", "entry"),
            ("Supplier:", "supplier", "entry")
        ]
        
        self.form_vars = {}
        for i, (label, field, field_type, *options) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.E, padx=5, pady=5)
            
            if field_type == "entry":
                var = tk.StringVar()
                entry = ttk.Entry(form_frame, textvariable=var)
                entry.grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)
                self.form_vars[field] = var
                
                # Set default values for edit mode
                if is_edit and field in product:
                    if isinstance(product[field], float):
                        var.set(f"{product[field]:.2f}")
                    else:
                        var.set(str(product[field]))
            
            elif field_type == "combobox":
                var = tk.StringVar()
                combobox = ttk.Combobox(form_frame, textvariable=var, values=options[0])
                combobox.grid(row=i, column=1, sticky=tk.W, padx=5, pady=5)
                self.form_vars[field] = var
                
                # Set default values for edit mode
                if is_edit and field in product:
                    var.set(str(product[field]))
        
        # Buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        if is_edit:
            ttk.Button(btn_frame, text="Update", 
                      command=lambda: self.save_product(product['product_id'])).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(btn_frame, text="Save", 
                      command=lambda: self.save_product()).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
    
    def save_product(self, product_id=None):
        # Get values from form
        try:
            data = {
                'name': self.form_vars['name'].get(),
                'pack': self.form_vars['pack'].get(),
                'category': self.form_vars['category'].get(),
                'quantity': float(self.form_vars['quantity'].get()),
                'unit': self.form_vars['unit'].get(),
                'cost_price': float(self.form_vars['cost_price'].get()),
                'selling_price': float(self.form_vars['selling_price'].get()),
                'min_stock_level': float(self.form_vars['min_stock_level'].get()),
                'supplier': self.form_vars['supplier'].get()
            }
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and prices")
            return
        
        # Validate required fields
        if not all([data['name'], data['pack'], data['category'], data['unit']]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Save to database
        if product_id:  # Update existing product
            if update_product(
                product_id,
                data['name'],
                data['pack'],
                data['category'],
                data['unit'],
                data['cost_price'],
                data['selling_price'],
                data['min_stock_level'],
                data['supplier']
            ):
                messagebox.showinfo("Success", "Product updated successfully")
                self.show_inventory()
            else:
                messagebox.showerror("Error", "Failed to update product")
        else:  # Add new product
            if add_product(
                data['name'],
                data['pack'],
                data['category'],
                data['quantity'],
                data['unit'],
                data['cost_price'],
                data['selling_price'],
                data['min_stock_level'],
                data['supplier']
            ):
                messagebox.showinfo("Success", "Product added successfully")
                self.show_inventory()
            else:
                messagebox.showerror("Error", "Failed to add product")
    
    def show_add_stock(self):
        self.clear_content()
        self.update_status("Adding stock...")
        
        # Get all products
        products = get_all_products()
        if not products:
            messagebox.showwarning("Warning", "No products found. Please add products first.")
            self.show_inventory()
            return
        
        # Main form frame
        form_frame = ttk.LabelFrame(self.content_frame, text="Add Stock")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product selection
        ttk.Label(form_frame, text="Product:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.product_var = tk.StringVar()
        product_names = [f"{p['name']} ({p['pack']})" for p in products]
        product_combobox = ttk.Combobox(form_frame, textvariable=self.product_var, values=product_names)
        product_combobox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        product_combobox.current(0)
        
        # Amount
        ttk.Label(form_frame, text="Amount to Add:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        
        self.notes_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.notes_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Add Stock", command=self.process_add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
    
    def process_add_stock(self):
        # Get selected product
        product_name = self.product_var.get()
        products = get_all_products()
        selected_product = None
        
        for p in products:
            if f"{p['name']} ({p['pack']})" == product_name:
                selected_product = p
                break
        
        if not selected_product:
            messagebox.showerror("Error", "Please select a valid product")
            return
        
        # Get amount
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for amount")
            return
        
        # Get notes
        notes = self.notes_var.get()
        
        # Add stock
        if add_stock(selected_product['product_id'], amount, notes):
            messagebox.showinfo("Success", "Stock added successfully")
            self.show_inventory()
        else:
            messagebox.showerror("Error", "Failed to add stock")
    
    def show_record_sale(self):
        self.clear_content()
        self.update_status("Recording sale...")

        # Get all products
        products = get_all_products()
        if not products:
            messagebox.showwarning("Warning", "No products found. Please add products first.")
            self.show_inventory()
            return

        # Main form frame
        form_frame = ttk.LabelFrame(self.content_frame, text="Record Sale")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Product selection
        ttk.Label(form_frame, text="Product:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        self.sale_product_var = tk.StringVar()
        product_names = [f"{p['name']} ({p['pack']})" for p in products]
        product_combobox = ttk.Combobox(form_frame, textvariable=self.sale_product_var, values=product_names)
        product_combobox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        product_combobox.current(0)

        # Quantity
        ttk.Label(form_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

        self.sale_quantity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.sale_quantity_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Price (default to product's selling price)
        ttk.Label(form_frame, text="Price per Unit:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)

        self.sale_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.sale_price_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Sale Date
        ttk.Label(form_frame, text="Sale Date:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)

        self.sale_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=self.sale_date_var).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # Set default price when product changes
        def update_price(event=None):
            product_name = self.sale_product_var.get()
            for p in products:
                if f"{p['name']} ({p['pack']})" == product_name:
                    self.sale_price_var.set(f"{p['selling_price']:.2f}")
                    break
    
        self.sale_product_var.trace_add('write', update_price)
        update_price()  # Set initial price
    
        # Buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Record Sale", command=self.process_record_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)

        # Set default price
        def update_price(event=None):
            product_name = self.sale_product_var.get()
            for p in products:
                if f"{p['name']} ({p['pack']})" == product_name:
                    self.sale_price_var.set(f"{p['selling_price']:.2f}")
                    break
        
        self.sale_product_var.trace_add('write', update_price)
        update_price()  # Set initial price
        
        # Buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
       # ttk.Button(btn_frame, text="Record Sale", command=self.process_record_sale).pack(side=tk.LEFT, padx=5)
       # ttk.Button(btn_frame, text="Cancel", command=self.show_inventory).pack(side=tk.LEFT, padx=5)
    
    def process_record_sale(self):
        # Get selected product
        product_name = self.sale_product_var.get()
        products = get_all_products()
        selected_product = None
    
        for p in products:
            if f"{p['name']} ({p['pack']})" == product_name:
                selected_product = p
                break
                
        if not selected_product:
            messagebox.showerror("Error", "Please select a valid product")
            return

        # Get quantity
        try:
            quantity = float(self.sale_quantity_var.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for quantity")
            return

        # Get price
        try:
            price = float(self.sale_price_var.get())
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for price")
            return

        # Get and validate sale date
        try:
            sale_date_str = self.sale_date_var.get()
            sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format")
            return

        # Record sale with specified date
        if self._record_sale_with_date(selected_product['product_id'], quantity, price, sale_date):
            messagebox.showinfo("Success", "Sale recorded successfully")
            self.show_inventory()
        else:
            messagebox.showerror("Error", "Failed to record sale")
    def _record_sale_with_date(self, product_id, quantity, sale_price, sale_date):
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

                # Record the sale with specified date
                sale_query = """
                INSERT INTO sales 
                (product_id, quantity, sale_price, sale_date)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sale_query, (product_id, quantity, sale_price, sale_date))

                # Log the inventory change
                log_query = """
                INSERT INTO inventory_log 
                (product_id, change_type, amount, notes)
                VALUES (%s, 'remove', %s, %s)
                """
                cursor.execute(log_query, (product_id, quantity, 'Sale recorded'))

                conn.commit()
                print(f"Recorded sale of {quantity} units of product ID {product_id} on {sale_date}")
                return True
            except Error as e:
                print(f"Error recording sale: {e}")
                return False
            finally:
                close_db_connection(conn)
        return False
    def show_reports(self):
        self.clear_content()
        self.update_status("Loading reports...")
    
        # Create notebook for multiple report tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        # Sales Report Tab
        sales_frame = ttk.Frame(notebook)
        notebook.add(sales_frame, text="Sales Report")
    
        # Date range for sales report
        date_frame = ttk.Frame(sales_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))
    
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=10)
        from_date_entry.pack(side=tk.LEFT, padx=5)
    
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=10)
        to_date_entry.pack(side=tk.LEFT, padx=5)
    
        ttk.Button(date_frame, text="Generate", command=self.generate_sales_report).pack(side=tk.LEFT, padx=10)
    
        # Sales Treeview
        tree_frame = ttk.Frame(sales_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
    
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
        # Create treeview
        columns = ("ID", "Date", "Product", "Pack", "Quantity", "Unit Price", "Total")
        self.sales_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.sales_tree.pack(fill=tk.BOTH, expand=True)
    
        # Configure scrollbars
        y_scroll.config(command=self.sales_tree.yview)
        x_scroll.config(command=self.sales_tree.xview)
    
        # Format columns
        col_widths = [50, 120, 150, 100, 100, 80, 80]
        for col, width in zip(columns, col_widths):
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=width, anchor=tk.CENTER)
    
        # Generate initial report
        self.generate_sales_report()
    
        # Inventory Changes Tab
        changes_frame = ttk.Frame(notebook)
        notebook.add(changes_frame, text="Inventory Changes")
    
        # Date range for changes report
        changes_date_frame = ttk.Frame(changes_frame)
        changes_date_frame.pack(fill=tk.X, pady=(0, 10))
    
        ttk.Label(changes_date_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.changes_from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        changes_from_date_entry = ttk.Entry(changes_date_frame, textvariable=self.changes_from_date_var, width=10)
        changes_from_date_entry.pack(side=tk.LEFT, padx=5)
    
        ttk.Label(changes_date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.changes_to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        changes_to_date_entry = ttk.Entry(changes_date_frame, textvariable=self.changes_to_date_var, width=10)
        changes_to_date_entry.pack(side=tk.LEFT, padx=5)
    
        ttk.Button(changes_date_frame, text="Generate", command=self.generate_changes_report).pack(side=tk.LEFT, padx=10)
    
        # Changes Treeview
        changes_tree_frame = ttk.Frame(changes_frame)
        changes_tree_frame.pack(fill=tk.BOTH, expand=True)
    
        changes_y_scroll = ttk.Scrollbar(changes_tree_frame)
        changes_y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
        changes_x_scroll = ttk.Scrollbar(changes_tree_frame, orient=tk.HORIZONTAL)
        changes_x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
        changes_columns = ("Date", "Product", "Pack", "Type", "Amount", "Notes")
        self.changes_tree = ttk.Treeview(changes_tree_frame, columns=changes_columns, show="headings",
                                   yscrollcommand=changes_y_scroll.set, xscrollcommand=changes_x_scroll.set)
        self.changes_tree.pack(fill=tk.BOTH, expand=True)
    
        changes_y_scroll.config(command=self.changes_tree.yview)
        changes_x_scroll.config(command=self.changes_tree.xview)
    
        # Format columns
        changes_col_widths = [120, 150, 100, 80, 80, 200]
        for col, width in zip(changes_columns, changes_col_widths):
            self.changes_tree.heading(col, text=col)
            self.changes_tree.column(col, width=width, anchor=tk.CENTER)
    
        # Generate initial report
        self.generate_changes_report()
    
        # Sales Chart Tab
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="Sales Chart")
    
        # Create figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        # Add refresh button
        refresh_frame = ttk.Frame(chart_frame)
        refresh_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(refresh_frame, text="Refresh Chart", command=self.generate_sales_chart).pack(side=tk.LEFT, padx=5)
    
        # Generate initial chart
        self.generate_sales_chart()
    
        self.update_status("Reports loaded successfully")
    
    def generate_sales_report(self):
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
    
        # Validate dates
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Please enter dates in YYYY-MM-DD format")
            return
    
        sales = get_sales_report(from_date, to_date)
    
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        # Insert new data
        total_sales = 0
        total_quantity = 0

        for sale in sales:
            total = sale['quantity'] * sale['sale_price']
            total_sales += total
            total_quantity += sale['quantity']

            values = (
                sale['sale_id'],
                sale['sale_date'].strftime('%Y-%m-%d %H:%M'),
                sale['name'],
                sale['Pack'],
                f"{sale['quantity']:.2f} {sale['unit']}",
                f"${sale['sale_price']:.2f}",
                f"${total:.2f}"
            )
            self.sales_tree.insert('', tk.END, values=values)

        # Add total row
        self.sales_tree.insert('', tk.END, values=(
            "", 
            f"{len(sales)} sales", 
            "", 
            "", 
            f"{total_quantity:.2f} total", 
            "Total:", 
            f"${total_sales:.2f}"
        ), tags=('total',))
        self.sales_tree.tag_configure('total', background='#e0e0e0', font=('Arial', 10, 'bold'))
    
    def generate_changes_report(self):
        from_date = self.changes_from_date_var.get()
        to_date = self.changes_to_date_var.get()
    
        # Validate dates
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Please enter dates in YYYY-MM-DD format")
            return

        changes = get_inventory_changes_report(None, from_date, to_date)

        # Clear existing data
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)

        # Insert new data
        for change in changes:
            values = (
                change['log_date'].strftime('%Y-%m-%d %H:%M'),
                change['name'],
                change['Pack'],
                change['change_type'].capitalize(),
                f"{change['amount']:.2f} {change['unit']}",
                change['notes'] if change['notes'] else "-"
            )
            tag = 'add' if change['change_type'] == 'add' else 'remove'
            self.changes_tree.insert('', tk.END, values=values, tags=(tag,))

        # Configure tags
        self.changes_tree.tag_configure('add', background='#ddffdd')
        self.changes_tree.tag_configure('remove', background='#ffdddd')

        # Add summary
        if changes:
            add_count = sum(1 for c in changes if c['change_type'] == 'add')
            remove_count = len(changes) - add_count
            self.changes_tree.insert('', tk.END, values=(
                "", 
                f"{len(changes)} changes", 
                "", 
                f"{add_count} additions, {remove_count} removals", 
                "", 
                ""
            ), tags=('total',))
            self.changes_tree.tag_configure('total', background='#e0e0e0', font=('Arial', 10, 'bold'))

    def generate_sales_chart(self):
        # Get date range from the sales report tab
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()

        # Validate dates
        try:
            datetime.strptime(from_date, '%Y-%m-%d')
            datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Please enter valid dates in YYYY-MM-DD format in the Sales Report tab")
            return

        sales_data = get_sales_by_date(from_date, to_date)

        if not sales_data:
            messagebox.showinfo("Info", "No sales data found for the selected date range")
            return

        # Prepare data for chart - MODIFIED THIS PART
        dates = []
        amounts = []
        date_labels = []

        for item in sales_data:
            # Handle both string and date objects
            if isinstance(item['sale_day'], str):
                sale_date = datetime.strptime(item['sale_day'], '%Y-%m-%d').date()
            else:  # It's already a date object
                sale_date = item['sale_day']

            dates.append(sale_date)
            amounts.append(item['total_sales'])
            date_labels.append(sale_date.strftime('%m-%d'))  # Format as MM-DD for x-axis

        # Clear previous chart
        self.ax.clear()

        # Create new chart
        bars = self.ax.bar(date_labels, amounts, color='skyblue')
        self.ax.set_title(f'Sales from {from_date} to {to_date}')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Total Sales ($)')

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:.2f}',
                        ha='center', va='bottom')

        # Rotate x-axis labels for better readability
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')

        # Adjust layout
        self.fig.tight_layout()

        # Redraw canvas
        self.canvas.draw()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
