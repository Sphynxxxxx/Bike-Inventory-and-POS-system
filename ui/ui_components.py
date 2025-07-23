import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
import uuid
import sys
import io

# Fix Unicode console output on Windows
try:
    if sys.platform.startswith('win'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
except Exception as e:
    print(f"Warning: Could not set UTF-8 encoding: {e}")

class CustomerQuantityDialog:
    def __init__(self, parent, product_name, available_stock):
        self.result = None
        try:
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Add to Cart")
            self.dialog.geometry("400x300")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.configure(bg='#ffffff')
            
            # Center the dialog
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (200)
            y = (self.dialog.winfo_screenheight() // 2) - (150)
            self.dialog.geometry(f"400x300+{x}+{y}")
            
            self.product_name = product_name
            self.available_stock = available_stock
            self.create_widgets()
            
            # Focus on the customer name entry
            self.customer_entry.focus_set()
            
            self.dialog.wait_window()
        except Exception as e:
            print(f"Error creating CustomerQuantityDialog: {e}")
            messagebox.showerror("Error", f"Failed to create dialog: {str(e)}")

    def create_widgets(self):
        try:
            main_frame = ttk.Frame(self.dialog, padding="30", style='Content.TFrame')
            main_frame.pack(fill='both', expand=True)

            # Title
            title_label = ttk.Label(main_frame, text="Add Product to Cart", 
                                   style='DialogTitle.TLabel')
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')

            # Product info
            product_info = ttk.Label(main_frame, 
                                    text=f"Product: {self.product_name}\nAvailable Stock: {self.available_stock}",
                                    style='FieldLabel.TLabel')
            product_info.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky='w')

            # Customer Name
            ttk.Label(main_frame, text="Customer Name:", style='FieldLabel.TLabel').grid(
                row=2, column=0, sticky='w', pady=8)
            self.customer_var = tk.StringVar()
            self.customer_entry = ttk.Entry(main_frame, textvariable=self.customer_var, 
                                           width=35, style='Modern.TEntry')
            self.customer_entry.grid(row=2, column=1, pady=8, sticky='ew')

            # Quantity
            ttk.Label(main_frame, text="Quantity:", style='FieldLabel.TLabel').grid(
                row=3, column=0, sticky='w', pady=8)
            self.quantity_var = tk.StringVar(value="1")
            self.quantity_entry = ttk.Entry(main_frame, textvariable=self.quantity_var, 
                                           width=35, style='Modern.TEntry')
            self.quantity_entry.grid(row=3, column=1, pady=8, sticky='ew')

            # Validation note
            note_label = ttk.Label(main_frame, 
                                  text=f"Enter quantity (1 to {self.available_stock})",
                                  style='ValidationNote.TLabel')
            note_label.grid(row=4, column=0, columnspan=2, pady=(5, 20), sticky='w')

            # Configure column weights
            main_frame.columnconfigure(1, weight=1)

            # Buttons
            button_frame = ttk.Frame(main_frame, style='Content.TFrame')
            button_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky='ew')

            cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel, 
                                   style='Secondary.TButton')
            cancel_btn.pack(side='right', padx=(10, 0))
            
            add_btn = ttk.Button(button_frame, text="Add to Cart", command=self.add_to_cart, 
                                style='Primary.TButton')
            add_btn.pack(side='right')
            
            # Bind Enter key to add
            self.dialog.bind('<Return>', lambda e: self.add_to_cart())
            self.dialog.bind('<Escape>', lambda e: self.cancel())
        except Exception as e:
            print(f"Error creating widgets in CustomerQuantityDialog: {e}")

    def add_to_cart(self):
        try:
            # Get values and strip whitespace
            customer_name = self.customer_var.get().strip()
            quantity_str = self.quantity_var.get().strip()

            # Validate customer name
            if not customer_name:
                messagebox.showerror("Validation Error", "Customer name is required!")
                self.customer_entry.focus_set()
                return

            # Validate and convert quantity
            try:
                quantity = int(quantity_str)
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid quantity!")
                self.quantity_entry.focus_set()
                return

            # Validate quantity range
            if quantity <= 0:
                messagebox.showerror("Validation Error", "Quantity must be greater than 0!")
                self.quantity_entry.focus_set()
                return
                
            if quantity > self.available_stock:
                messagebox.showerror("Validation Error", 
                                   f"Quantity cannot exceed available stock ({self.available_stock})!")
                self.quantity_entry.focus_set()
                return

            # Create result dictionary
            self.result = {
                'customer_name': customer_name,
                'quantity': quantity
            }
            
            print(f"CustomerQuantityDialog result: {self.result}")  # Debug print
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            print(f"Error in CustomerQuantityDialog.add_to_cart(): {e}")

    def cancel(self):
        try:
            self.result = None
            self.dialog.destroy()
        except Exception as e:
            print(f"Error in CustomerQuantityDialog.cancel(): {e}")

