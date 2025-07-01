import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import os


class POSInventorySystem:
    def __init__(self, root):
        self.root = root

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window title and size to fit screen
        self.root.title("POS & Inventory Management System")
        self.root.geometry(f"{screen_width}x{screen_height}")

        self.root.configure(bg='#f0f0f0')

        # Initialize database
        self.init_database()

        # Create main interface
        self.create_widgets()

        # Load initial data
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
        
        # Create sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
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
        # Create notebook for tabs
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
    
    def create_pos_interface(self):
        """Create POS interface"""
        # Left side - Product search and selection
        left_frame = ttk.Frame(self.pos_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search Product:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # Products listbox
        ttk.Label(left_frame, text="Available Products:").pack(anchor='w')
        
        products_frame = ttk.Frame(left_frame)
        products_frame.pack(fill='both', expand=True)
        
        self.products_listbox = tk.Listbox(products_frame)
        products_scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=self.products_listbox.yview)
        self.products_listbox.configure(yscrollcommand=products_scrollbar.set)
        
        self.products_listbox.pack(side='left', fill='both', expand=True)
        products_scrollbar.pack(side='right', fill='y')
        
        # Add to cart button
        ttk.Button(left_frame, text="Add to Cart", command=self.add_to_cart).pack(pady=10)
        
        # Right side - Shopping cart
        right_frame = ttk.Frame(self.pos_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(right_frame, text="Shopping Cart:", font=('Arial', 12, 'bold')).pack(anchor='w')
        
        # Cart treeview
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
        
        # Cart controls
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Button(controls_frame, text="Remove Item", command=self.remove_from_cart).pack(side='left', padx=(0, 5))
        ttk.Button(controls_frame, text="Clear Cart", command=self.clear_cart).pack(side='left')
        
        # Total and checkout
        total_frame = ttk.Frame(right_frame)
        total_frame.pack(fill='x', pady=10)
        
        self.total_label = ttk.Label(total_frame, text="Total: $0.00", font=('Arial', 14, 'bold'))
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
        
        # Initialize cart
        self.cart_items = []
    
    def create_inventory_interface(self):
        """Create inventory management interface"""
        # Top frame for controls
        top_frame = ttk.Frame(self.inventory_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(top_frame, text="Add Product", command=self.add_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Edit Product", command=self.edit_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Delete Product", command=self.delete_product).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Refresh", command=self.refresh_products).pack(side='left')
        
        # Products treeview
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
        """Create sales history interface"""
        # Controls frame
        controls_frame = ttk.Frame(self.sales_frame)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_sales_history).pack(side='left')
        
        # Sales treeview
        sales_tree_frame = ttk.Frame(self.sales_frame)
        sales_tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Transaction ID', 'Product', 'Quantity', 'Price', 'Total', 'Date')
        self.sales_tree = ttk.Treeview(sales_tree_frame, columns=columns, show='headings')
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            if col == 'Transaction ID':
                self.sales_tree.column(col, width=150)
            elif col == 'Product':
                self.sales_tree.column(col, width=200)
            else:
                self.sales_tree.column(col, width=100)
        
        sales_scrollbar = ttk.Scrollbar(sales_tree_frame, orient='vertical', command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=sales_scrollbar.set)
        
        self.sales_tree.pack(side='left', fill='both', expand=True)
        sales_scrollbar.pack(side='right', fill='y')
    
    def search_products(self, event=None):
        """Search products by name"""
        search_term = self.search_var.get().lower()
        
        self.cursor.execute('''
            SELECT name, price, stock FROM products 
            WHERE LOWER(name) LIKE ? AND stock > 0
        ''', (f'%{search_term}%',))
        
        products = self.cursor.fetchall()
        
        self.products_listbox.delete(0, tk.END)
        for product in products:
            self.products_listbox.insert(tk.END, f"{product[0]} - ${product[1]:.2f} (Stock: {product[2]})")
    
    def add_to_cart(self):
        """Add selected product to cart"""
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart.")
            return
        
        product_text = self.products_listbox.get(selection[0])
        product_name = product_text.split(' - ')[0]
        
        # Get product details
        self.cursor.execute('SELECT id, name, price, stock FROM products WHERE name = ?', (product_name,))
        product = self.cursor.fetchone()
        
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return
        
        if product[3] <= 0:
            messagebox.showerror("Error", "Product is out of stock.")
            return
        
        # Ask for quantity
        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {product_name}:", 
                                         minvalue=1, maxvalue=product[3])
        if not quantity:
            return
        
        # Add to cart
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
        """Refresh cart display"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add items to cart tree
        total = 0
        for item in self.cart_items:
            self.cart_tree.insert('', 'end', values=(
                item['name'], 
                item['quantity'], 
                f"${item['price']:.2f}", 
                f"${item['total']:.2f}"
            ))
            total += item['total']
        
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove.")
            return
        
        item_index = self.cart_tree.index(selection[0])
        del self.cart_items[item_index]
        self.refresh_cart()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items.clear()
        self.refresh_cart()
    
    def checkout(self):
        """Process checkout"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty.")
            return
        
        # Generate transaction ID
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate total
        total_amount = sum(item['total'] for item in self.cart_items)
        
        try:
            # Save transaction
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, total_amount, payment_method)
                VALUES (?, ?, ?)
            ''', (transaction_id, total_amount, self.payment_var.get()))
            
            # Save sales and update inventory
            for item in self.cart_items:
                # Save sale
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (transaction_id, item['id'], item['name'], item['quantity'], item['price'], item['total']))
                
                # Update inventory
                self.cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE id = ?
                ''', (item['quantity'], item['id']))
            
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Transaction completed!\nTransaction ID: {transaction_id}\nTotal: ${total_amount:.2f}")
            
            # Clear cart
            self.clear_cart()
            
            # Refresh data
            self.refresh_products()
            self.refresh_sales_history()
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Transaction failed: {str(e)}")
            self.conn.rollback()
    
    def add_product(self):
        """Add new product dialog"""
        dialog = ProductDialog(self.root, "Add Product")
        if dialog.result:
            try:
                self.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, barcode)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], dialog.result['price'], dialog.result['stock'], 
                     dialog.result['category'], dialog.result['barcode']))
                self.conn.commit()
                self.refresh_products()
                messagebox.showinfo("Success", "Product added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Barcode already exists!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def edit_product(self):
        """Edit selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Get current product data
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
                self.conn.commit()
                self.refresh_products()
                messagebox.showinfo("Success", "Product updated successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Barcode already exists!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update product: {str(e)}")
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            try:
                self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.conn.commit()
                self.refresh_products()
                messagebox.showinfo("Success", "Product deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
    
    def refresh_products(self):
        """Refresh products display"""
        # Clear inventory tree
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Fetch and display products
        self.cursor.execute('SELECT * FROM products ORDER BY name')
        products = self.cursor.fetchall()
        
        for product in products:
            self.inventory_tree.insert('', 'end', values=product[:-1])  # Exclude date_added
        
        # Refresh POS products list
        self.search_products()
    
    def refresh_sales_history(self):
        """Refresh sales history display"""
        # Clear sales tree
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Fetch and display sales
        self.cursor.execute('''
            SELECT transaction_id, product_name, quantity, price, total, sale_date
            FROM sales ORDER BY sale_date DESC
        ''')
        sales = self.cursor.fetchall()
        
        for sale in sales:
            # Format date
            date_str = sale[5].split('.')[0]  # Remove microseconds
            self.sales_tree.insert('', 'end', values=sale[:5] + (date_str,))
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


class ProductDialog:
    def __init__(self, parent, title, product_data=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(product_data)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, product_data):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Product name
        ttk.Label(main_frame, text="Product Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar(value=product_data[1] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # Price
        ttk.Label(main_frame, text="Price:").grid(row=1, column=0, sticky='w', pady=5)
        self.price_var = tk.StringVar(value=str(product_data[2]) if product_data else "")
        ttk.Entry(main_frame, textvariable=self.price_var, width=30).grid(row=1, column=1, pady=5)
        
        # Stock
        ttk.Label(main_frame, text="Stock:").grid(row=2, column=0, sticky='w', pady=5)
        self.stock_var = tk.StringVar(value=str(product_data[3]) if product_data else "")
        ttk.Entry(main_frame, textvariable=self.stock_var, width=30).grid(row=2, column=1, pady=5)
        
        # Category
        ttk.Label(main_frame, text="Category:").grid(row=3, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar(value=product_data[4] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.category_var, width=30).grid(row=3, column=1, pady=5)
        
        # Barcode
        ttk.Label(main_frame, text="Barcode:").grid(row=4, column=0, sticky='w', pady=5)
        self.barcode_var = tk.StringVar(value=product_data[5] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.barcode_var, width=30).grid(row=4, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)
    
    def save(self):
        """Save product data"""
        try:
            name = self.name_var.get().strip()
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
            category = self.category_var.get().strip()
            barcode = self.barcode_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                return
            
            if price < 0:
                messagebox.showerror("Error", "Price cannot be negative!")
                return
            
            if stock < 0:
                messagebox.showerror("Error", "Stock cannot be negative!")
                return
            
            self.result = {
                'name': name,
                'price': price,
                'stock': stock,
                'category': category,
                'barcode': barcode if barcode else None
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for price and stock!")
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

    
if __name__ == "__main__":
    root = tk.Tk()
    app = POSInventorySystem(root)
    root.mainloop()

