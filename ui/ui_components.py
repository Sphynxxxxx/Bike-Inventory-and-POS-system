import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
import uuid

class ProductDialog:
    def __init__(self, parent, title, product_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg='#ffffff')
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        self.create_widgets(product_data)
        
        # Focus on the first entry
        self.name_entry.focus_set()
        
        self.dialog.wait_window()

    def create_widgets(self, product_data):
        main_frame = ttk.Frame(self.dialog, padding="30", style='Content.TFrame')
        main_frame.pack(fill='both', expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Product Information", style='DialogTitle.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')

        # Product Name
        ttk.Label(main_frame, text="Product Name:", style='FieldLabel.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.name_var = tk.StringVar(value=product_data[1] if product_data else "")
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=35, style='Modern.TEntry')
        self.name_entry.grid(row=1, column=1, pady=8, sticky='ew')

        # Price
        ttk.Label(main_frame, text="Price (₱):", style='FieldLabel.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.price_var = tk.StringVar(value=str(product_data[2]) if product_data else "0.00")
        self.price_entry = ttk.Entry(main_frame, textvariable=self.price_var, width=35, style='Modern.TEntry')
        self.price_entry.grid(row=2, column=1, pady=8, sticky='ew')

        # Stock
        ttk.Label(main_frame, text="Stock Quantity:", style='FieldLabel.TLabel').grid(row=3, column=0, sticky='w', pady=8)
        self.stock_var = tk.StringVar(value=str(product_data[3]) if product_data else "0")
        self.stock_entry = ttk.Entry(main_frame, textvariable=self.stock_var, width=35, style='Modern.TEntry')
        self.stock_entry.grid(row=3, column=1, pady=8, sticky='ew')

        # Category
        ttk.Label(main_frame, text="Category:", style='FieldLabel.TLabel').grid(row=4, column=0, sticky='w', pady=8)
        self.category_var = tk.StringVar(value=product_data[4] if product_data else "Bikes")
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=33, style='Modern.TCombobox')
        self.category_combo['values'] = ('Bikes', 'Accessories', 'Parts', 'Clothing', 'Services')
        self.category_combo.state(['readonly'])
        self.category_combo.grid(row=4, column=1, pady=8, sticky='ew')

        # Product ID
        ttk.Label(main_frame, text="Product ID:", style='FieldLabel.TLabel').grid(row=5, column=0, sticky='w', pady=8)
        self.product_id_var = tk.StringVar(value=product_data[5] if product_data else "")
        self.product_id_entry = ttk.Entry(main_frame, textvariable=self.product_id_var, width=35, style='Modern.TEntry')
        self.product_id_entry.grid(row=5, column=1, pady=8, sticky='ew')

        # Configure column weights
        main_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(main_frame, style='Content.TFrame')
        button_frame.grid(row=6, column=0, columnspan=2, pady=30, sticky='ew')

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel, 
                               style='Secondary.TButton')
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = ttk.Button(button_frame, text="Save Product", command=self.save, 
                             style='Primary.TButton')
        save_btn.pack(side='right')
        
        # Bind Enter key to save
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())

    def save(self):
        try:
            # Get values and strip whitespace
            name = self.name_var.get().strip()
            price_str = self.price_var.get().strip()
            stock_str = self.stock_var.get().strip()
            category = self.category_var.get().strip()
            product_id = self.product_id_var.get().strip()

            # Validate required fields
            if not name:
                messagebox.showerror("Validation Error", "Product name is required!")
                self.name_entry.focus_set()
                return
                
            if not product_id:
                messagebox.showerror("Validation Error", "Product ID is required!")
                self.product_id_entry.focus_set()
                return

            # Validate and convert numeric fields
            try:
                price = float(price_str) if price_str else 0.0
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid price!")
                self.price_entry.focus_set()
                return

            try:
                stock = int(stock_str) if stock_str else 0
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid stock quantity!")
                self.stock_entry.focus_set()
                return

            # Validate ranges
            if price < 0:
                messagebox.showerror("Validation Error", "Price cannot be negative!")
                self.price_entry.focus_set()
                return
                
            if stock < 0:
                messagebox.showerror("Validation Error", "Stock cannot be negative!")
                self.stock_entry.focus_set()
                return

            # Set default category if not selected
            if not category:
                category = "Bikes"

            # Create result dictionary
            self.result = {
                'name': name,
                'price': price,
                'stock': stock,
                'category': category,
                'product_id': product_id
            }
            
            print(f"ProductDialog result: {self.result}")  # Debug print
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            print(f"Error in ProductDialog.save(): {e}")

    def cancel(self):
        self.result = None
        self.dialog.destroy()