class ProductDialog:
    def __init__(self, parent, title, product_data=None):
        self.result = None
        try:
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
        except Exception as e:
            print(f"Error creating ProductDialog: {e}")
            messagebox.showerror("Error", f"Failed to create product dialog: {str(e)}")

    def create_widgets(self, product_data):
        try:
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
        except Exception as e:
            print(f"Error creating widgets in ProductDialog: {e}")

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
        try:
            self.result = None
            self.dialog.destroy()
        except Exception as e:
            print(f"Error in ProductDialog.cancel(): {e}")

class ModernSidebar(ttk.Frame):
    def __init__(self, parent, main_app):
        try:
            super().__init__(parent, style='Sidebar.TFrame')
            self.main_app = main_app
            self.active_button = None
            self.create_sidebar()
        except Exception as e:
            print(f"Error creating ModernSidebar: {e}")

    def create_sidebar(self):
        try:
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
            
            # Statistics button
            self.statistics_btn = self.create_nav_button(nav_frame, "📈", "Statistics", self.main_app.show_statistics)
            
            # Stock History button
            self.stock_history_btn = self.create_nav_button(nav_frame, "📋", "Stock History", self.main_app.show_stock_history)
            
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
                'statistics': self.statistics_btn,
                'stock_history': self.stock_history_btn,
                'inventory': self.inventory_btn,
                'services': self.services_btn
            }
        except Exception as e:
            print(f"Error in create_sidebar: {e}")

    def create_nav_button(self, parent, icon, text, command):
        try:
            btn_frame = ttk.Frame(parent, style='Sidebar.TFrame')
            btn_frame.pack(fill='x', pady=2)

            btn = ttk.Button(btn_frame, text=f"{icon} {text}", command=command,
                            style='SidebarNav.TButton')
            btn.pack(fill='x')
            return btn
        except Exception as e:
            print(f"Error creating nav button: {e}")
            return None

    def set_active(self, button_name):
        """Set the active navigation button"""
        try:
            # Reset all buttons to normal style
            for btn in self.nav_buttons.values():
                if btn:  # Check if button exists
                    btn.configure(style='SidebarNav.TButton')
            
            # Set active button style
            if button_name in self.nav_buttons and self.nav_buttons[button_name]:
                self.nav_buttons[button_name].configure(style='SidebarNavActive.TButton')
                self.active_button = button_name
        except Exception as e:
            print(f"Error setting active button: {e}")

class SalesEntryFrame(ttk.Frame):
    def __init__(self, parent, main_app):
        try:
            super().__init__(parent, style='Content.TFrame')
            self.main_app = main_app
            self.cart_items = []
            self.products_data = {}  # Store complete product data
            self.create_pos_interface()
        except Exception as e:
            print(f"Error creating SalesEntryFrame: {e}")

    def create_pos_interface(self):
        try:
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
            product_columns = ('Product ID', 'Name', 'Price', 'Stock', 'Category')
            self.products_tree = ttk.Treeview(products_frame, columns=product_columns, show='headings', 
                                             style='Modern.Treeview', height=12)

            # Configure columns
            self.products_tree.heading('Product ID', text='Product ID')
            self.products_tree.heading('Name', text='Name')
            self.products_tree.heading('Price', text='Price')
            self.products_tree.heading('Stock', text='Stock')
            self.products_tree.heading('Category', text='Category')
            
            self.products_tree.column('Product ID', width=100)
            self.products_tree.column('Name', width=150)
            self.products_tree.column('Price', width=80)
            self.products_tree.column('Stock', width=60)
            self.products_tree.column('Category', width=100)

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

            # Create cart treeview - Added Customer column
            cart_columns = ('Product ID', 'Product', 'Customer', 'Qty', 'Price', 'Total')
            self.cart_tree = ttk.Treeview(cart_table_frame, columns=cart_columns, show='headings', 
                                         style='Modern.Treeview', height=10)

            self.cart_tree.heading('Product ID', text='ID')
            self.cart_tree.heading('Product', text='Product')
            self.cart_tree.heading('Customer', text='Customer')
            self.cart_tree.heading('Qty', text='Qty')
            self.cart_tree.heading('Price', text='Price')
            self.cart_tree.heading('Total', text='Total')
            
            self.cart_tree.column('Product ID', width=70)
            self.cart_tree.column('Product', width=100)
            self.cart_tree.column('Customer', width=100)
            self.cart_tree.column('Qty', width=40)
            self.cart_tree.column('Price', width=70)
            self.cart_tree.column('Total', width=70)

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
            
        except Exception as e:
            print(f"Error creating POS interface: {e}")
            import traceback
            traceback.print_exc()

    # Add placeholder methods to prevent errors
    def load_all_products(self):
        print("Loading products...")
        # This will be implemented by the actual POS module
        pass
        
    def filter_products(self, event=None):
        print("Filtering products...")
        # This will be implemented by the actual POS module
        pass
    
    def add_to_cart(self):
        print("Adding to cart...")
        # This will be implemented by the actual POS module
        pass
    
    def remove_from_cart(self):
        print("Removing from cart...")
        # This will be implemented by the actual POS module
        pass
    
    def clear_cart(self):
        print("Clearing cart...")
        # This will be implemented by the actual POS module
        pass
    
    def process_checkout(self):
        print("Processing checkout...")
        # This will be implemented by the actual POS module
        pass

