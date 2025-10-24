import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
import uuid
import sys
import io

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
            self.dialog.geometry("450x550")  # Increased height for all fields
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.configure(bg='#ffffff')
            
            # Center the dialog
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
            self.dialog.geometry(f"450x550+{x}+{y}")
            
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

            # Stock Quantity - FIXED: Added the missing stock field
            ttk.Label(main_frame, text="Stock Quantity:", style='FieldLabel.TLabel').grid(row=3, column=0, sticky='w', pady=8)
            self.stock_var = tk.StringVar(value=str(product_data[3]) if product_data else "0")
            self.stock_entry = ttk.Entry(main_frame, textvariable=self.stock_var, width=35, style='Modern.TEntry')
            self.stock_entry.grid(row=3, column=1, pady=8, sticky='ew')

            # Category
            ttk.Label(main_frame, text="Category:", style='FieldLabel.TLabel').grid(row=4, column=0, sticky='w', pady=8)
            self.category_var = tk.StringVar(value=product_data[4] if product_data else "Bikes")
            self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=33, style='Modern.TCombobox')
            self.category_combo['values'] = ('Bikes', 'Accessories', 'Parts', 'Clothing', 'Maintenance')
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
            button_frame.grid(row=6, column=0, columnspan=2, pady=(30, 15), sticky='ew')

            # Action buttons
            cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel, 
                                   style='Secondary.TButton', width=15)
            cancel_btn.pack(side='right', padx=(10, 20))
            
            save_btn = ttk.Button(button_frame, text="Save Product", command=self.save, 
                                 style='Primary.TButton', width=15)
            save_btn.pack(side='right', padx=(10, 0))
            
            # Bind keys
            self.dialog.bind('<Return>', lambda e: self.save())
            self.dialog.bind('<KP_Enter>', lambda e: self.save())
            self.dialog.bind('<Escape>', lambda e: self.cancel())
            
            # Bind Tab key to move between fields and Enter to save
            for widget in [self.name_entry, self.price_entry, self.stock_entry, 
                         self.category_combo, self.product_id_entry]:
                widget.bind('<Return>', lambda e: self.save())
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