class ModernSidebar(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, style='Sidebar.TFrame')
        self.main_app = main_app
        self.active_button = None
        self.create_sidebar()

    def create_sidebar(self):
        # Logo/Title section
        logo_frame = ttk.Frame(self, style='SidebarLogo.TFrame')
        logo_frame.pack(fill='x', pady=20, padx=20)

        # Bike shop icon (using text for now)
        icon_label = ttk.Label(logo_frame, text="🚲", font=('Arial', 24), style='Logo.TLabel')
        icon_label.pack()

        title_label = ttk.Label(logo_frame, text="Bike Shop Inventory", style='LogoTitle.TLabel')
        title_label.pack(pady=(5, 0))

        # Navigation buttons
        nav_frame = ttk.Frame(self, style='Sidebar.TFrame')
        nav_frame.pack(fill='x', pady=20, padx=15)

        # Dashboard button
        self.dashboard_btn = self.create_nav_button(nav_frame, "📊", "Dashboard", self.main_app.show_dashboard)
        
        # Sales Entry button
        self.sales_entry_btn = self.create_nav_button(nav_frame, "🛒", "Point of Sale", self.main_app.show_sales_entry)
        
        # Stock History button
        self.stock_history_btn = self.create_nav_button(nav_frame, "📈", "Stock History", self.main_app.show_stock_history)
        
        # Inventory button
        self.inventory_btn = self.create_nav_button(nav_frame, "📦", "Inventory", self.main_app.show_inventory)
        
        # Services button
        self.services_btn = self.create_nav_button(nav_frame, "🔧", "Services", self.main_app.show_services)

        # Logout button at bottom
        logout_frame = ttk.Frame(self, style='Sidebar.TFrame')
        logout_frame.pack(side='bottom', fill='x', pady=20, padx=15)

        logout_btn = ttk.Button(logout_frame, text="🚪 Logout", command=self.main_app.logout,
                               style='SidebarLogout.TButton')
        logout_btn.pack(fill='x')

        # Store button references
        self.nav_buttons = {
            'dashboard': self.dashboard_btn,
            'sales_entry': self.sales_entry_btn,
            'stock_history': self.stock_history_btn,
            'inventory': self.inventory_btn,
            'services': self.services_btn
        }

    def create_nav_button(self, parent, icon, text, command):
        btn_frame = ttk.Frame(parent, style='Sidebar.TFrame')
        btn_frame.pack(fill='x', pady=2)

        btn = ttk.Button(btn_frame, text=f"{icon} {text}", command=command,
                        style='SidebarNav.TButton')
        btn.pack(fill='x')
        return btn

    def set_active(self, button_name):
        """Set the active navigation button"""
        # Reset all buttons to normal style
        for btn in self.nav_buttons.values():
            btn.configure(style='SidebarNav.TButton')
        
        # Set active button style
        if button_name in self.nav_buttons:
            self.nav_buttons[button_name].configure(style='SidebarNavActive.TButton')
            self.active_button = button_name