def create_styles():
    """Create modern styles for the application with better error handling"""
    try:
        style = ttk.Style()
        
        # Try to use clam theme, fall back to default if not available
        try:
            style.theme_use('clam')
        except tk.TclError:
            print("Warning: 'clam' theme not available, using default theme")
            try:
                style.theme_use('alt')
            except tk.TclError:
                print("Warning: 'alt' theme not available, using system default")

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
        try:
            style.configure('.', background=colors['bg'])
        except tk.TclError as e:
            print(f"Warning: Could not configure root style: {e}")

        # Content frame styles
        try:
            style.configure('Content.TFrame', background=colors['bg'])
            style.configure('Card.TFrame', background=colors['card_bg'], relief='solid', borderwidth=1)
        except tk.TclError as e:
            print(f"Warning: Could not configure frame styles: {e}")

        # Sidebar styles
        try:
            style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
            style.configure('SidebarLogo.TFrame', background=colors['sidebar_bg'])
        except tk.TclError as e:
            print(f"Warning: Could not configure sidebar styles: {e}")
        
        # Logo styles
        try:
            style.configure('Logo.TLabel', background=colors['sidebar_bg'], foreground=colors['sidebar_text'])
            style.configure('LogoTitle.TLabel', background=colors['sidebar_bg'], foreground=colors['sidebar_text'],
                           font=('Helvetica', 11, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure logo styles: {e}")

        # Navigation button styles
        try:
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
        except tk.TclError as e:
            print(f"Warning: Could not configure navigation button styles: {e}")

        # Page title styles
        try:
            style.configure('PageTitle.TLabel', 
                           background=colors['bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 24, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure page title styles: {e}")

        # Breadcrumb styles
        try:
            style.configure('Breadcrumb.TLabel',
                           background=colors['bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 10))
            
            style.configure('BreadcrumbActive.TLabel',
                           background=colors['bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 10, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure breadcrumb styles: {e}")

        # Section styles
        try:
            style.configure('SectionTitle.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 16, 'bold'))

            style.configure('SectionIcon.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'])
        except tk.TclError as e:
            print(f"Warning: Could not configure section styles: {e}")

        # Field label styles
        try:
            style.configure('FieldLabel.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 10, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure field label styles: {e}")

        # Entry and combobox styles
        try:
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
        except tk.TclError as e:
            print(f"Warning: Could not configure entry/combobox styles: {e}")

        # Button styles
        try:
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

            style.configure('Success.TButton',
                           background=colors['success'],
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
        except tk.TclError as e:
            print(f"Warning: Could not configure button styles: {e}")

        # Treeview styles
        try:
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
        except tk.TclError as e:
            print(f"Warning: Could not configure treeview styles: {e}")

        # Additional label styles
        try:
            style.configure('TotalAmount.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 18, 'bold'))

            style.configure('ValidationNote.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 8))

            style.configure('DialogTitle.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 16, 'bold'))

            style.configure('CardTitle.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 10))

            style.configure('CardValue.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 20, 'bold'))

            style.configure('CardIcon.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'])

            style.configure('Placeholder.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 12))
        except tk.TclError as e:
            print(f"Warning: Could not configure additional label styles: {e}")

        # Dashboard specific styles
        try:
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
        except tk.TclError as e:
            print(f"Warning: Could not configure dashboard styles: {e}")

        # Header styles
        try:
            style.configure('Header.TFrame', background=colors['bg'])
        except tk.TclError as e:
            print(f"Warning: Could not configure header styles: {e}")

        # Insight styles
        try:
            style.configure('InsightTitle.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 9, 'bold'))

            style.configure('InsightValue.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 14, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure insight styles: {e}")

        # View more style
        try:
            style.configure('ViewMore.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['primary'],
                           font=('Helvetica', 9),
                           cursor='hand2')
        except tk.TclError as e:
            print(f"Warning: Could not configure view more styles: {e}")

        # No data style
        try:
            style.configure('NoData.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 10))
        except tk.TclError as e:
            print(f"Warning: Could not configure no data styles: {e}")

        print("Styles created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating styles: {e}")
        import traceback
        traceback.print_exc()
        return False