class SalesFrame(ttk.Frame):
    def __init__(self, parent, main_app):
        try:
            super().__init__(parent, style='Content.TFrame')
            self.main_app = main_app
            self.create_sales_interface()
        except Exception as e:
            print(f"Error creating SalesFrame: {e}")

    def create_sales_interface(self):
        try:
            # Header with breadcrumb
            header_frame = ttk.Frame(self, style='Content.TFrame')
            header_frame.pack(fill='x', padx=30, pady=20)

            # Title
            title_label = ttk.Label(header_frame, text="Sales Records", style='PageTitle.TLabel')
            title_label.pack(side='left')

            # Breadcrumb
            breadcrumb_frame = ttk.Frame(header_frame, style='Content.TFrame')
            breadcrumb_frame.pack(side='right')

            ttk.Label(breadcrumb_frame, text="Dashboard", style='Breadcrumb.TLabel').pack(side='left')
            ttk.Label(breadcrumb_frame, text=" / ", style='Breadcrumb.TLabel').pack(side='left')
            ttk.Label(breadcrumb_frame, text="Sales", style='BreadcrumbActive.TLabel').pack(side='left')

            # Controls frame
            controls_frame = ttk.Frame(self, style='Content.TFrame')
            controls_frame.pack(fill='x', padx=30, pady=(0, 20))

            # Date filter
            filter_frame = ttk.Frame(controls_frame, style='Card.TFrame')
            filter_frame.pack(side='left', fill='x', expand=True, padx=(0, 20))

            ttk.Label(filter_frame, text="Filter by Date:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=15)
            
            self.date_filter_var = tk.StringVar(value="All Time")
            date_combo = ttk.Combobox(filter_frame, textvariable=self.date_filter_var,
                                    values=['Today', 'This Week', 'This Month', 'This Year', 'All Time'],
                                    state='readonly', style='Modern.TCombobox', width=15)
            date_combo.pack(side='left', padx=(0, 10), pady=15)
            date_combo.bind('<<ComboboxSelected>>', self.filter_sales)

            # Search
            search_frame = ttk.Frame(controls_frame, style='Card.TFrame')
            search_frame.pack(side='right', fill='x')

            ttk.Label(search_frame, text="Search:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=15)
            self.search_var = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style='Modern.TEntry', width=30)
            search_entry.pack(side='left', padx=(0, 15), pady=15)
            search_entry.bind('<KeyRelease>', self.search_sales)

            # Export button
            export_btn = ttk.Button(controls_frame, text="📊 Export Report", 
                                   command=self.export_sales_report, style='Secondary.TButton')
            export_btn.pack(side='right', padx=(10, 0), pady=15)

            # Main content
            content_frame = ttk.Frame(self, style='Content.TFrame')
            content_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))

            # Sales summary cards
            summary_frame = ttk.Frame(content_frame, style='Content.TFrame')
            summary_frame.pack(fill='x', pady=(0, 20))

            # Total Sales Card
            total_sales_card = ttk.Frame(summary_frame, style='Card.TFrame')
            total_sales_card.pack(side='left', fill='x', expand=True, padx=(0, 15))

            ttk.Label(total_sales_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
            ttk.Label(total_sales_card, text="Total Sales", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
            self.total_sales_var = tk.StringVar(value="₱0.00")
            ttk.Label(total_sales_card, textvariable=self.total_sales_var, style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))

            # Total Transactions Card
            transactions_card = ttk.Frame(summary_frame, style='Card.TFrame')
            transactions_card.pack(side='left', fill='x', expand=True, padx=(0, 15))

            ttk.Label(transactions_card, text="📈", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
            ttk.Label(transactions_card, text="Total Transactions", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
            self.transactions_var = tk.StringVar(value="0")
            ttk.Label(transactions_card, textvariable=self.transactions_var, style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))

            # Average Sale Card
            avg_sale_card = ttk.Frame(summary_frame, style='Card.TFrame')
            avg_sale_card.pack(side='left', fill='x', expand=True)

            ttk.Label(avg_sale_card, text="📊", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
            ttk.Label(avg_sale_card, text="Average Sale", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
            self.avg_sale_var = tk.StringVar(value="₱0.00")
            ttk.Label(avg_sale_card, textvariable=self.avg_sale_var, style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))

            # Sales table
            table_frame = ttk.Frame(content_frame, style='Card.TFrame')
            table_frame.pack(fill='both', expand=True, padx=0, pady=0)

            # Create sales treeview
            sales_columns = ('Sale ID', 'Date', 'Customer', 'Product', 'Quantity', 'Unit Price', 'Total', 'Payment Method')
            self.sales_tree = ttk.Treeview(table_frame, columns=sales_columns, show='headings', 
                                          style='Modern.Treeview', height=15)

            # Configure columns
            column_widths = {
                'Sale ID': 80,
                'Date': 120,
                'Customer': 120,
                'Product': 150,
                'Quantity': 80,
                'Unit Price': 100,
                'Total': 100,
                'Payment Method': 120
            }

            for col in sales_columns:
                self.sales_tree.heading(col, text=col)
                self.sales_tree.column(col, width=column_widths.get(col, 100))

            # Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.sales_tree.yview)
            self.sales_tree.configure(yscrollcommand=scrollbar.set)

            self.sales_tree.pack(side='left', fill='both', expand=True, padx=20, pady=20)
            scrollbar.pack(side='right', fill='y', pady=20)

            # Load initial data
            self.load_sales_data()
            
        except Exception as e:
            print(f"Error creating sales interface: {e}")
            import traceback
            traceback.print_exc()

    def load_sales_data(self):
        """Load sales data from database"""
        try:
            # Clear existing data
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            # Connect to database
            conn = sqlite3.connect('bike_shop.db')
            cursor = conn.cursor()

            # Get sales data
            cursor.execute('''
                SELECT sale_id, sale_date, customer_name, product_name, quantity, 
                       unit_price, total_amount, payment_method 
                FROM sales 
                ORDER BY sale_date DESC
            ''')
            sales_data = cursor.fetchall()

            # Insert data into treeview
            total_sales = 0
            transaction_count = 0
            
            for sale in sales_data:
                self.sales_tree.insert('', 'end', values=sale)
                total_sales += sale[6]  # total_amount
                transaction_count += 1

            # Update summary cards
            self.total_sales_var.set(f"₱{total_sales:,.2f}")
            self.transactions_var.set(f"{transaction_count}")
            
            if transaction_count > 0:
                avg_sale = total_sales / transaction_count
                self.avg_sale_var.set(f"₱{avg_sale:,.2f}")
            else:
                self.avg_sale_var.set("₱0.00")

            conn.close()
            
        except Exception as e:
            print(f"Error loading sales data: {e}")
            messagebox.showerror("Database Error", f"Failed to load sales data: {str(e)}")

    def filter_sales(self, event=None):
        """Filter sales by date range"""
        try:
            # This would implement date filtering logic
            # For now, just reload all data
            self.load_sales_data()
        except Exception as e:
            print(f"Error filtering sales: {e}")

    def search_sales(self, event=None):
        """Search sales by customer or product name"""
        try:
            search_term = self.search_var.get().strip().lower()
            if not search_term:
                self.load_sales_data()
                return

            # Clear existing data
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            # Connect to database
            conn = sqlite3.connect('bike_shop.db')
            cursor = conn.cursor()

            # Search sales data
            cursor.execute('''
                SELECT sale_id, sale_date, customer_name, product_name, quantity, 
                       unit_price, total_amount, payment_method 
                FROM sales 
                WHERE LOWER(customer_name) LIKE ? OR LOWER(product_name) LIKE ?
                ORDER BY sale_date DESC
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            sales_data = cursor.fetchall()

            # Insert filtered data
            for sale in sales_data:
                self.sales_tree.insert('', 'end', values=sale)

            conn.close()
            
        except Exception as e:
            print(f"Error searching sales: {e}")

    def export_sales_report(self):
        """Export sales report to CSV"""
        try:
            # Get all sales data
            conn = sqlite3.connect('bike_shop.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sale_id, sale_date, customer_name, product_name, quantity, 
                       unit_price, total_amount, payment_method 
                FROM sales 
                ORDER BY sale_date DESC
            ''')
            sales_data = cursor.fetchall()
            conn.close()

            if not sales_data:
                messagebox.showinfo("Export", "No sales data to export.")
                return

            # Create CSV content
            csv_content = "Sale ID,Date,Customer,Product,Quantity,Unit Price,Total,Payment Method\n"
            for sale in sales_data:
                csv_content += f"{sale[0]},{sale[1]},{sale[2]},{sale[3]},{sale[4]},{sale[5]},{sale[6]},{sale[7]}\n"

            # Save to file
            filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            messagebox.showinfo("Export Successful", f"Sales report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export sales report: {str(e)}")

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
            
            # Sales button - NEW ADDITION
            self.sales_btn = self.create_nav_button(nav_frame, "💰", "Sales", self.main_app.show_sales)

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
                'services': self.services_btn,
                'sales': self.sales_btn  # Added sales to the nav_buttons dictionary
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

class BikeShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bike Shop Inventory Management System")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0fdff')
        
        # Initialize database
        self.init_database()
        
        # Create styles
        create_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Show dashboard by default
        self.show_dashboard()
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect('bike_shop.db')
            cursor = conn.cursor()
            
            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    product_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id TEXT UNIQUE NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    customer_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    payment_method TEXT NOT NULL
                )
            ''')
            
            # Create stock history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    new_stock_level INTEGER NOT NULL,
                    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
    
    def create_main_layout(self):
        """Create the main application layout with sidebar and content area"""
        try:
            # Main container
            main_container = ttk.Frame(self.root, style='Content.TFrame')
            main_container.pack(fill='both', expand=True)
            
            # Sidebar
            self.sidebar = ModernSidebar(main_container, self)
            self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
            
            # Content area
            self.content_area = ttk.Frame(main_container, style='Content.TFrame')
            self.content_area.pack(side='right', fill='both', expand=True)
            
        except Exception as e:
            print(f"Error creating main layout: {e}")
    
    def show_dashboard(self):
        """Show dashboard page"""
        self.clear_content_area()
        self.sidebar.set_active('dashboard')
        
        # Create dashboard content
        dashboard_frame = ttk.Frame(self.content_area, style='Content.TFrame')
        dashboard_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(dashboard_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Dashboard Overview", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Placeholder content
        placeholder = ttk.Label(dashboard_frame, text="🚴‍♂️ Bike Shop Dashboard\n\nThis is the main dashboard where you can see\nkey metrics and recent activities.", 
                               style='Placeholder.TLabel', justify='center')
        placeholder.pack(expand=True)
    
    def show_sales_entry(self):
        """Show sales entry (POS) page"""
        self.clear_content_area()
        self.sidebar.set_active('sales_entry')
        
        sales_frame = SalesEntryFrame(self.content_area, self)
        sales_frame.pack(fill='both', expand=True)
    
    def show_statistics(self):
        """Show statistics page"""
        self.clear_content_area()
        self.sidebar.set_active('statistics')
        
        # Create statistics content
        stats_frame = ttk.Frame(self.content_area, style='Content.TFrame')
        stats_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(stats_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Sales Statistics", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Placeholder content
        placeholder = ttk.Label(stats_frame, text="📊 Statistics\n\nSales analytics and performance metrics\nwill be displayed here.", 
                               style='Placeholder.TLabel', justify='center')
        placeholder.pack(expand=True)
    
    def show_stock_history(self):
        """Show stock history page"""
        self.clear_content_area()
        self.sidebar.set_active('stock_history')
        
        # Create stock history content
        stock_frame = ttk.Frame(self.content_area, style='Content.TFrame')
        stock_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(stock_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Stock History", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Placeholder content
        placeholder = ttk.Label(stock_frame, text="📋 Stock History\n\nTrack inventory changes and stock movements\nover time.", 
                               style='Placeholder.TLabel', justify='center')
        placeholder.pack(expand=True)
    
    def show_inventory(self):
        """Show inventory management page"""
        self.clear_content_area()
        self.sidebar.set_active('inventory')
        
        # Create inventory content
        inventory_frame = ttk.Frame(self.content_area, style='Content.TFrame')
        inventory_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(inventory_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Inventory Management", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Placeholder content
        placeholder = ttk.Label(inventory_frame, text="📦 Inventory\n\nManage your product inventory and stock levels\nin this section.", 
                               style='Placeholder.TLabel', justify='center')
        placeholder.pack(expand=True)
    
    def show_services(self):
        """Show services page"""
        self.clear_content_area()
        self.sidebar.set_active('services')
        
        # Create services content
        services_frame = ttk.Frame(self.content_area, style='Content.TFrame')
        services_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Header
        header_frame = ttk.Frame(services_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Bike Services", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Placeholder content
        placeholder = ttk.Label(services_frame, text="🔧 Services\n\nManage bike repair and maintenance services\nfor your customers.", 
                               style='Placeholder.TLabel', justify='center')
        placeholder.pack(expand=True)
    
    def show_sales(self):
        """Show sales records page"""
        self.clear_content_area()
        self.sidebar.set_active('sales')
        
        sales_frame = SalesFrame(self.content_area, self)
        sales_frame.pack(fill='both', expand=True)
    
    def clear_content_area(self):
        """Clear the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.quit()

def create_styles():
    """Create modern styles with the bike shop logo color scheme"""
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

        # Color scheme based on the bike shop logo
        colors = {
            'bg': '#f0fdff',                    # Very light cyan background
            'sidebar_bg': '#0f172a',            # Deep dark blue/black from logo
            'sidebar_text': '#ffffff',          # Pure white text
            'sidebar_active': '#00d4ff',        # Bright cyan from logo
            'card_bg': '#ffffff',               # Pure white cards
            'text_primary': '#0f172a',          # Dark blue/black for primary text
            'text_secondary': '#1e40af',        # Medium blue for secondary text
            'border': "#ddf4ff",                # Light cyan borders
            'primary': '#00bcd4',               # Turquoise/cyan primary
            'primary_dark': '#0891b2',          # Darker cyan for hover states
            'success': '#10b981',               # Keep green for success
            'warning': '#f59e0b',               # Keep amber for warning
            'danger': '#ef4444',                # Keep red for danger
            'accent': '#0ea5e9',                # Sky blue accent
            'gradient_start': '#00d4ff',        # Bright cyan (top of gradient)
            'gradient_end': '#1e40af'           # Deep blue (bottom of gradient)
        }

        # Configure root
        try:
            style.configure('.', background=colors['bg'])
        except tk.TclError as e:
            print(f"Warning: Could not configure root style: {e}")

        # Content frame styles
        try:
            style.configure('Content.TFrame', background=colors['bg'])
            style.configure('Card.TFrame', 
                           background=colors['card_bg'], 
                           relief='solid', 
                           borderwidth=1,
                           bordercolor=colors['border'])
        except tk.TclError as e:
            print(f"Warning: Could not configure frame styles: {e}")

        # Sidebar styles with gradient-like appearance
        try:
            style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
            style.configure('SidebarLogo.TFrame', background=colors['sidebar_bg'])
        except tk.TclError as e:
            print(f"Warning: Could not configure sidebar styles: {e}")
        
        # Logo styles with white text on dark background
        try:
            style.configure('Logo.TLabel', 
                           background=colors['sidebar_bg'], 
                           foreground=colors['sidebar_text'],
                           font=('Helvetica', 16))  # Larger font for bike emoji
            style.configure('LogoTitle.TLabel', 
                           background=colors['sidebar_bg'], 
                           foreground=colors['sidebar_text'],
                           font=('Helvetica', 12, 'bold'))
        except tk.TclError as e:
            print(f"Warning: Could not configure logo styles: {e}")

        # Navigation button styles with cyan active state
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
                     background=[('active', '#1e293b'), ('pressed', '#334155')])

            style.configure('SidebarNavActive.TButton',
                           background=colors['sidebar_active'],
                           foreground=colors['sidebar_bg'],  # Dark text on bright cyan
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

        # Breadcrumb styles with blue theme
        try:
            style.configure('Breadcrumb.TLabel',
                           background=colors['bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 10))
            
            style.configure('BreadcrumbActive.TLabel',
                           background=colors['bg'],
                           foreground=colors['primary'],
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
                           foreground=colors['primary'])  # Cyan icons
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

        # Entry and combobox styles with cyan borders
        try:
            style.configure('Modern.TEntry',
                           fieldbackground=colors['card_bg'],
                           foreground=colors['text_primary'],
                           bordercolor=colors['border'],
                           borderwidth=2,
                           relief='solid',
                           padding=12,
                           focuscolor=colors['primary'])

            style.configure('Modern.TCombobox',
                           fieldbackground=colors['card_bg'],
                           foreground=colors['text_primary'],
                           bordercolor=colors['border'],
                           borderwidth=2,
                           relief='solid',
                           padding=12,
                           arrowsize=12,
                           focuscolor=colors['primary'])
        except tk.TclError as e:
            print(f"Warning: Could not configure entry/combobox styles: {e}")

        # Button styles with cyan primary color
        try:
            style.configure('Primary.TButton',
                           background=colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           relief='flat',
                           font=('Helvetica', 10, 'bold'),
                           padding=(20, 12))
            
            style.map('Primary.TButton',
                     background=[('active', colors['primary_dark']), 
                               ('pressed', colors['gradient_end'])])

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

            # Special gradient-style button for checkout
            style.configure('RecordSale.TButton',
                           background=colors['gradient_end'],  # Deep blue
                           foreground='white',
                           borderwidth=0,
                           relief='flat',
                           font=('Helvetica', 12, 'bold'),
                           padding=(20, 15))
            
            style.map('RecordSale.TButton',
                     background=[('active', colors['primary']), 
                               ('pressed', colors['gradient_start'])])
        except tk.TclError as e:
            print(f"Warning: Could not configure button styles: {e}")

        # Treeview styles with cyan theme
        try:
            style.configure('Modern.Treeview',
                           background=colors['card_bg'],
                           foreground=colors['text_primary'],
                           fieldbackground=colors['card_bg'],
                           borderwidth=1,
                           bordercolor=colors['border'],
                           rowheight=35,
                           font=('Helvetica', 9))

            style.configure('Modern.Treeview.Heading',
                           background=colors['primary'],  # Cyan headers
                           foreground='white',
                           relief='flat',
                           font=('Helvetica', 9, 'bold'),
                           borderwidth=1,
                           bordercolor=colors['primary_dark'])

            # Alternating row colors
            style.map('Modern.Treeview',
                     background=[('selected', colors['primary']),
                               ('active', colors['gradient_start'])])
        except tk.TclError as e:
            print(f"Warning: Could not configure treeview styles: {e}")

        # Additional label styles
        try:
            style.configure('TotalAmount.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['gradient_end'],  # Deep blue for emphasis
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
                           foreground=colors['primary'],  # Cyan for values
                           font=('Helvetica', 20, 'bold'))

            style.configure('CardIcon.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['primary'])  # Cyan icons

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
                           borderwidth=1,
                           bordercolor=colors['border'],
                           rowheight=25,
                           font=('Helvetica', 8))

            style.configure('Dashboard.Treeview.Heading',
                           background=colors['accent'],  # Sky blue for dashboard
                           foreground='white',
                           relief='flat',
                           font=('Helvetica', 8, 'bold'),
                           borderwidth=1)
        except tk.TclError as e:
            print(f"Warning: Could not configure dashboard styles: {e}")

        # Insight styles with gradient colors
        try:
            style.configure('InsightTitle.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 9, 'bold'))

            style.configure('InsightValue.TLabel',
                           background=colors['card_bg'],
                           foreground=colors['gradient_end'],
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

        print("Bike shop color scheme applied successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating styles: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the application
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BikeShopApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()