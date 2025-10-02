import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from dashboard import DashboardModule
from pointofsale import PointOfSaleModule
from statistics import StatisticsModule
from stockhistory import StockHistoryModule
from inventory import InventoryModule
from services import ServicesModule
from ui_components import create_styles, ModernSidebar

class BikeShopInventorySystem:
    def __init__(self, root):
        self.root = root
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.title("Bike Shop Inventory")
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.configure(bg='#f8fafc')
        
        # Create modern styles
        create_styles()
        
        self.init_database()
        self.create_main_interface()
        
        # Initialize modules
        self.init_modules()
        
        # Show default page
        self.show_sales_entry() 

    def init_modules(self):
        """Initialize all the modular components"""
        self.dashboard_module = DashboardModule(self.content_frame, self)
        self.pos_module = PointOfSaleModule(self.content_frame, self)
        self.statistics_module = StatisticsModule(self.content_frame, self)
        self.stock_history_module = StockHistoryModule(self.content_frame, self)
        self.inventory_module = InventoryModule(self.content_frame, self)
        self.services_module = ServicesModule(self.content_frame, self)
        
        self.sales_entry_frame = None
        self.dashboard_frame = None
        self.statistics_frame = None
        self.inventory_frame = None
        self.stock_history_frame = None
        self.services_frame = None

    def init_database(self):
        """Initialize SQLite database and create tables - UPDATED with customer name and address support"""
        self.conn = sqlite3.connect('bike_shop_inventory.db')
        self.cursor = self.conn.cursor()

        # Create products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL DEFAULT 0.0,
                stock INTEGER NOT NULL DEFAULT 0,
                category TEXT DEFAULT 'Bikes',
                product_id TEXT UNIQUE NOT NULL,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_id TEXT,
                product_name TEXT,
                product_category TEXT,
                customer_name TEXT,
                customer_address TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        try:
            self.cursor.execute("PRAGMA table_info(sales)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'customer_address' not in columns:
                self.cursor.execute("ALTER TABLE sales ADD COLUMN customer_address TEXT DEFAULT ''")
                self.conn.commit()
                print("Added customer_address column to sales table")
                
            # Add customer_name column if it doesn't exist
            if 'customer_name' not in columns:
                self.cursor.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT DEFAULT ''")
                self.conn.commit()
                print("Added customer_name column to sales table")
                
        except Exception as e:
            print(f"Error checking/adding columns: {str(e)}")

        # Create transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE NOT NULL,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                product_name TEXT,
                movement_type TEXT NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT'
                quantity INTEGER NOT NULL,
                reference_id TEXT, -- transaction_id for sales, or other reference
                reason TEXT, -- 'SALE', 'RESTOCK', 'RETURN', 'DAMAGE', etc.
                movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        self.conn.commit()
        print("Database initialized successfully with customer name and address support")

    def create_main_interface(self):
        """Create the main interface with sidebar and content area"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)

        # Create sidebar
        self.sidebar = ModernSidebar(main_container, self)
        self.sidebar.pack(side='left', fill='y')

        # Create main content area
        self.content_frame = ttk.Frame(main_container, style='Content.TFrame')
        self.content_frame.pack(side='right', fill='both', expand=True)

    def show_sales_entry(self):
        """Show the POS interface"""
        self.hide_all_frames()
        self.sales_entry_frame = self.pos_module.create_interface()
        if self.sales_entry_frame:
            self.sales_entry_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('sales_entry')

    def show_dashboard(self):
        """Show the dashboard interface"""
        self.hide_all_frames()
        self.dashboard_frame = self.dashboard_module.create_interface()
        if self.dashboard_frame:
            self.dashboard_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('dashboard')

    def show_statistics(self):
        """Show the statistics interface"""
        self.hide_all_frames()
        self.statistics_frame = self.statistics_module.create_interface()
        if self.statistics_frame:
            self.statistics_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('statistics')

    def show_inventory(self):
        """Show the inventory interface"""
        self.hide_all_frames()
        self.inventory_frame = self.inventory_module.create_interface()
        if self.inventory_frame:
            self.inventory_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('inventory')

    def show_stock_history(self):
        """Show the stock history interface"""
        self.hide_all_frames()
        self.stock_history_frame = self.stock_history_module.create_interface()
        if self.stock_history_frame:
            self.stock_history_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('stock_history')

    def show_services(self):
        """Show the services interface"""
        self.hide_all_frames()
        self.services_frame = self.services_module.create_interface()
        if self.services_frame:
            self.services_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('services')

    def hide_all_frames(self):
        """Hide all content frames"""
        for frame in [self.sales_entry_frame, self.dashboard_frame, self.statistics_frame,
                     self.inventory_frame, self.stock_history_frame, self.services_frame]:
            if frame:
                frame.pack_forget()

    # Database helper methods for modules
    def get_total_sales_count(self):
        """Get total number of sales transactions"""
        self.cursor.execute('SELECT COUNT(*) FROM sales')
        return self.cursor.fetchone()[0]

    def get_total_products(self):
        self.cursor.execute('SELECT COUNT(*) FROM products')
        return self.cursor.fetchone()[0]

    def get_total_sales(self):
        self.cursor.execute('SELECT SUM(total) FROM sales')
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_total_stock_items(self):
        """Get total stock items across all products"""
        self.cursor.execute('SELECT SUM(stock) FROM products')
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_today_summary(self):
        """Get today's sales summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            # Sales count
            self.cursor.execute('''
                SELECT COUNT(DISTINCT transaction_id) as sales_count,
                       SUM(quantity) as items_sold,
                       SUM(total) as revenue
                FROM sales 
                WHERE DATE(sale_date) = ?
            ''', (today,))
            result = self.cursor.fetchone()
            
            return {
                'sales_count': result[0] if result[0] else 0,
                'items_sold': result[1] if result[1] else 0,
                'revenue': result[2] if result[2] else 0.0
            }
        except Exception as e:
            print(f"Error getting today's summary: {e}")
            return {'sales_count': 0, 'items_sold': 0, 'revenue': 0.0}

    def get_monthly_sales_data(self):
        """Get monthly sales data for the current year"""
        try:
            current_year = datetime.now().year
            self.cursor.execute('''
                SELECT 
                    strftime('%m', sale_date) as month,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE strftime('%Y', sale_date) = ?
                GROUP BY month
                ORDER BY month
            ''', (str(current_year),))
            
            results = self.cursor.fetchall()
            
            # Format month numbers to month names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            formatted_results = []
            for row in results:
                month_index = int(row[0]) - 1
                month_name = month_names[month_index]
                formatted_results.append((month_name, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting monthly sales data: {e}")
            return []
        
    def get_specific_month_sales_data(self, month_name):
        """Get daily sales data for a specific month"""
        try:
            current_year = datetime.now().year
            
            # Map month names to numbers
            month_map = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }
            
            month_num = month_map.get(month_name)
            if not month_num:
                return []
            
            self.cursor.execute('''
                SELECT 
                    strftime('%d', sale_date) as day,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE strftime('%Y', sale_date) = ? AND strftime('%m', sale_date) = ?
                GROUP BY day
                ORDER BY day
            ''', (str(current_year), month_num))
            
            results = self.cursor.fetchall()
            
            # Format day labels
            formatted_results = []
            for row in results:
                day_label = f"Day {int(row[0])}"
                formatted_results.append((day_label, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting specific month sales data: {e}")
            return []

    def get_daily_sales_data(self):
        """Get daily sales data for the last 30 days"""
        try:
            self.cursor.execute('''
                SELECT 
                    DATE(sale_date) as date,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-30 days')
                GROUP BY DATE(sale_date)
                ORDER BY date
            ''')
            results = self.cursor.fetchall()
            
            # Format dates to be more readable (MM-DD)
            formatted_results = []
            for row in results:
                date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%m-%d')
                formatted_results.append((formatted_date, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting daily sales data: {e}")
            return []

    def get_weekly_sales_data(self):
        """Get weekly sales data for the last 12 weeks"""
        try:
            self.cursor.execute('''
                SELECT 
                    strftime('%Y-W%W', sale_date) as week,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-84 days')
                GROUP BY week
                ORDER BY week
            ''')
            results = self.cursor.fetchall()
            
            # Format week labels (W01, W02, etc.)
            formatted_results = []
            for row in results:
                week_label = f"W{row[0].split('-W')[1]}"
                formatted_results.append((week_label, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting weekly sales data: {e}")
            return []

    def get_yearly_sales_data(self):
        """Get yearly sales data for the last 5 years"""
        try:
            self.cursor.execute('''
                SELECT 
                    strftime('%Y', sale_date) as year,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                GROUP BY year
                ORDER BY year
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting yearly sales data: {e}")
            return []

    def get_available_years(self):
        """Get list of years that have sales data"""
        try:
            self.cursor.execute('''
                SELECT DISTINCT strftime('%Y', sale_date) as year
                FROM sales 
                WHERE sale_date IS NOT NULL
                ORDER BY year DESC
            ''')
            results = self.cursor.fetchall()
            return [row[0] for row in results] if results else [str(datetime.now().year)]
        except Exception as e:
            print(f"Error getting available years: {e}")
            return [str(datetime.now().year)]

    def get_monthly_sales_data(self, year=None):
        """Get monthly sales data for a specific year"""
        try:
            if year is None:
                year = datetime.now().year
            
            self.cursor.execute('''
                SELECT 
                    strftime('%m', sale_date) as month,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE strftime('%Y', sale_date) = ?
                GROUP BY month
                ORDER BY month
            ''', (str(year),))
            
            results = self.cursor.fetchall()
            
            # Format month numbers to month names
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            formatted_results = []
            for row in results:
                month_index = int(row[0]) - 1
                month_name = month_names[month_index]
                formatted_results.append((month_name, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting monthly sales data: {e}")
            return []

    def get_specific_month_sales_data(self, month_name, year=None):
        """Get daily sales data for a specific month and year"""
        try:
            if year is None:
                year = datetime.now().year
            
            # Map month names to numbers
            month_map = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }
            
            month_num = month_map.get(month_name)
            if not month_num:
                return []
            
            self.cursor.execute('''
                SELECT 
                    strftime('%d', sale_date) as day,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold
                FROM sales 
                WHERE strftime('%Y', sale_date) = ? AND strftime('%m', sale_date) = ?
                GROUP BY day
                ORDER BY day
            ''', (str(year), month_num))
            
            results = self.cursor.fetchall()
            
            # Format day labels
            formatted_results = []
            for row in results:
                day_label = f"Day {int(row[0])}"
                formatted_results.append((day_label, row[1], row[2]))
            
            return formatted_results
        except Exception as e:
            print(f"Error getting specific month sales data: {e}")
            return []

    def get_category_sales_data(self):
        """Get sales data by category"""
        self.cursor.execute('''
            SELECT product_category, SUM(total) as total_sales
            FROM sales 
            GROUP BY product_category
            ORDER BY total_sales DESC
        ''')
        return self.cursor.fetchall()

    def get_top_buyers(self, limit=10):
        """Get top buyers by total purchase amount"""
        try:
            self.cursor.execute('''
                SELECT 
                    customer_name,
                    COUNT(DISTINCT transaction_id) as purchase_count,
                    SUM(total) as total_amount
                FROM sales 
                WHERE customer_name IS NOT NULL AND customer_name != ''
                GROUP BY customer_name
                ORDER BY total_amount DESC
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting top buyers: {e}")
            return []

    def get_top_products(self, limit=10):
        """Get top products by quantity sold"""
        try:
            self.cursor.execute('''
                SELECT 
                    product_name,
                    SUM(quantity) as quantity_sold,
                    SUM(total) as total_revenue
                FROM sales 
                GROUP BY product_name
                ORDER BY quantity_sold DESC
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting top products: {e}")
            return []

    def get_low_stock_products(self):
        """Get products with low stock"""
        self.cursor.execute('''
            SELECT id, name, price, stock, product_id 
            FROM products 
            WHERE stock < 10 
            ORDER BY stock ASC
            LIMIT 10
        ''')
        return self.cursor.fetchall()

    def get_recent_sales(self, limit=10):
        """Get recent sales for display - UPDATED to include customer name and address"""
        try:
            self.cursor.execute('''
                SELECT sale_date, product_name, product_id, customer_name, 
                       COALESCE(customer_address, 'N/A') as customer_address, 
                       quantity, total
                FROM sales 
                ORDER BY sale_date DESC 
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting recent sales: {e}")
            return []

    def add_product(self):
        """Delegate to inventory module"""
        if hasattr(self, 'inventory_module'):
            self.inventory_module.add_product()

    def refresh_products(self):
        """Refresh products display"""
        if hasattr(self, 'inventory_module') and self.inventory_module.frame:
            self.inventory_module.refresh_products()

    # POS Integration methods
    def get_all_products(self):
        """Get all products from the database"""
        try:
            self.cursor.execute('''
                SELECT product_id, name, price, stock, category 
                FROM products 
                ORDER BY name
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all products: {e}")
            return []

    def get_product_by_id(self, product_id):
        """Get product details by product_id"""
        try:
            self.cursor.execute('''
                SELECT name, price, stock, category 
                FROM products 
                WHERE product_id = ?
            ''', (product_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting product {product_id}: {e}")
            return None

    def get_current_stock(self, product_id):
        """Get current stock for a product"""
        try:
            self.cursor.execute('SELECT stock FROM products WHERE product_id = ?', (product_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error getting current stock for {product_id}: {e}")
            return 0

    def check_stock_availability(self, product_id, quantity):
        """Check if enough stock is available for a product"""
        try:
            self.cursor.execute('SELECT stock FROM products WHERE product_id = ?', (product_id,))
            result = self.cursor.fetchone()
            if result:
                current_stock = result[0]
                print(f"Stock check for {product_id}: Current={current_stock}, Requested={quantity}")
                return current_stock >= quantity
            else:
                print(f"Product {product_id} not found in stock check")
                return False
        except sqlite3.Error as e:
            print(f"Error checking stock for {product_id}: {e}")
            return False

   
    def validate_transaction(self, cart_items):
        """Validate that all products in cart exist and have sufficient stock"""
        for item in cart_items:
            product_id = item['product_id']
            
            # Check if product exists
            self.cursor.execute('SELECT name, stock FROM products WHERE product_id = ?', (product_id,))
            product = self.cursor.fetchone()
            
            if not product:
                return False, f"Product {item['product_name']} (ID: {product_id}) not found in inventory"
            
            # Check stock availability
            product_name, stock = product
            if item['quantity'] > stock:
                return False, f"Insufficient stock for {product_name}. Available: {stock}, Requested: {item['quantity']}"
        
        return True, "Validation successful"

    def record_sale(self, cart_items, payment_method='Cash'):
        """Record a sale transaction and update inventory - UPDATED with customer address support"""
        try:
            print(f"Recording sale with {len(cart_items)} items")
            
            # Validate input
            if not cart_items:
                return False, "No items to record"
            
            # Generate unique transaction ID
            transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            total_amount = 0
            sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Start transaction
            self.cursor.execute('BEGIN TRANSACTION')
            
            # Validate and process each item
            for item in cart_items:
                required_fields = ['product_id', 'product_name', 'customer_name', 'unit_price', 'quantity']
                if not all(field in item for field in required_fields):
                    self.cursor.execute('ROLLBACK')
                    return False, f"Missing required fields in item: {item}"
                
                # Validate stock availability
                if not self.check_stock_availability(item['product_id'], item['quantity']):
                    current_stock = self.get_current_stock(item['product_id'])
                    self.cursor.execute('ROLLBACK')
                    return False, f"Insufficient stock for {item['product_name']}. Available: {current_stock}, Requested: {item['quantity']}"
                
                # Calculate item total
                item_total = item['quantity'] * item['unit_price']
                total_amount += item_total
                
                # Get customer address (might be empty)
                customer_address = item.get('customer_address', '')
                
                # Insert into sales table
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, product_category, 
                                    customer_name, customer_address, quantity, price, total, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (transaction_id, item['product_id'], item['product_name'], 
                    item.get('category', 'N/A'), item['customer_name'], customer_address,
                    item['quantity'], item['unit_price'], item_total, sale_date))
                
                # Update product stock
                self.cursor.execute('''
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE product_id = ?
                ''', (item['quantity'], item['product_id']))
                
                # Verify the update worked
                if self.cursor.rowcount == 0:
                    self.cursor.execute('ROLLBACK')
                    return False, f"Failed to update stock for product {item['product_id']}"
                
                # Get updated stock for logging
                self.cursor.execute('SELECT stock FROM products WHERE product_id = ?', (item['product_id'],))
                updated_stock = self.cursor.fetchone()
                
                if updated_stock is None:
                    self.cursor.execute('ROLLBACK')
                    return False, f"Product {item['product_id']} not found after stock update"
                
                if updated_stock[0] < 0:
                    self.cursor.execute('ROLLBACK')
                    return False, f"Stock would become negative for {item['product_name']}"
                
                # Record stock movement 
                address_note = f" (Address: {customer_address})" if customer_address else ""
                self.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                            reference_id, reason, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item['product_id'], item['product_name'], 'OUT', 
                    item['quantity'], transaction_id, 'SALE', 
                    f'Sold {item["quantity"]} units to {item["customer_name"]}{address_note}. New stock: {updated_stock[0]}'))
            
            # Insert into transactions table
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, total_amount, payment_method, transaction_date)
                VALUES (?, ?, ?, ?)
            ''', (transaction_id, total_amount, payment_method, sale_date))
            
            # Commit the transaction
            self.cursor.execute('COMMIT')
            
            print(f"Sale recorded successfully. Transaction ID: {transaction_id}, Total: ₱{total_amount:.2f}")
            return True, transaction_id
            
        except sqlite3.Error as e:
            self.cursor.execute('ROLLBACK')
            print(f"Database error in record_sale: {e}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            self.cursor.execute('ROLLBACK')
            print(f"Unexpected error in record_sale: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Unexpected error: {str(e)}"

    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.quit()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = BikeShopInventorySystem(root)
    root.mainloop()