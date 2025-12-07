import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from ui_components import ProductDialog

class InventoryModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.search_var = None
        self.category_filter_var = None
        
    def generate_product_id(self):
        """Generate a unique product ID in format PROD-XXXX"""
        try:
            # Get the highest existing product ID number
            self.main_app.cursor.execute('''
                SELECT product_id FROM products 
                WHERE product_id LIKE 'PROD-%'
                ORDER BY CAST(SUBSTR(product_id, 6) AS INTEGER) DESC 
                LIMIT 1
            ''')
            
            result = self.main_app.cursor.fetchone()
            
            if result:
                # Extract the number from the last product ID (e.g., "PROD-0001" -> 1)
                last_number = int(result[0].split('-')[1])
                new_number = last_number + 1
            else:
                # First product ID
                new_number = 1
            
            # Format as PROD-XXXX (e.g., PROD-0001, PROD-0002, etc.)
            return f"PROD-{new_number:04d}"
            
        except Exception as e:
            print(f"Error generating product ID: {e}")
            # Fallback to timestamp-based ID if there's an error
            import time
            return f"PROD-{int(time.time()) % 10000:04d}"
        
    def create_interface(self):
        """Create the inventory management interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Inventory", style='PageTitle.TLabel').pack(side='left')
        
        # Statistics Panel
        self.create_statistics_panel()
        
        # Filter and Search frame
        filter_search_frame = ttk.Frame(self.frame, style='Content.TFrame')
        filter_search_frame.pack(fill='x', padx=30, pady=10)
        
        # Category filter dropdown
        ttk.Label(filter_search_frame, text="Category:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        
        self.category_filter_var = tk.StringVar(value="All Categories")
        category_combo = ttk.Combobox(filter_search_frame, textvariable=self.category_filter_var,
                                     values=['All Categories', 'Bikes', 'Accessories', 'Parts', 'Clothing', 'Maintenance'],
                                     state='readonly', style='Modern.TCombobox', width=18)
        category_combo.pack(side='left', padx=(0, 20))
        category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Search box
        ttk.Label(filter_search_frame, text="Search:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(filter_search_frame, textvariable=self.search_var, width=30, style='Modern.TEntry')
        search_entry.pack(side='left', padx=(0, 10))
        
        # Clear filters button
        ttk.Button(filter_search_frame, text="Clear Filters", command=self.clear_filters, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        
        # Search hint label
        ttk.Label(filter_search_frame, text="(Search by name or product ID)", 
                 style='Hint.TLabel').pack(side='left', padx=(10, 0))
        
        # Controls
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Button(controls_frame, text="Add Product", command=self.add_product, 
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Add Stock", command=self.add_stock, 
                  style='Success.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit Product", command=self.edit_product, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete Product", command=self.delete_product, 
                  style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="📊 View Stock History", command=self.view_stock_history, 
                  style='Primary.TButton').pack(side='left')
        
        # Inventory table
        table_frame = ttk.Frame(self.frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview (ID column hidden but stored)
        columns = ('ID', 'Product ID', 'Name', 'Category', 'Price', 'Stock')
        display_columns = ('Product ID', 'Name', 'Category', 'Price', 'Stock')
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, displaycolumns=display_columns, 
                                          show='headings', style='Modern.Treeview')
        
        # Set headings and alignment for displayed columns
        column_configs = {
            'Product ID': {'width': 120, 'anchor': 'center'},
            'Name': {'width': 250, 'anchor': 'w'},
            'Category': {'width': 150, 'anchor': 'center'},
            'Price': {'width': 120, 'anchor': 'center'},
            'Stock': {'width': 100, 'anchor': 'center'}
        }
        
        for col in display_columns:
            self.inventory_tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            config = column_configs.get(col, {'width': 120, 'anchor': 'center'})
            self.inventory_tree.column(col, width=config['width'], anchor=config['anchor'])

        # Bind double-click event to view stock history
        self.inventory_tree.bind('<Double-1>', lambda e: self.view_stock_history())

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status bar showing filtered results
        self.status_frame = ttk.Frame(self.frame, style='Content.TFrame')
        self.status_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="", style='FieldLabel.TLabel')
        self.status_label.pack(side='left')
        
        # Hint label
        hint_label = ttk.Label(self.status_frame, text="💡 Tip: Double-click a product to view its stock history", 
                              style='ValidationNote.TLabel')
        hint_label.pack(side='right')
        
        # Load initial data
        self.refresh_products()
        
        print("Inventory interface created successfully")  # Debug print
        
        return self.frame

    def view_stock_history(self):
        """View stock history for the selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to view its stock history.")
            return
        
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]  # Hidden ID
        product_code = item['values'][1]  # Product ID
        product_name = item['values'][2]  # Name
        current_stock = item['values'][5]  # Stock
        
        # Create stock history dialog
        StockHistoryDialog(self.main_app.root, self.main_app, product_code, product_name, current_stock)

    def sort_column(self, col):
        """Sort treeview by column"""
        try:
            # Get current items
            items = [(self.inventory_tree.set(item, col), item) for item in self.inventory_tree.get_children('')]
            
            # Determine if we should sort as numbers or strings
            try:
                # Try to sort as numbers (for Price and Stock columns)
                if col in ['Price', 'Stock']:
                    # Remove currency symbol and commas for Price
                    items = [(float(val.replace('₱', '').replace(',', '')), item) for val, item in items]
                    items.sort(reverse=False)
                else:
                    items.sort(reverse=False)
            except (ValueError, AttributeError):
                # Fall back to string sorting
                items.sort(reverse=False)
            
            # Rearrange items in sorted positions
            for index, (val, item) in enumerate(items):
                self.inventory_tree.move(item, '', index)
                
        except Exception as e:
            print(f"Error sorting column: {e}")

    def create_statistics_panel(self):
        """Create a panel to display inventory statistics"""
        stats_frame = ttk.Frame(self.frame, style='Content.TFrame')
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Container for stat cards
        cards_container = ttk.Frame(stats_frame, style='Content.TFrame')
        cards_container.pack(fill='x')
        
        # Total Stock Card
        stock_card = ttk.Frame(cards_container, style='Card.TFrame', relief='raised', borderwidth=1)
        stock_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(stock_card, text="Total Stock Units", 
                 font=('Arial', 10), foreground='#666').pack(pady=(15, 5))
        self.total_stock_label = ttk.Label(stock_card, text="0", 
                                          font=('Arial', 24, 'bold'), foreground="#000000")
        self.total_stock_label.pack(pady=(0, 15))
        
        # Total Inventory Value Card
        value_card = ttk.Frame(cards_container, style='Card.TFrame', relief='raised', borderwidth=1)
        value_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(value_card, text="Total Inventory Value", 
                 font=('Arial', 10), foreground='#666').pack(pady=(15, 5))
        self.total_value_label = ttk.Label(value_card, text="₱0.00", 
                                          font=('Arial', 24, 'bold'), foreground="#000000")
        self.total_value_label.pack(pady=(0, 15))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_container, style='Card.TFrame', relief='raised', borderwidth=1)
        revenue_card.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(revenue_card, text="Total Revenue (Sales)", 
                 font=('Arial', 10), foreground='#666').pack(pady=(15, 5))
        self.total_revenue_label = ttk.Label(revenue_card, text="₱0.00", 
                                            font=('Arial', 24, 'bold'), foreground="#000000")
        self.total_revenue_label.pack(pady=(0, 15))
        
        # Total Products Card
        products_card = ttk.Frame(cards_container, style='Card.TFrame', relief='raised', borderwidth=1)
        products_card.pack(side='left', fill='both', expand=True)
        
        ttk.Label(products_card, text="Total Products", 
                 font=('Arial', 10), foreground='#666').pack(pady=(15, 5))
        self.total_products_label = ttk.Label(products_card, text="0", 
                                             font=('Arial', 24, 'bold'), foreground="#000000")
        self.total_products_label.pack(pady=(0, 15))

    def update_statistics(self, search_term=None, category_filter=None):
        """Update the statistics display based on current view (all products or filtered results)"""
        try:
            conditions = []
            params = []
            
            # Build WHERE clause based on filters
            if search_term and search_term.strip():
                search_pattern = f"%{search_term}%"
                conditions.append("(name LIKE ? OR product_id LIKE ?)")
                params.extend([search_pattern, search_pattern])
            
            if category_filter and category_filter != "All Categories":
                conditions.append("category = ?")
                params.append(category_filter)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Calculate total stock units
            self.main_app.cursor.execute(f'''
                SELECT SUM(stock) FROM products 
                WHERE {where_clause}
            ''', params)
            total_stock = self.main_app.cursor.fetchone()[0] or 0
            
            # Calculate total inventory value
            self.main_app.cursor.execute(f'''
                SELECT SUM(stock * price) FROM products 
                WHERE {where_clause}
            ''', params)
            total_value = self.main_app.cursor.fetchone()[0] or 0
            
            # Get product IDs for revenue calculation
            self.main_app.cursor.execute(f'''
                SELECT product_id FROM products 
                WHERE {where_clause}
            ''', params)
            filtered_product_ids = [row[0] for row in self.main_app.cursor.fetchall()]
            
            # Calculate total revenue
            if filtered_product_ids:
                placeholders = ','.join('?' * len(filtered_product_ids))
                self.main_app.cursor.execute(f'''
                    SELECT SUM(total) FROM sales 
                    WHERE quantity > 0 AND product_id IN ({placeholders})
                ''', filtered_product_ids)
                total_revenue = self.main_app.cursor.fetchone()[0] or 0
            else:
                total_revenue = 0
            
            # Count products
            self.main_app.cursor.execute(f'''
                SELECT COUNT(*) FROM products 
                WHERE {where_clause}
            ''', params)
            total_products = self.main_app.cursor.fetchone()[0] or 0
            
            # Update labels
            self.total_stock_label.config(text=f"{total_stock:,}")
            self.total_value_label.config(text=f"₱{total_value:,.2f}")
            self.total_revenue_label.config(text=f"₱{total_revenue:,.2f}")
            self.total_products_label.config(text=f"{total_products}")
            
            # Update status label
            if conditions:
                filter_text = []
                if search_term:
                    filter_text.append(f"Search: '{search_term}'")
                if category_filter and category_filter != "All Categories":
                    filter_text.append(f"Category: {category_filter}")
                self.status_label.config(text=f"Showing {total_products} products ({', '.join(filter_text)})")
            else:
                self.status_label.config(text=f"Showing all {total_products} products")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")

    def on_filter_change(self, event=None):
        """Handle category filter changes"""
        self.apply_filters()

    def on_search_change(self, *args):
        """Handle search input changes"""
        self.apply_filters()

    def apply_filters(self):
        """Apply both category filter and search"""
        search_term = self.search_var.get().strip()
        category_filter = self.category_filter_var.get()
        
        self.filter_products(search_term, category_filter)
        self.update_statistics(search_term, category_filter)

    def filter_products(self, search_term, category_filter):
        """Filter products by search term and/or category"""
        if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
            try:
                # Clear existing items
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                # Build query with filters
                conditions = []
                params = []
                
                if search_term:
                    search_pattern = f"%{search_term}%"
                    conditions.append("(name LIKE ? OR product_id LIKE ?)")
                    params.extend([search_pattern, search_pattern])
                
                if category_filter and category_filter != "All Categories":
                    conditions.append("category = ?")
                    params.append(category_filter)
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                query = f'''
                    SELECT id, name, price, stock, category, product_id 
                    FROM products 
                    WHERE {where_clause}
                    ORDER BY category, name
                '''
                
                self.main_app.cursor.execute(query, params)
                products = self.main_app.cursor.fetchall()
                
                # Insert filtered products into treeview
                for product in products:
                    self.inventory_tree.insert('', 'end', values=(
                        product[0],  # id (hidden)
                        product[5],  # product_id
                        product[1],  # name
                        product[4],  # category
                        f"₱{product[2]:.2f}",  # price
                        product[3]   # stock
                    ))
                
                print(f"Found {len(products)} products")
                
            except Exception as e:
                print(f"Error filtering products: {e}")
                messagebox.showerror("Error", f"Failed to filter products: {str(e)}")

    def clear_filters(self):
        """Clear all filters and show all products"""
        self.search_var.set("")
        self.category_filter_var.set("All Categories")
        self.refresh_products()

    def search_products(self, search_term):
        """Legacy method - redirects to filter_products"""
        category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else "All Categories"
        self.filter_products(search_term, category_filter)

    def add_stock(self):
        """Add stock to an existing product"""
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add stock to.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]  # Hidden ID column
        product_code = item['values'][1]  # Product ID
        product_name = item['values'][2]  # Name
        current_stock = item['values'][5]  # Stock
        
        # Create a simple dialog for stock addition
        stock_dialog = AddStockDialog(self.main_app.root, product_name, current_stock)
        if stock_dialog.result:
            try:
                quantity_to_add = stock_dialog.result['quantity']
                
                if quantity_to_add <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0!")
                    return
                
                # Get current stock from database to ensure accuracy
                self.main_app.cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
                current_db_stock = self.main_app.cursor.fetchone()[0]
                
                new_stock = current_db_stock + quantity_to_add
                
                # Update product stock
                self.main_app.cursor.execute('''
                    UPDATE products SET stock = ? WHERE id = ?
                ''', (new_stock, product_id))
                
                # Record stock movement
                self.main_app.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                            reference_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_code, product_name, 'IN', quantity_to_add, 
                      f"STOCK_ADD_{product_id}", f"Stock addition: {quantity_to_add} units added"))
                
                self.main_app.conn.commit()
                
                # Refresh display (respects current filters)
                self.apply_filters()
                
                # Refresh stock history if it's currently displayed
                self.refresh_stock_history_if_visible()
                    
                messagebox.showinfo("Success", 
                    f"Added {quantity_to_add} units to '{product_name}'\n"
                    f"Previous stock: {current_db_stock}\n"
                    f"New stock: {new_stock}")
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
                self.main_app.conn.rollback()
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def validate_product_data(self, product_data):
        """Validate product data before adding or updating"""
        try:
            # Validate name
            if not product_data.get('name') or not product_data['name'].strip():
                raise ValueError("Product name is required!")
                
            # Validate price
            try:
                price = float(product_data['price'])
                if price < 0:
                    raise ValueError("Price cannot be negative!")
            except (TypeError, ValueError):
                raise ValueError("Invalid price value!")
                
            # Validate stock
            try:
                stock = int(product_data['stock'])
                if stock < 0:
                    raise ValueError("Stock cannot be negative!")
            except (TypeError, ValueError):
                raise ValueError("Invalid stock value!")
                
            return True
                
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False

    def add_product(self):
        try:
            # Generate auto product ID
            auto_product_id = self.generate_product_id()
            
            dialog = ProductDialog(self.main_app.root, "Add Product", auto_product_id=auto_product_id)
            if dialog.result:
                # Validate the product data first
                if not self.validate_product_data(dialog.result):
                    return
                    
                print(f"Dialog result: {dialog.result}")  
                
                # Validate required fields
                if not dialog.result.get('name'):
                    messagebox.showerror("Error", "Product name is required!")
                    return
                    
                # Use the product_id from dialog (which should be the auto-generated one)
                product_id_input = dialog.result.get('product_id', auto_product_id).strip()
                
                # Double-check for duplicates (shouldn't happen with auto-generation, but safety check)
                self.main_app.cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', 
                                (product_id_input,))
                if self.main_app.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Product ID already exists! Please try again.")
                    return
                
                # Insert the new product
                self.main_app.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, product_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], 
                    float(dialog.result['price']), 
                    int(dialog.result['stock']),
                    dialog.result['category'], 
                    product_id_input))  
                
                # Record initial stock addition
                if int(dialog.result['stock']) > 0:
                    self.main_app.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                reference_id, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (product_id_input, dialog.result['name'], 'IN', 
                        int(dialog.result['stock']), 'INITIAL', 
                        'Initial stock when product was added to inventory'))
                
                self.main_app.conn.commit()
                messagebox.showinfo("Success", f"Product '{dialog.result['name']}' added successfully with ID: {product_id_input}")
                
                # Refresh inventory display (respects current filters)
                self.apply_filters()
                
                # Refresh stock history if it's currently displayed
                self.refresh_stock_history_if_visible()
                
        except sqlite3.IntegrityError as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Product ID already exists or constraint violation: {str(e)}")
        except sqlite3.Error as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            print(f"Exception in add_product: {e}") 

    def edit_product(self):
        """Edit the selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
            
        # Get the selected product
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]  # Hidden ID
        
        try:
            # Get the current product data for the dialog
            self.main_app.cursor.execute('''
                SELECT name, price, stock, category, product_id
                FROM products WHERE id = ?
            ''', (product_id,))
            
            product = self.main_app.cursor.fetchone()
            if not product:
                messagebox.showerror("Error", "Product not found in database!")
                return
                
            original_name = product[0]
            original_category = product[3]
            original_product_code = product[4]
            
            product_data = (product_id, product[0], product[1], product[2], product[3], product[4])
            
            # Open the product dialog for editing with the product_data tuple
            dialog = ProductDialog(self.frame.winfo_toplevel(), "Edit Product", product_data)
            
            if dialog.result:
                if original_product_code != dialog.result['product_id']:
                    # Check if new product ID already exists
                    self.main_app.cursor.execute('''
                        SELECT COUNT(*) FROM products WHERE product_id = ? AND id != ?
                    ''', (dialog.result['product_id'], product_id))
                    
                    if self.main_app.cursor.fetchone()[0] > 0:
                        messagebox.showerror("Error", "A product with this ID already exists!")
                        return
                
                try:
                    # Start a database transaction
                    self.main_app.cursor.execute("BEGIN TRANSACTION")
                    
                    # Update the product in the products table
                    self.main_app.cursor.execute('''
                        UPDATE products 
                        SET name = ?, price = ?, stock = ?, category = ?, product_id = ?
                        WHERE id = ?
                    ''', (dialog.result['name'], dialog.result['price'], 
                        dialog.result['stock'], dialog.result['category'], 
                        dialog.result['product_id'], product_id))
                    
                    print(f"Updated product in products table: {dialog.result['name']}")
                    
                    # Check if any attributes have changed that need to be synchronized
                    name_changed = original_name != dialog.result['name']
                    category_changed = original_category != dialog.result['category']
                    product_code_changed = original_product_code != dialog.result['product_id']
                    
                    if name_changed or category_changed or product_code_changed:
                        print(f"Changes detected: Name: {name_changed}, Category: {category_changed}, Product ID: {product_code_changed}")
                        
                        # First update stock_movements table
                        try:
                            if name_changed or category_changed:
                                self.main_app.cursor.execute('''
                                    UPDATE stock_movements 
                                    SET product_name = ?, category = ?
                                    WHERE product_id = ?
                                ''', (dialog.result['name'], dialog.result['category'], original_product_code))
                                
                                sm_rows = self.main_app.cursor.rowcount
                                print(f"Updated name/category for {sm_rows} rows in stock_movements table")
                            
                            if product_code_changed:
                                # Update product_id in stock_movements
                                self.main_app.cursor.execute('''
                                    UPDATE stock_movements 
                                    SET product_id = ?
                                    WHERE product_id = ?
                                ''', (dialog.result['product_id'], original_product_code))
                                
                                sm_id_rows = self.main_app.cursor.rowcount
                                print(f"Updated product_id for {sm_id_rows} rows in stock_movements table")
                        except Exception as e:
                            print(f"Error updating stock_movements: {e}")
                        
                        # Then update sales table
                        try:
                            if name_changed or category_changed:
                                # Update name and/or category in sales
                                self.main_app.cursor.execute('''
                                    UPDATE sales 
                                    SET product_name = ?, product_category = ?
                                    WHERE product_id = ?
                                ''', (dialog.result['name'], dialog.result['category'], original_product_code))
                                
                                sales_rows = self.main_app.cursor.rowcount
                                print(f"Updated name/category for {sales_rows} rows in sales table")
                            
                            if product_code_changed:
                                # Update product_id in sales
                                self.main_app.cursor.execute('''
                                    UPDATE sales 
                                    SET product_id = ?
                                    WHERE product_id = ?
                                ''', (dialog.result['product_id'], original_product_code))
                                
                                sales_id_rows = self.main_app.cursor.rowcount
                                print(f"Updated product_id for {sales_id_rows} rows in sales table")
                        except Exception as e:
                            print(f"Error updating sales: {e}")
                    
                    # Commit all the database changes
                    self.main_app.conn.commit()
                    print("Database transaction committed successfully")
                    
                    # Refresh the inventory display (respects current filters)
                    self.apply_filters()
                    
                    # Force refresh the stock history module if it's visible
                    try:
                        if hasattr(self.main_app, 'stock_history_module'):
                            stock_history = self.main_app.stock_history_module
                            if hasattr(stock_history, 'refresh_stock_history'):
                                stock_history.refresh_stock_history()
                                print("Stock history refreshed")
                            else:
                                print("stock_history_module does not have refresh_stock_history method")
                        else:
                            print("main_app does not have stock_history_module attribute")
                    except Exception as e:
                        print(f"Error refreshing stock history: {e}")
                    
                    # Show success message
                    messagebox.showinfo("Success", "Product updated successfully!")
                    
                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                    self.main_app.conn.rollback()
                    messagebox.showerror("Error", f"Failed to update product: {str(e)}")
                except Exception as e:
                    print(f"Unexpected error during update: {e}")
                    self.main_app.conn.rollback()
                    messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        except Exception as e:
            print(f"Error in edit_product: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def delete_product(self):
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]  # Hidden ID
        product_name = item['values'][2]  # Name
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            try:
                # First get the product_id for the sales deletion
                self.main_app.cursor.execute('SELECT product_id FROM products WHERE id = ?', (product_id,))
                product_code = self.main_app.cursor.fetchone()
                
                if product_code:
                    # Delete related sales records first
                    self.main_app.cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_code[0],))
                    # Delete related stock movements
                    self.main_app.cursor.execute('DELETE FROM stock_movements WHERE product_id = ?', (product_code[0],))
                    
                # Delete the product
                self.main_app.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.main_app.conn.commit()
                
                # Refresh display (respects current filters)
                self.apply_filters()
                
                # Refresh stock history if it's currently displayed
                self.refresh_stock_history_if_visible()
                    
                messagebox.showinfo("Success", "Product deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                self.main_app.conn.rollback()

    def refresh_products(self):
        """Refresh the inventory display"""
        if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
            try:
                # Clear existing items
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                # Get all products from database, ordered by category then name
                self.main_app.cursor.execute('''
                    SELECT id, name, price, stock, category, product_id 
                    FROM products 
                    ORDER BY category, name
                ''')
                products = self.main_app.cursor.fetchall()
                
                # Insert products into treeview
                for product in products:
                    self.inventory_tree.insert('', 'end', values=(
                        product[0],  # id (hidden)
                        product[5],  # product_id
                        product[1],  # name
                        product[4],  # category
                        f"₱{product[2]:.2f}",  # price
                        product[3]   # stock
                    ))
                    
                # Update statistics
                self.update_statistics()
                    
                print(f"Loaded {len(products)} products into inventory")
                
            except Exception as e:
                print(f"Error refreshing products: {e}")
                messagebox.showerror("Error", f"Failed to load products: {str(e)}")
        else:
            print("Inventory tree not available yet")  

    def refresh(self):
        """Refresh the inventory interface"""
        if self.frame:
            self.apply_filters()
            return self.frame
        return None

    def refresh_stock_history_if_visible(self):
        """Refresh stock history module if it exists and is visible"""
        try:
            # Check if main_app has a stock_history module
            if hasattr(self.main_app, 'stock_history_module'):
                stock_history = self.main_app.stock_history_module
                # Check if the stock history frame exists and is visible
                if hasattr(stock_history, 'frame') and stock_history.frame and stock_history.frame.winfo_exists():
                    if stock_history.frame.winfo_viewable():
                        stock_history.refresh_stock_history()
                        print("Stock history refreshed after inventory change")
        except Exception as e:
            print(f"Could not refresh stock history: {e}")


class StockHistoryDialog:
    """Dialog to display stock history for a specific product"""
    
    def __init__(self, parent, main_app, product_code, product_name, current_stock):
        self.main_app = main_app
        self.product_code = product_code
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Stock History - {product_name}")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#f0fdff')
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450)
        y = (self.dialog.winfo_screenheight() // 2) - (300)
        self.dialog.geometry(f"900x600+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20", style='Content.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text=f"📊 Stock History", 
                 style='PageTitle.TLabel').pack(side='left')
        
        # Product info
        info_frame = ttk.Frame(main_frame, style='Card.TFrame')
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Product: {product_name}", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', padx=20, pady=(15, 5))
        ttk.Label(info_frame, text=f"Product ID: {product_code}", 
                 font=('Arial', 10)).pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(info_frame, text=f"Current Stock: {current_stock} units", 
                 font=('Arial', 10, 'bold'), foreground='#00bcd4').pack(anchor='w', padx=20, pady=(0, 15))
        
        # History table
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create treeview
        columns = ('Date', 'Type', 'Quantity', 'Reference', 'Notes')
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                        style='Modern.Treeview', height=15)
        
        # Configure columns
        self.history_tree.heading('Date', text='Date & Time')
        self.history_tree.heading('Type', text='Type')
        self.history_tree.heading('Quantity', text='Quantity')
        self.history_tree.heading('Reference', text='Reference')
        self.history_tree.heading('Notes', text='Notes')
        
        self.history_tree.column('Date', width=180, anchor='center')
        self.history_tree.column('Type', width=80, anchor='center')
        self.history_tree.column('Quantity', width=100, anchor='center')
        self.history_tree.column('Reference', width=150, anchor='center')
        self.history_tree.column('Notes', width=300, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        scrollbar.pack(side='right', fill='y', pady=20)
        
        # Buttons
        button_frame = ttk.Frame(main_frame, style='Content.TFrame')
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy, 
                  style='Secondary.TButton').pack(side='right')
        
        # Load stock history
        self.load_stock_history()
        
        # Bind Escape key to close
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def load_stock_history(self):
        """Load stock history for the product"""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Get stock movements from database
            self.main_app.cursor.execute('''
                SELECT movement_date, movement_type, quantity, reference_id, notes
                FROM stock_movements
                WHERE product_id = ?
                ORDER BY movement_date DESC
            ''', (self.product_code,))
            
            movements = self.main_app.cursor.fetchall()
            
            # Insert movements into treeview
            for movement in movements:
                # Format date
                date_str = movement[0]
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%Y-%m-%d %I:%M %p')
                except:
                    formatted_date = date_str
                
                # Determine type display and quantity format
                movement_type = movement[1]
                quantity = movement[2]
                
                if movement_type == 'IN':
                    type_display = '📥 IN'
                    quantity_display = f"+{quantity}"
                    tags = ('in',)
                elif movement_type == 'OUT':
                    type_display = '📤 OUT'
                    quantity_display = f"-{quantity}"
                    tags = ('out',)
                else:
                    type_display = movement_type
                    quantity_display = str(quantity)
                    tags = ()
                
                self.history_tree.insert('', 'end', values=(
                    formatted_date,
                    type_display,
                    quantity_display,
                    movement[3] or '',  # reference_id
                    movement[4] or ''   # notes
                ), tags=tags)
            
            # Configure tag colors
            self.history_tree.tag_configure('in', foreground='#10b981')  # Green for IN
            self.history_tree.tag_configure('out', foreground='#ef4444')  # Red for OUT
            
            if not movements:
                # Show message if no history
                self.history_tree.insert('', 'end', values=(
                    'No stock history available',
                    '',
                    '',
                    '',
                    ''
                ))
            
        except Exception as e:
            print(f"Error loading stock history: {e}")
            messagebox.showerror("Error", f"Failed to load stock history: {str(e)}")


class AddStockDialog:
    """Simple dialog for adding stock to existing products"""
    
    def __init__(self, parent, product_name, current_stock):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Stock")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (220 // 2)
        self.dialog.geometry(f"350x220+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Product info
        ttk.Label(main_frame, text=f"Product: {product_name}", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Label(main_frame, text=f"Current Stock: {current_stock}", 
                 font=('Arial', 10)).pack(anchor='w', pady=(0, 20))
        
        # Quantity to add
        ttk.Label(main_frame, text="Quantity to Add:").pack(anchor='w', pady=(0, 5))
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(main_frame, textvariable=self.quantity_var, width=20)
        quantity_entry.pack(anchor='w', pady=(0, 20))
        quantity_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Add Stock", command=self.ok_clicked).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='right')
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        self.dialog.wait_window()
    
    def ok_clicked(self):
        try:
            quantity = int(self.quantity_var.get().strip())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0!")
                return
            
            self.result = {
                'quantity': quantity
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
    
    def cancel_clicked(self):
        self.dialog.destroy()