import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui_components import ProductDialog, create_styles

class POSInventorySystem:
    def __init__(self, root):
        self.root = root
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.title("POS & Inventory Management System")
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg='#ffffff')  # White background

        # Create a modern black and white theme
        create_styles()
        
        self.init_database()
        self.create_widgets()
        self.refresh_products()
        self.refresh_sales_history()

    def init_database(self):
        """Initialize SQLite database and create tables"""
        self.conn = sqlite3.connect('pos_inventory.db')
        self.cursor = self.conn.cursor()

        # Create products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                category TEXT,
                barcode TEXT UNIQUE,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create sales table with product_category column
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_id INTEGER,
                product_name TEXT,
                product_category TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Add product_category column if it doesn't exist
        self.cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'product_category' not in columns:
            self.cursor.execute('ALTER TABLE sales ADD COLUMN product_category TEXT')

        # Create transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def create_widgets(self):
        """Create the main GUI interface"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # POS Tab
        self.pos_frame = ttk.Frame(notebook)
        notebook.add(self.pos_frame, text='Point of Sale')
        self.create_pos_interface()

        # Inventory Tab
        self.inventory_frame = ttk.Frame(notebook)
        notebook.add(self.inventory_frame, text='Inventory Management')
        self.create_inventory_interface()

        # Sales History Tab
        self.sales_frame = ttk.Frame(notebook)
        notebook.add(self.sales_frame, text='Sales History')
        self.create_sales_interface()

        # Statistics Tab
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text='Statistics Dashboard')
        self.create_stats_interface()

    def create_stats_interface(self):
        """Create the statistics dashboard with graphs"""
        # Frame for controls
        controls_frame = ttk.Frame(self.stats_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Time period selection
        ttk.Label(controls_frame, text="Time Period:").pack(side='left', padx=(0, 5))
        self.time_period_var = tk.StringVar(value="7")
        time_period_combo = ttk.Combobox(controls_frame, textvariable=self.time_period_var,
                                        values=["7", "30", "90", "365", "All"], width=5)
        time_period_combo.pack(side='left', padx=(0, 10))
        
        # Graph type selection
        ttk.Label(controls_frame, text="Graph Type:").pack(side='left', padx=(0, 5))
        self.graph_type_var = tk.StringVar(value="Sales Trend")
        graph_type_combo = ttk.Combobox(controls_frame, textvariable=self.graph_type_var,
                                       values=["Sales Trend", "Category Distribution", 
                                               "Top Products", "Revenue by Payment Method"])
        graph_type_combo.pack(side='left', padx=(0, 10))
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh", command=self.update_stats).pack(side='left')
        
        # Frame for graphs
        self.graph_frame = ttk.Frame(self.stats_frame)
        self.graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initial graph display
        self.update_stats()

    def update_stats(self):
        """Update the statistics graphs based on selected options"""
        # Clear previous graphs
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Get selected options
        time_period = self.time_period_var.get()
        graph_type = self.graph_type_var.get()
        
        # Create figure
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Generate appropriate graph based on selection
        if graph_type == "Sales Trend":
            self.generate_sales_trend(ax, time_period)
        elif graph_type == "Category Distribution":
            self.generate_category_distribution(ax, time_period)
        elif graph_type == "Top Products":
            self.generate_top_products(ax, time_period)
        elif graph_type == "Revenue by Payment Method":
            self.generate_payment_method_stats(ax, time_period)
        
        # Add figure to Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def generate_sales_trend(self, ax, time_period):
        """Generate sales trend graph"""
        if time_period == "All":
            self.cursor.execute('''
                SELECT date(sale_date) as day, SUM(total) as daily_total
                FROM sales
                GROUP BY day
                ORDER BY day
            ''')
        else:
            days = int(time_period)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            self.cursor.execute('''
                SELECT date(sale_date) as day, SUM(total) as daily_total
                FROM sales
                WHERE sale_date >= ?
                GROUP BY day
                ORDER BY day
            ''', (start_date,))
        
        data = self.cursor.fetchall()
        if not data:
            ax.set_title("No sales data available")
            return
            
        dates = [row[0] for row in data]
        amounts = [row[1] for row in data]
        
        ax.plot(dates, amounts, marker='o')
        ax.set_title(f"Sales Trend (Last {time_period} days)" if time_period != "All" else "Sales Trend (All Time)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Total Sales (₱)")
        ax.grid(True)
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    def generate_category_distribution(self, ax, time_period):
        """Generate pie chart of sales by category"""
        if time_period == "All":
            self.cursor.execute('''
                SELECT product_category, SUM(total) as category_total
                FROM sales
                GROUP BY product_category
                ORDER BY category_total DESC
            ''')
        else:
            days = int(time_period)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            self.cursor.execute('''
                SELECT product_category, SUM(total) as category_total
                FROM sales
                WHERE sale_date >= ?
                GROUP BY product_category
                ORDER BY category_total DESC
            ''', (start_date,))
        
        data = self.cursor.fetchall()
        if not data:
            ax.set_title("No sales data available")
            return
            
        categories = [row[0] if row[0] else 'Uncategorized' for row in data]
        amounts = [row[1] for row in data]
        
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title(f"Sales by Category (Last {time_period} days)" if time_period != "All" else "Sales by Category (All Time)")
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    def generate_top_products(self, ax, time_period):
        """Generate bar chart of top selling products"""
        if time_period == "All":
            self.cursor.execute('''
                SELECT product_name, SUM(quantity) as total_quantity, SUM(total) as total_revenue
                FROM sales
                GROUP BY product_name
                ORDER BY total_revenue DESC
                LIMIT 10
            ''')
        else:
            days = int(time_period)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            self.cursor.execute('''
                SELECT product_name, SUM(quantity) as total_quantity, SUM(total) as total_revenue
                FROM sales
                WHERE sale_date >= ?
                GROUP BY product_name
                ORDER BY total_revenue DESC
                LIMIT 10
            ''', (start_date,))
        
        data = self.cursor.fetchall()
        if not data:
            ax.set_title("No sales data available")
            return
            
        products = [row[0] for row in data]
        revenue = [row[2] for row in data]
        
        y_pos = range(len(products))
        ax.barh(y_pos, revenue, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(products)
        ax.invert_yaxis()  # highest revenue at top
        ax.set_xlabel('Total Revenue (₱)')
        ax.set_title(f"Top Products by Revenue (Last {time_period} days)" if time_period != "All" else "Top Products by Revenue (All Time)")

    def generate_payment_method_stats(self, ax, time_period):
        """Generate bar chart of revenue by payment method"""
        if time_period == "All":
            self.cursor.execute('''
                SELECT payment_method, SUM(total_amount) as method_total
                FROM transactions
                GROUP BY payment_method
                ORDER BY method_total DESC
            ''')
        else:
            days = int(time_period)
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            self.cursor.execute('''
                SELECT payment_method, SUM(total_amount) as method_total
                FROM transactions
                WHERE transaction_date >= ?
                GROUP BY payment_method
                ORDER BY method_total DESC
            ''', (start_date,))
        
        data = self.cursor.fetchall()
        if not data:
            ax.set_title("No transaction data available")
            return
            
        methods = [row[0] if row[0] else 'Unknown' for row in data]
        amounts = [row[1] for row in data]
        
        y_pos = range(len(methods))
        ax.bar(y_pos, amounts)
        ax.set_xticks(y_pos)
        ax.set_xticklabels(methods)
        ax.set_ylabel('Total Revenue (₱)')
        ax.set_title(f"Revenue by Payment Method (Last {time_period} days)" if time_period != "All" else "Revenue by Payment Method (All Time)")

    def create_pos_interface(self):
        left_frame = ttk.Frame(self.pos_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(search_frame, text="Search Product:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<KeyRelease>', self.search_products)

        ttk.Label(left_frame, text="Available Products:").pack(anchor='w')
        products_frame = ttk.Frame(left_frame)
        products_frame.pack(fill='both', expand=True)

        self.products_listbox = tk.Listbox(products_frame, bg="#2d2d2d", fg="#ffffff", selectbackground="#505050")
        products_scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=self.products_listbox.yview)
        self.products_listbox.configure(yscrollcommand=products_scrollbar.set)
        self.products_listbox.pack(side='left', fill='both', expand=True)
        products_scrollbar.pack(side='right', fill='y')

        ttk.Button(left_frame, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

        right_frame = ttk.Frame(self.pos_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Shopping Cart:", font=('Arial', 12, 'bold')).pack(anchor='w')

        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill='both', expand=True, pady=10)

        columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        self.cart_tree.pack(side='left', fill='both', expand=True)
        cart_scrollbar.pack(side='right', fill='y')

        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill='x', pady=10)
        ttk.Button(controls_frame, text="Remove Item", command=self.remove_from_cart).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Clear Cart", command=self.clear_cart).pack(side='left')

        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill='x', pady=10)
        self.total_label = ttk.Label(total_frame, text="Total: ₱0.00", font=('Arial', 14, 'bold'))
        self.total_label.pack(anchor='e')

        checkout_frame = ttk.Frame(right_frame)
        checkout_frame.pack(fill='x')
        ttk.Label(checkout_frame, text="Payment:").pack(side='left')
        self.payment_var = tk.StringVar(value='Cash')
        payment_combo = ttk.Combobox(checkout_frame, textvariable=self.payment_var,
                                     values=['Cash', 'Card', 'Check'], state='readonly')
        payment_combo.pack(side='left', padx=5)
        ttk.Button(checkout_frame, text="Checkout", command=self.checkout,
                   style='Accent.TButton').pack(side='right')

        self.cart_items = []

    def create_inventory_interface(self):
        top_frame = ttk.Frame(self.inventory_frame)
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(top_frame, text="Add Product", command=self.add_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Edit Product", command=self.edit_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Delete Product", command=self.delete_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Refresh", command=self.refresh_products).pack(side='left')

        tree_frame = ttk.Frame(self.inventory_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Name', 'Price', 'Stock', 'Category', 'Barcode')
        self.inventory_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            if col == 'ID':
                self.inventory_tree.column(col, width=50)
            elif col == 'Name':
                self.inventory_tree.column(col, width=200)
            else:
                self.inventory_tree.column(col, width=100)

        inventory_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=inventory_scrollbar.set)
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        inventory_scrollbar.pack(side='right', fill='y')

    def create_sales_interface(self):
        controls_frame = ttk.Frame(self.sales_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(controls_frame, text="Refresh", command=self.refresh_sales_history).pack(side='left')

        sales_tree_frame = ttk.Frame(self.sales_frame)
        sales_tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Sales Date', 'Product Category', 'Product Name', 'Product ID', 'Quantity', 'Unit Price', 'Total Price')
        self.sales_tree = ttk.Treeview(sales_tree_frame, columns=columns, show='headings')
        for col in columns:
            self.sales_tree.heading(col, text=col)
            if col == 'Sales Date':
                self.sales_tree.column(col, width=150)
            elif col == 'Product Name':
                self.sales_tree.column(col, width=200)
            elif col == 'Product ID':
                self.sales_tree.column(col, width=80)
            elif col in ['Quantity', 'Unit Price', 'Total Price']:
                self.sales_tree.column(col, width=100)
            else:
                self.sales_tree.column(col, width=120)

        sales_scrollbar = ttk.Scrollbar(sales_tree_frame, orient='vertical', command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        self.sales_tree.pack(side='left', fill='both', expand=True)
        sales_scrollbar.pack(side='right', fill='y')

    def search_products(self, event=None):
        search_term = self.search_var.get().lower()
        self.cursor.execute('''
            SELECT name, price, stock FROM products 
            WHERE LOWER(name) LIKE ? AND stock > 0
        ''', (f'%{search_term}%',))
        products = self.cursor.fetchall()
        self.products_listbox.delete(0, tk.END)
        for product in products:
            self.products_listbox.insert(tk.END, f"{product[0]} - ₱{product[1]:.2f} (Stock: {product[2]})")

    def add_to_cart(self):
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart.")
            return
        product_text = self.products_listbox.get(selection[0])
        product_name = product_text.split(' - ')[0]
        self.cursor.execute('SELECT id, name, price, stock FROM products WHERE name = ?', (product_name,))
        product = self.cursor.fetchone()
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        if product[3] <= 0:
            messagebox.showerror("Error", "Product is out of stock.")
            return
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {product_name}:",
                                           minvalue=1, maxvalue=product[3])
        if not quantity:
            return
        item_total = product[2] * quantity
        self.cart_items.append({
            'id': product[0],
            'name': product[1],
            'price': product[2],
            'quantity': quantity,
            'total': item_total
        })
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        total = 0
        for item in self.cart_items:
            self.cart_tree.insert('', 'end', values=(
                item['name'],
                item['quantity'],
                f"₱{item['price']:.2f}",
                f"₱{item['total']:.2f}"
            ))
            total += item['total']
        self.total_label.config(text=f"Total: ₱{total:.2f}")

    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        item_index = self.cart_tree.index(selection[0])
        del self.cart_items[item_index]
        self.refresh_cart()

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart()

    def checkout(self):
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty.")
            return
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_amount = sum(item['total'] for item in self.cart_items)
        try:
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, total_amount, payment_method)
                VALUES (?, ?, ?)
            ''', (transaction_id, total_amount, self.payment_var.get()))
            for item in self.cart_items:
                self.cursor.execute('SELECT category FROM products WHERE id = ?', (item['id'],))
                category_result = self.cursor.fetchone()
                category = category_result[0] if category_result else "Uncategorized"
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, product_category, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (transaction_id, item['id'], item['name'], category, item['quantity'], item['price'], item['total']))
                self.cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE id = ?
                ''', (item['quantity'], item['id']))
            self.conn.commit()
            messagebox.showinfo("Success", f"Transaction completed!\n"
                                          f"Transaction ID: {transaction_id}\n"
                                          f"Total: ₱{total_amount:.2f}")
            self.clear_cart()
            self.refresh_products()
            self.refresh_sales_history()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Transaction failed: {str(e)}")
            self.conn.rollback()

    def add_product(self):
        dialog = ProductDialog(self.root, "Add Product")
        if dialog.result:
            try:
                self.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, barcode)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], dialog.result['price'], dialog.result['stock'],
                      dialog.result['category'], dialog.result['barcode']))
                product_id = self.cursor.lastrowid
                transaction_id = f"INIT{datetime.now().strftime('%Y%m%d%H%M%S')}"
                quantity = 0
                total = 0
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, product_category, 
                                      quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (transaction_id, product_id, dialog.result['name'], dialog.result['category'],
                      quantity, dialog.result['price'], total))
                self.conn.commit()
                self.refresh_products()
                self.refresh_sales_history()
                messagebox.showinfo("Success", "Product added successfully with initial sales record!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Barcode already exists!")
                self.conn.rollback()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
                self.conn.rollback()

    def edit_product(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        dialog = ProductDialog(self.root, "Edit Product", product)
        if dialog.result:
            try:
                self.cursor.execute('''
                    UPDATE products SET name = ?, price = ?, stock = ?, category = ?, barcode = ?
                    WHERE id = ?
                ''', (dialog.result['name'], dialog.result['price'], dialog.result['stock'],
                      dialog.result['category'], dialog.result['barcode'], product_id))
                self.cursor.execute('''
                    UPDATE sales SET product_name = ?, product_category = ?, price = ?
                    WHERE product_id = ?
                ''', (dialog.result['name'], dialog.result['category'], dialog.result['price'], product_id))
                self.conn.commit()
                self.refresh_products()
                self.refresh_sales_history()
                messagebox.showinfo("Success", "Product updated successfully with sales records!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Barcode already exists!")
                self.conn.rollback()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update product: {str(e)}")
                self.conn.rollback()

    def delete_product(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            try:
                self.cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_id,))
                self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.conn.commit()
                self.refresh_products()
                self.refresh_sales_history()
                messagebox.showinfo("Success", "Product and associated sales records deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                self.conn.rollback()

    def refresh_products(self):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        self.cursor.execute('SELECT * FROM products ORDER BY name')
        products = self.cursor.fetchall()
        for product in products:
            self.inventory_tree.insert('', 'end', values=product[:-1])
        self.search_products()

    def refresh_sales_history(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        self.cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'product_category' in columns:
            self.cursor.execute('''
                SELECT sale_date, product_category, product_name, product_id, quantity, price, total
                FROM sales ORDER BY sale_date DESC
            ''')
        else:
            self.cursor.execute('''
                SELECT sale_date, 'Uncategorized', product_name, product_id, quantity, price, total
                FROM sales ORDER BY sale_date DESC
            ''')
        sales = self.cursor.fetchall()
        for sale in sales:
            date_str = sale[0].split('.')[0] if isinstance(sale[0], str) else sale[0]
            self.sales_tree.insert('', 'end', values=(
                date_str,
                sale[1],
                sale[2],
                sale[3],
                sale[4],
                f"₱{sale[5]:.2f}",
                f"₱{sale[6]:.2f}"
            ))

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = POSInventorySystem(root)
    root.mainloop()