class SalesEntryFrame(ttk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, style='Content.TFrame')
        self.main_app = main_app
        self.cart_items = []
        self.create_pos_interface()

    def create_pos_interface(self):
        # Header with breadcrumb
        header_frame = ttk.Frame(self, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)

        # Title
        title_label = ttk.Label(header_frame, text="Point of Sale (POS)", style='PageTitle.TLabel')
        title_label.pack(side='left')

        # Breadcrumb
        breadcrumb_frame = ttk.Frame(header_frame, style='Content.TFrame')
        breadcrumb_frame.pack(side='right')

        ttk.Label(breadcrumb_frame, text="Dashboard", style='Breadcrumb.TLabel').pack(side='left')
        ttk.Label(breadcrumb_frame, text=" / ", style='Breadcrumb.TLabel').pack(side='left')
        ttk.Label(breadcrumb_frame, text="Point of Sale", style='BreadcrumbActive.TLabel').pack(side='left')

        # Main content container
        content_container = ttk.Frame(self, style='Content.TFrame')
        content_container.pack(fill='both', expand=True, padx=30, pady=20)

        # Left side - Product Search and Selection
        left_frame = ttk.Frame(content_container, style='Card.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 20))

        # Product Search Section
        search_header = ttk.Frame(left_frame, style='Card.TFrame')
        search_header.pack(fill='x', padx=25, pady=20)

        ttk.Label(search_header, text="🔍", font=('Arial', 12), style='SectionIcon.TLabel').pack(side='left')
        ttk.Label(search_header, text="Product Search", style='SectionTitle.TLabel').pack(side='left', padx=(8, 0))

        # Search controls
        search_frame = ttk.Frame(left_frame, style='Card.TFrame')
        search_frame.pack(fill='x', padx=25, pady=(0, 15))

        # Search by category
        ttk.Label(search_frame, text="Filter by Category:", style='FieldLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.search_category_var = tk.StringVar()
        category_filter = ttk.Combobox(search_frame, textvariable=self.search_category_var, 
                                     style='Modern.TCombobox', state='readonly')
        category_filter['values'] = ('All Categories', 'Bikes', 'Accessories', 'Parts', 'Clothing', 'Services')
        category_filter.set('All Categories')
        category_filter.pack(fill='x', pady=(0, 10))
        category_filter.bind('<<ComboboxSelected>>', self.filter_products)

        # Search by name
        ttk.Label(search_frame, text="Search Product:", style='FieldLabel.TLabel').pack(anchor='w', pady=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style='Modern.TEntry')
        search_entry.pack(fill='x', pady=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_products)

        # Product list
        ttk.Label(left_frame, text="Available Products:", style='FieldLabel.TLabel').pack(anchor='w', padx=25, pady=(10, 5))
        
        products_frame = ttk.Frame(left_frame, style='Card.TFrame')
        products_frame.pack(fill='both', expand=True, padx=25, pady=(0, 25))

        # Create treeview for products
        product_columns = ('Name', 'Price', 'Stock', 'Category')
        self.products_tree = ttk.Treeview(products_frame, columns=product_columns, show='headings', 
                                         style='Modern.Treeview', height=12)

        for col in product_columns:
            self.products_tree.heading(col, text=col)
            if col == 'Name':
                self.products_tree.column(col, width=150)
            elif col == 'Price':
                self.products_tree.column(col, width=80)
            elif col == 'Stock':
                self.products_tree.column(col, width=60)
            else:
                self.products_tree.column(col, width=100)

        products_scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)

        self.products_tree.pack(side='left', fill='both', expand=True)
        products_scrollbar.pack(side='right', fill='y')

        # Add to cart button
        add_cart_btn = ttk.Button(left_frame, text="🛒 Add to Cart", command=self.add_to_cart,
                                 style='Primary.TButton')
        add_cart_btn.pack(fill='x', padx=25, pady=(0, 25))

        # Right side - Shopping Cart
        right_frame = ttk.Frame(content_container, style='Card.TFrame')
        right_frame.pack(side='right', fill='both', expand=True)

        # Cart Header
        cart_header = ttk.Frame(right_frame, style='Card.TFrame')
        cart_header.pack(fill='x', padx=25, pady=20)

        ttk.Label(cart_header, text="🛒", font=('Arial', 12), style='SectionIcon.TLabel').pack(side='left')
        ttk.Label(cart_header, text="Shopping Cart", style='SectionTitle.TLabel').pack(side='left', padx=(8, 0))

        # Cart table
        cart_table_frame = ttk.Frame(right_frame, style='Card.TFrame')
        cart_table_frame.pack(fill='both', expand=True, padx=25, pady=(0, 15))

        # Create cart treeview
        cart_columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_table_frame, columns=cart_columns, show='headings', 
                                     style='Modern.Treeview', height=10)

        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            if col == 'Product':
                self.cart_tree.column(col, width=120)
            elif col == 'Qty':
                self.cart_tree.column(col, width=50)
            elif col == 'Price':
                self.cart_tree.column(col, width=80)
            else:
                self.cart_tree.column(col, width=80)

        cart_scrollbar = ttk.Scrollbar(cart_table_frame, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)

        self.cart_tree.pack(side='left', fill='both', expand=True)
        cart_scrollbar.pack(side='right', fill='y')

        # Cart controls
        cart_controls = ttk.Frame(right_frame, style='Card.TFrame')
        cart_controls.pack(fill='x', padx=25, pady=(0, 15))

        ttk.Button(cart_controls, text="Remove Item", command=self.remove_from_cart,
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(cart_controls, text="Clear Cart", command=self.clear_cart,
                  style='Danger.TButton').pack(side='left')

        # Total section
        total_frame = ttk.Frame(right_frame, style='Card.TFrame')
        total_frame.pack(fill='x', padx=25, pady=(0, 15))

        self.total_var = tk.StringVar(value="₱0.00")
        ttk.Label(total_frame, text="Total Amount:", style='FieldLabel.TLabel').pack(side='left')
        ttk.Label(total_frame, textvariable=self.total_var, style='TotalAmount.TLabel').pack(side='right')

        # Payment method
        payment_frame = ttk.Frame(right_frame, style='Card.TFrame')
        payment_frame.pack(fill='x', padx=25, pady=(0, 15))

        ttk.Label(payment_frame, text="Payment Method:", style='FieldLabel.TLabel').pack(side='left')
        self.payment_var = tk.StringVar(value='Cash')
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_var,
                                   values=['Cash', 'Card', 'GCash', 'Bank Transfer'], 
                                   state='readonly', style='Modern.TCombobox', width=15)
        payment_combo.pack(side='right')

        # Checkout button
        checkout_btn = ttk.Button(right_frame, text="💳 Checkout", command=self.process_checkout,
                                 style='RecordSale.TButton')
        checkout_btn.pack(fill='x', padx=25, pady=(0, 25))

        # Load initial products
        self.load_all_products()

    def load_all_products(self):
        """Load all products into the products tree"""
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)

            cursor = self.main_app.cursor
            cursor.execute('''
                SELECT name, price, stock, category, product_id 
                FROM products 
                WHERE stock > 0 
                ORDER BY name
            ''')
            products = cursor.fetchall()

            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product[0],  # name
                    f"₱{product[1]:.2f}",  # price
                    product[2],  # stock
                    product[3]   # category
                ), tags=(product[4],))  # Store product_id in tags

        except Exception as e:
            print(f"Error loading products: {e}")

    def filter_products(self, event=None):
        """Filter products based on category and search term"""
        try:
            # Clear existing items
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)

            cursor = self.main_app.cursor
            category = self.search_category_var.get()
            search_term = self.search_var.get().lower()

            # Build query based on filters
            if category == 'All Categories':
                if search_term:
                    cursor.execute('''
                        SELECT name, price, stock, category, product_id 
                        FROM products 
                        WHERE stock > 0 AND LOWER(name) LIKE ?
                        ORDER BY name
                    ''', (f'%{search_term}%',))
                else:
                    cursor.execute('''
                        SELECT name, price, stock, category, product_id 
                        FROM products 
                        WHERE stock > 0 
                        ORDER BY name
                    ''')
            else:
                if search_term:
                    cursor.execute('''
                        SELECT name, price, stock, category, product_id 
                        FROM products 
                        WHERE stock > 0 AND category = ? AND LOWER(name) LIKE ?
                        ORDER BY name
                    ''', (category, f'%{search_term}%'))
                else:
                    cursor.execute('''
                        SELECT name, price, stock, category, product_id 
                        FROM products 
                        WHERE stock > 0 AND category = ?
                        ORDER BY name
                    ''', (category,))

            products = cursor.fetchall()

            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product[0],  # name
                    f"₱{product[1]:.2f}",  # price
                    product[2],  # stock
                    product[3]   # category
                ), tags=(product[4],))  # Store product_id in tags

        except Exception as e:
            print(f"Error filtering products: {e}")

    def add_to_cart(self):
        """Add selected product to cart"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add to cart.")
            return

        try:
            item = self.products_tree.item(selection[0])
            product_name = item['values'][0]
            product_price_str = item['values'][1].replace('₱', '').replace(',', '')
            product_price = float(product_price_str)
            available_stock = int(item['values'][2])
            product_category = item['values'][3]
            product_id = item['tags'][0]

            # Ask for quantity
            quantity = simpledialog.askinteger(
                "Quantity", 
                f"Enter quantity for {product_name}:\n(Available: {available_stock})",
                minvalue=1, 
                maxvalue=available_stock
            )

            if not quantity:
                return

            # Check if product already in cart
            for cart_item in self.cart_items:
                if cart_item['product_id'] == product_id:
                    # Update existing item
                    new_quantity = cart_item['quantity'] + quantity
                    if new_quantity > available_stock:
                        messagebox.showerror("Error", 
                                           f"Not enough stock! Available: {available_stock}, "
                                           f"Already in cart: {cart_item['quantity']}")
                        return
                    cart_item['quantity'] = new_quantity
                    cart_item['total'] = cart_item['quantity'] * cart_item['unit_price']
                    self.refresh_cart()
                    return

            # Add new item to cart
            cart_item = {
                'product_id': product_id,
                'product_name': product_name,  # Changed from 'name' to 'product_name'
                'unit_price': product_price,   # Changed from 'price' to 'unit_price'
                'quantity': quantity,
                'total': product_price * quantity,
                'category': product_category
            }

            self.cart_items.append(cart_item)
            self.refresh_cart()
            messagebox.showinfo("Success", f"Added {quantity} x {product_name} to cart!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product to cart: {str(e)}")

    def refresh_cart(self):
        """Refresh the cart display and total"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        # Add cart items
        total_amount = 0
        for item in self.cart_items:
            self.cart_tree.insert('', 'end', values=(
                item['product_name'],  # Changed from 'name'
                item['quantity'],
                f"₱{item['unit_price']:.2f}",  # Changed from 'price'
                f"₱{item['total']:.2f}"
            ))
            total_amount += item['total']

        # Update total
        self.total_var.set(f"₱{total_amount:.2f}")

    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove from cart.")
            return

        item_index = self.cart_tree.index(selection[0])
        removed_item = self.cart_items.pop(item_index)
        self.refresh_cart()
        messagebox.showinfo("Success", f"Removed {removed_item['product_name']} from cart!")

    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is already empty.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to clear the cart?"):
            self.cart_items.clear()
            self.refresh_cart()
            messagebox.showinfo("Success", "Cart cleared!")

    def process_checkout(self):
        """Process the checkout - FIXED VERSION"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty. Please add items before checkout.")
            return

        try:
            print("=== CHECKOUT DEBUG ===")
            print(f"Cart items: {self.cart_items}")
            
            # Validate transaction using the main app's method
            is_valid, error_msg = self.main_app.validate_transaction(self.cart_items)
            if not is_valid:
                messagebox.showerror("Validation Error", error_msg)
                return
            
            # Get payment method
            payment_method = self.payment_var.get()
            
            # CRITICAL FIX: Use the main app's record_sale method instead of direct DB manipulation
            success, result = self.main_app.record_sale(self.cart_items, payment_method)
            
            if success:
                transaction_id = result
                total_amount = sum(item['quantity'] * item['unit_price'] for item in self.cart_items)
                
                # Show success message
                messagebox.showinfo("Checkout Successful", 
                                  f"Transaction completed successfully!\n\n"
                                  f"Transaction ID: {transaction_id}\n"
                                  f"Total Amount: ₱{total_amount:.2f}\n"
                                  f"Payment Method: {payment_method}")
                
                # Clear cart and refresh displays
                self.cart_items.clear()
                self.refresh_cart()
                self.load_all_products()  # Refresh to show updated stock
                
                # Refresh inventory display if it's currently visible
                if hasattr(self.main_app, 'inventory_frame') and self.main_app.inventory_frame:
                    if self.main_app.inventory_frame.winfo_viewable():
                        self.main_app.refresh_products()
                
                print(f"Checkout successful! Transaction ID: {transaction_id}")
                
            else:
                # Show error message
                messagebox.showerror("Checkout Failed", f"Transaction failed: {result}")
                print(f"Checkout failed: {result}")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error during checkout: {str(e)}")
            print(f"Checkout exception: {e}")

    def refresh_recent_sales(self):
        """This method is kept for compatibility but not used in POS interface"""
        pass

def create_styles():
    """Create modern styles for the application"""
    style = ttk.Style()
    style.theme_use('clam')

    # Color scheme
    colors = {
        'bg': '#f8fafc',
        'sidebar_bg': '#1e293b',
        'sidebar_text': '#e2e8f0',
        'sidebar_active': '#3b82f6',
        'card_bg': '#ffffff',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b',
        'border': '#e2e8f0',
        'primary': '#3b82f6',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444'
    }

    # Configure root
    style.configure('.', background=colors['bg'])

    # Content frame styles
    style.configure('Content.TFrame', background=colors['bg'])
    style.configure('Card.TFrame', background=colors['card_bg'], relief='solid', borderwidth=1)

    # Sidebar styles
    style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
    style.configure('SidebarLogo.TFrame', background=colors['sidebar_bg'])
    
    # Logo styles
    style.configure('Logo.TLabel', background=colors['sidebar_bg'], foreground=colors['sidebar_text'])
    style.configure('LogoTitle.TLabel', background=colors['sidebar_bg'], foreground=colors['sidebar_text'],
                   font=('Helvetica', 11, 'bold'))

    # Navigation button styles
    style.configure('SidebarNav.TButton', 
                   background=colors['sidebar_bg'],
                   foreground=colors['sidebar_text'],
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10),
                   anchor='w',
                   padding=(15, 12))
    
    style.map('SidebarNav.TButton',
             background=[('active', '#334155'), ('pressed', '#334155')])

    style.configure('SidebarNavActive.TButton',
                   background=colors['sidebar_active'],
                   foreground='white',
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10, 'bold'),
                   anchor='w',
                   padding=(15, 12))

    style.configure('SidebarLogout.TButton',
                   background='#7f1d1d',
                   foreground=colors['sidebar_text'],
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10),
                   padding=(15, 12))

    # Page title styles
    style.configure('PageTitle.TLabel', 
                   background=colors['bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 24, 'bold'))

    # Breadcrumb styles
    style.configure('Breadcrumb.TLabel',
                   background=colors['bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 10))
    
    style.configure('BreadcrumbActive.TLabel',
                   background=colors['bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 10, 'bold'))

    # Section styles
    style.configure('SectionTitle.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 16, 'bold'))

    style.configure('SectionIcon.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'])

    # Field label styles
    style.configure('FieldLabel.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 10, 'bold'))

    # Entry and combobox styles
    style.configure('Modern.TEntry',
                   fieldbackground=colors['card_bg'],
                   foreground=colors['text_primary'],
                   bordercolor=colors['border'],
                   borderwidth=1,
                   relief='solid',
                   padding=12)

    style.configure('Modern.TCombobox',
                   fieldbackground=colors['card_bg'],
                   foreground=colors['text_primary'],
                   bordercolor=colors['border'],
                   borderwidth=1,
                   relief='solid',
                   padding=12,
                   arrowsize=12)

    # Button styles
    style.configure('Primary.TButton',
                   background=colors['primary'],
                   foreground='white',
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10, 'bold'),
                   padding=(20, 12))
    
    style.map('Primary.TButton',
             background=[('active', '#2563eb'), ('pressed', '#1d4ed8')])

    style.configure('Secondary.TButton',
                   background=colors['border'],
                   foreground=colors['text_primary'],
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10),
                   padding=(20, 12))

    style.configure('Danger.TButton',
                   background=colors['danger'],
                   foreground='white',
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 10, 'bold'),
                   padding=(20, 12))

    style.configure('RecordSale.TButton',
                   background='#1f2937',
                   foreground='white',
                   borderwidth=0,
                   relief='flat',
                   font=('Helvetica', 12, 'bold'),
                   padding=(20, 15))

    # Treeview styles
    style.configure('Modern.Treeview',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   fieldbackground=colors['card_bg'],
                   borderwidth=0,
                   rowheight=35,
                   font=('Helvetica', 9))

    style.configure('Modern.Treeview.Heading',
                   background=colors['bg'],
                   foreground=colors['text_secondary'],
                   relief='flat',
                   font=('Helvetica', 9, 'bold'),
                   borderwidth=0)

    # Total amount style
    style.configure('TotalAmount.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 18, 'bold'))

    # Validation note style
    style.configure('ValidationNote.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 8))

    # Dialog styles
    style.configure('DialogTitle.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 16, 'bold'))

    # Stats card styles
    style.configure('CardTitle.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 10))

    style.configure('CardValue.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 20, 'bold'))

    # Placeholder style
    style.configure('Placeholder.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 12))

    # Dashboard specific styles
    style.configure('Dashboard.Treeview',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   fieldbackground=colors['card_bg'],
                   borderwidth=0,
                   rowheight=25,
                   font=('Helvetica', 8))

    style.configure('Dashboard.Treeview.Heading',
                   background=colors['bg'],
                   foreground=colors['text_secondary'],
                   relief='flat',
                   font=('Helvetica', 8, 'bold'),
                   borderwidth=0)

    # Header styles
    style.configure('Header.TFrame', background=colors['bg'])

    # Insight styles
    style.configure('InsightTitle.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 9, 'bold'))

    style.configure('InsightValue.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_primary'],
                   font=('Helvetica', 14, 'bold'))

    # View more style
    style.configure('ViewMore.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['primary'],
                   font=('Helvetica', 9),
                   cursor='hand2')

    # No data style
    style.configure('NoData.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'],
                   font=('Helvetica', 10))

    # Card icon style
    style.configure('CardIcon.TLabel',
                   background=colors['card_bg'],
                   foreground=colors['text_secondary'])