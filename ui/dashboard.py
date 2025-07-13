import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ui_components import ProductDialog, create_styles, ModernSidebar, SalesEntryFrame

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
        self.show_sales_entry() 
        

    def init_database(self):
        """Initialize SQLite database and create tables"""
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

        # Create sales table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                product_id TEXT,
                product_name TEXT,
                product_category TEXT,
                quantity INTEGER,
                price REAL,
                total REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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

        # Create stock_movements table for better tracking
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
        print("Database initialized successfully")  

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

        # Initialize content frames (but don't pack them yet)
        self.sales_entry_frame = None
        self.dashboard_frame = None
        self.inventory_frame = None
        self.stock_history_frame = None
        self.services_frame = None

    def show_sales_entry(self):
        """Show the POS interface"""
        self.hide_all_frames()
        if not self.sales_entry_frame:
            self.sales_entry_frame = SalesEntryFrame(self.content_frame, self)
        self.sales_entry_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('sales_entry')

    def show_dashboard(self):
        """Show the dashboard interface"""
        self.hide_all_frames()
        if not self.dashboard_frame:
            self.create_dashboard_interface()
        self.dashboard_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('dashboard')

    def show_inventory(self):
        """Show the inventory interface"""
        self.hide_all_frames()
        if not self.inventory_frame:
            self.create_inventory_interface()
        self.inventory_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('inventory')
        # Refresh products after the interface is created and shown
        self.refresh_products()

    def show_stock_history(self):
        """Show the stock history interface"""
        self.hide_all_frames()
        if not self.stock_history_frame:
            self.create_stock_history_interface()
        self.stock_history_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('stock_history')
        # Refresh stock history after the interface is created and shown
        self.refresh_stock_history()

    def show_services(self):
        """Show the services interface"""
        self.hide_all_frames()
        if not self.services_frame:
            self.create_services_interface()
        self.services_frame.pack(fill='both', expand=True)
        self.sidebar.set_active('services')

    def hide_all_frames(self):
        """Hide all content frames"""
        for frame in [self.sales_entry_frame, self.dashboard_frame, 
                     self.inventory_frame, self.stock_history_frame, self.services_frame]:
            if frame:
                frame.pack_forget()

    def create_dashboard_interface(self):
        """Create the dashboard with statistics"""
        self.dashboard_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.dashboard_frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Dashboard", style='PageTitle.TLabel').pack(side='left')
        
        # Stats cards container
        stats_container = ttk.Frame(self.dashboard_frame, style='Content.TFrame')
        stats_container.pack(fill='x', padx=30, pady=(0, 20))
        
        # Create stats cards
        self.create_dashboard_stats_cards(stats_container)
        
        # Main content area with charts and tables
        main_content = ttk.Frame(self.dashboard_frame, style='Content.TFrame')
        main_content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Top row - Charts
        charts_row = ttk.Frame(main_content, style='Content.TFrame')
        charts_row.pack(fill='x', pady=(0, 20))
        
        # Left chart - Monthly Sales Trend
        left_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        left_chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_monthly_sales_chart(left_chart_frame)
        
        # Middle chart - Sales by Category
        middle_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        middle_chart_frame.pack(side='left', fill='both', expand=True, padx=(5, 5))
        self.create_category_sales_chart(middle_chart_frame)
        
        # Right section - Inventory Insights
        right_insights_frame = ttk.Frame(charts_row, style='Card.TFrame')
        right_insights_frame.pack(side='right', fill='y', padx=(10, 0))
        self.create_inventory_insights(right_insights_frame)
        
        # Bottom row - Tables
        tables_row = ttk.Frame(main_content, style='Content.TFrame')
        tables_row.pack(fill='both', expand=True)
        
        # Left table - Recent Sales
        recent_sales_frame = ttk.Frame(tables_row, style='Card.TFrame')
        recent_sales_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_recent_sales_table(recent_sales_frame)
        
        # Right table - Stock Alert
        stock_alert_frame = ttk.Frame(tables_row, style='Card.TFrame')
        stock_alert_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.create_stock_alert_table(stock_alert_frame)

    def create_dashboard_stats_cards(self, parent):
        """Create modern statistics cards"""
        # Get statistics from database
        total_sales_count = self.get_total_sales_count()
        total_revenue = self.get_total_sales()
        total_products = self.get_total_products()
        total_stock_items = self.get_total_stock_items()
        
        # Cards frame
        cards_frame = ttk.Frame(parent, style='Content.TFrame')
        cards_frame.pack(fill='x')
        
        # Configure grid weights
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Total Sales Card
        self.create_modern_stat_card(cards_frame, "Total Sales", str(total_sales_count), "+100%", "#3b82f6", "🛒", 0)
        
        # Total Revenue Card
        self.create_modern_stat_card(cards_frame, "Total Revenue", f"₱{total_revenue:,.2f}", "-100%", "#10b981", "💰", 1)
        
        # Total Products Card
        self.create_modern_stat_card(cards_frame, "Total Products", str(total_products), "0%", "#8b5cf6", "📦", 2)
        
        # Total Stock Card
        self.create_modern_stat_card(cards_frame, "Total Stock", str(total_stock_items), "0%", "#f59e0b", "📊", 3)

    def create_modern_stat_card(self, parent, title, value, change, color, icon, column):
        """Create a modern statistics card with icon and change indicator"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=0, column=column, padx=10, sticky='ew')
        
        # Card content
        content_frame = ttk.Frame(card_frame, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header with icon and title
        header_frame = ttk.Frame(content_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text=title, style='CardTitle.TLabel').pack(side='left')
        ttk.Label(header_frame, text=icon, font=('Arial', 16), style='CardIcon.TLabel').pack(side='right')
        
        # Value
        ttk.Label(content_frame, text=value, style='CardValue.TLabel').pack(anchor='w')
        
        # Change indicator
        change_color = '#10b981' if change.startswith('+') else '#ef4444' if change.startswith('-') else '#6b7280'
        change_label = ttk.Label(content_frame, text=change, foreground=change_color, 
                                font=('Helvetica', 9), background='#ffffff')
        change_label.pack(anchor='w', pady=(5, 0))

    def create_monthly_sales_chart(self, parent):
        """Create monthly sales trend chart"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        ttk.Label(header_frame, text="Monthly Sales Trend", style='SectionTitle.TLabel').pack(side='left')
        
        # Year selector
        year_frame = ttk.Frame(header_frame, style='Card.TFrame')
        year_frame.pack(side='right')
        
        year_var = tk.StringVar(value='2025')
        year_combo = ttk.Combobox(year_frame, textvariable=year_var, values=['2023', '2024', '2025'], 
                                 width=8, state='readonly', style='Modern.TCombobox')
        year_combo.pack()
        
        # Chart area
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(10, 15))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(6, 3), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Get monthly sales data
        monthly_data = self.get_monthly_sales_data()
        
        if monthly_data:
            months = [row[0] for row in monthly_data]
            revenue = [row[1] for row in monthly_data]
            items_sold = [row[2] for row in monthly_data]
            
            # Create dual axis chart
            ax2 = ax.twinx()
            
            # Revenue line
            line1 = ax.plot(months, revenue, color='#3b82f6', linewidth=2, marker='o', 
                           markersize=4, label='Sales Revenue (₱)')
            
            # Items sold bars
            bars = ax2.bar(months, items_sold, alpha=0.3, color='#94a3b8', label='Items Sold')
            
            ax.set_ylabel('Sales Revenue (₱)', color='#3b82f6', fontsize=9)
            ax2.set_ylabel('Items Sold', color='#94a3b8', fontsize=9)
            ax.tick_params(axis='y', labelcolor='#3b82f6', labelsize=8)
            ax2.tick_params(axis='y', labelcolor='#94a3b8', labelsize=8)
            ax.tick_params(axis='x', labelsize=8, rotation=45)
            
        else:
            ax.text(0.5, 0.5, 'No sales data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='#6b7280')
        
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('white')
        fig.tight_layout()
        
        # Add to tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_category_sales_chart(self, parent):
        """Create sales by category pie chart"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        ttk.Label(header_frame, text="Sales by Category", style='SectionTitle.TLabel').pack(side='left')
        
        # Year selector
        year_frame = ttk.Frame(header_frame, style='Card.TFrame')
        year_frame.pack(side='right')
        
        year_var = tk.StringVar(value='2025')
        year_combo = ttk.Combobox(year_frame, textvariable=year_var, values=['2023', '2024', '2025'], 
                                 width=8, state='readonly', style='Modern.TCombobox')
        year_combo.pack()
        
        # Chart area
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(10, 15))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 3), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Get category sales data
        category_data = self.get_category_sales_data()
        
        if category_data:
            categories = [row[0] if row[0] else 'Other' for row in category_data]
            amounts = [row[1] for row in category_data]
            
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                             colors=colors[:len(categories)], startangle=90)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
                autotext.set_weight('bold')
        else:
            ax.text(0.5, 0.5, 'No sales data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='#6b7280')
        
        ax.set_facecolor('white')
        fig.tight_layout()
        
        # Add to tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_inventory_insights(self, parent):
        """Create inventory insights card"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Inventory Insights", style='SectionTitle.TLabel').pack()
        
        # Content
        content_frame = ttk.Frame(parent, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Low Stock Items
        low_stock_frame = ttk.Frame(content_frame, style='Card.TFrame')
        low_stock_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(low_stock_frame, text="Low Stock Items", style='InsightTitle.TLabel').pack(anchor='w')
        low_stock_count = self.get_low_stock_count()
        ttk.Label(low_stock_frame, text=str(low_stock_count), style='InsightValue.TLabel').pack(anchor='w')
        
        # Categories
        categories_frame = ttk.Frame(content_frame, style='Card.TFrame')
        categories_frame.pack(fill='x')
        
        ttk.Label(categories_frame, text="Categories", style='InsightTitle.TLabel').pack(anchor='w')
        categories_count = self.get_categories_count()
        ttk.Label(categories_frame, text=str(categories_count), style='InsightValue.TLabel').pack(anchor='w')

    def create_recent_sales_table(self, parent):
        """Create recent sales table"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Recent Sales", style='SectionTitle.TLabel').pack(side='left')
        ttk.Label(header_frame, text="View More →", style='ViewMore.TLabel').pack(side='right')
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('#', 'Date', 'Product', 'Category', 'Amount')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=6)
        
        # Configure columns
        tree.heading('#', text='#')
        tree.heading('Date', text='Date')
        tree.heading('Product', text='Product')
        tree.heading('Category', text='Category')
        tree.heading('Amount', text='Amount')
        
        tree.column('#', width=30)
        tree.column('Date', width=70)
        tree.column('Product', width=120)
        tree.column('Category', width=80)
        tree.column('Amount', width=80)
        
        # Get recent sales data
        recent_sales = self.get_recent_sales(5)
        for i, sale in enumerate(recent_sales, 1):
            # Format date
            sale_date = sale[0]
            if isinstance(sale_date, str):
                try:
                    date_obj = datetime.strptime(sale_date.split()[0], '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%b %d')
                except:
                    formatted_date = sale_date[:6]
            else:
                formatted_date = str(sale_date)[:6]
            
            tree.insert('', 'end', values=(
                f"{i:02d}",
                formatted_date,
                sale[1][:15] + "..." if len(sale[1]) > 15 else sale[1],  # product_name
                sale[3] if sale[3] else "N/A",  # category
                f"₱{sale[5]:,.2f}"  # total
            ))
        
        tree.pack(fill='both', expand=True)

    def create_stock_alert_table(self, parent):
        """Create stock alert table"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Stock Alert", style='SectionTitle.TLabel').pack(side='left')
        ttk.Label(header_frame, text="View More →", style='ViewMore.TLabel').pack(side='right')
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Get low stock products
        low_stock_products = self.get_low_stock_products()
        
        if low_stock_products:
            columns = ('SKU', 'Product', 'Quantity')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=6)
            
            # Configure columns
            tree.heading('SKU', text='SKU')
            tree.heading('Product', text='Product')
            tree.heading('Quantity', text='Quantity')
            
            tree.column('SKU', width=80)
            tree.column('Product', width=150)
            tree.column('Quantity', width=80)
            
            for product in low_stock_products:
                tree.insert('', 'end', values=(
                    product[4],  # product_id
                    product[1][:20] + "..." if len(product[1]) > 20 else product[1],  # name
                    product[3]  # stock
                ))
            
            tree.pack(fill='both', expand=True)
        else:
            no_alerts_label = ttk.Label(table_frame, text="No stock alerts", 
                                       style='NoData.TLabel')
            no_alerts_label.pack(expand=True)

    # Additional database helper methods for dashboard
    def get_total_sales_count(self):
        """Get total number of sales transactions"""
        self.cursor.execute('SELECT COUNT(*) FROM sales')
        return self.cursor.fetchone()[0]

    def get_total_stock_items(self):
        """Get total stock items across all products"""
        self.cursor.execute('SELECT SUM(stock) FROM products')
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_monthly_sales_data(self):
        """Get monthly sales data for chart"""
        self.cursor.execute('''
            SELECT 
                strftime('%m', sale_date) as month,
                SUM(total) as revenue,
                SUM(quantity) as items_sold
            FROM sales 
            WHERE strftime('%Y', sale_date) = '2025'
            GROUP BY month
            ORDER BY month
        ''')
        return self.cursor.fetchall()

    def get_category_sales_data(self):
        """Get sales data by category"""
        self.cursor.execute('''
            SELECT product_category, SUM(total) as total_sales
            FROM sales 
            GROUP BY product_category
            ORDER BY total_sales DESC
        ''')
        return self.cursor.fetchall()

    def get_categories_count(self):
        """Get number of distinct categories"""
        self.cursor.execute('SELECT COUNT(DISTINCT category) FROM products')
        return self.cursor.fetchone()[0]

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

    def create_inventory_interface(self):
        """Create the inventory management interface"""
        self.inventory_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.inventory_frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Inventory", style='PageTitle.TLabel').pack(side='left')
        
        # Controls
        controls_frame = ttk.Frame(self.inventory_frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Button(controls_frame, text="Add Product", command=self.add_product, 
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit Product", command=self.edit_product, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete Product", command=self.delete_product, 
                  style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_products, 
                  style='Secondary.TButton').pack(side='left')
        
        # Inventory table
        table_frame = ttk.Frame(self.inventory_frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview
        columns = ('ID', 'Name', 'Price', 'Stock', 'Category', 'Product ID')
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            if col == 'ID':
                self.inventory_tree.column(col, width=50)
            elif col == 'Name':
                self.inventory_tree.column(col, width=200)
            else:
                self.inventory_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        print("Inventory interface created successfully")  # Debug print

    def create_stock_history_interface(self):
        """Create the stock history interface"""
        self.stock_history_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.stock_history_frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Stock History", style='PageTitle.TLabel').pack(side='left')
        
        # Controls and filters
        controls_frame = ttk.Frame(self.stock_history_frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        # Left side - Filters
        filters_frame = ttk.Frame(controls_frame, style='Content.TFrame')
        filters_frame.pack(side='left', fill='x', expand=True)
        
        # Date filter
        ttk.Label(filters_frame, text="Filter by Date:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        self.date_filter_var = tk.StringVar(value='All Time')
        date_filter = ttk.Combobox(filters_frame, textvariable=self.date_filter_var,
                                  values=['All Time', 'Today', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days'],
                                  state='readonly', style='Modern.TCombobox', width=15)
        date_filter.pack(side='left', padx=(0, 15))
        date_filter.bind('<<ComboboxSelected>>', self.filter_stock_history)
        
        # Category filter
        ttk.Label(filters_frame, text="Category:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        self.stock_category_var = tk.StringVar(value='All Categories')
        category_filter = ttk.Combobox(filters_frame, textvariable=self.stock_category_var,
                                     values=['All Categories', 'Bikes', 'Accessories', 'Parts', 'Clothing', 'Services'],
                                     state='readonly', style='Modern.TCombobox', width=15)
        category_filter.pack(side='left', padx=(0, 15))
        category_filter.bind('<<ComboboxSelected>>', self.filter_stock_history)
        
        # Movement type filter
        ttk.Label(filters_frame, text="Movement Type:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        self.movement_type_var = tk.StringVar(value='All Movements')
        movement_filter = ttk.Combobox(filters_frame, textvariable=self.movement_type_var,
                                     values=['All Movements', 'Sales (Out)', 'Stock Added (In)', 'Returns (In)'],
                                     state='readonly', style='Modern.TCombobox', width=15)
        movement_filter.pack(side='left', padx=(0, 15))
        movement_filter.bind('<<ComboboxSelected>>', self.filter_stock_history)
        
        # Right side - Action buttons
        buttons_frame = ttk.Frame(controls_frame, style='Content.TFrame')
        buttons_frame.pack(side='right')
        
        # Delete button
        ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_stock_history,
                  style='Danger.TButton').pack(side='right', padx=(0, 10))
        
        # Refresh button
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_stock_history,
                  style='Secondary.TButton').pack(side='right', padx=(0, 10))
        
        # Stock history table
        table_frame = ttk.Frame(self.stock_history_frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview for stock history
        columns = ('ID', 'Date', 'Time', 'Transaction ID', 'Product Name', 'Product ID', 
                  'Category', 'Movement Type', 'Quantity', 'Unit Price', 'Total Amount', 'Current Stock')
        self.stock_history_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                              style='Modern.Treeview')
        
        # Configure columns
        column_widths = {
            'ID': 60,  
            'Date': 80,
            'Time': 80, 
            'Transaction ID': 120,
            'Product Name': 150,
            'Product ID': 100,
            'Category': 80,
            'Movement Type': 100,
            'Quantity': 70,
            'Unit Price': 80,
            'Total Amount': 100,
            'Current Stock': 90
        }
        
        for col in columns:
            self.stock_history_tree.heading(col, text=col)
            self.stock_history_tree.column(col, width=column_widths.get(col, 80))
        
        # Hide the ID column but keep it for reference
        self.stock_history_tree.column('ID', width=0, stretch=False)
        self.stock_history_tree.heading('ID', text='')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.stock_history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.stock_history_tree.xview)
        self.stock_history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.stock_history_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Summary section
        summary_frame = ttk.Frame(self.stock_history_frame, style='Card.TFrame')
        summary_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Summary labels
        summary_content = ttk.Frame(summary_frame, style='Card.TFrame')
        summary_content.pack(fill='x', padx=25, pady=15)
        
        self.total_transactions_var = tk.StringVar(value="0")
        self.total_items_sold_var = tk.StringVar(value="0")
        self.total_revenue_var = tk.StringVar(value="₱0.00")
        
        ttk.Label(summary_content, text="Total Transactions:", style='FieldLabel.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(summary_content, textvariable=self.total_transactions_var, style='CardValue.TLabel').grid(row=0, column=1, sticky='w', padx=(0, 30))
        
        ttk.Label(summary_content, text="Total Items Sold:", style='FieldLabel.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        ttk.Label(summary_content, textvariable=self.total_items_sold_var, style='CardValue.TLabel').grid(row=0, column=3, sticky='w', padx=(0, 30))
        
        ttk.Label(summary_content, text="Total Revenue:", style='FieldLabel.TLabel').grid(row=0, column=4, sticky='w', padx=(0, 10))
        ttk.Label(summary_content, textvariable=self.total_revenue_var, style='CardValue.TLabel').grid(row=0, column=5, sticky='w')
        
        print("Stock history interface created successfully")  # Debug print

    def delete_stock_history(self):
        """Delete selected stock history records"""
        if not hasattr(self, 'stock_history_tree'):
            messagebox.showwarning("Warning", "Please navigate to stock history first.")
            return
            
        selection = self.stock_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select one or more stock history records to delete.")
            return
        
        # Get selected items info for confirmation
        selected_items = []
        for item_id in selection:
            item = self.stock_history_tree.item(item_id)
            values = item['values']
            selected_items.append({
                'sales_id': values[0],  # ID column (hidden)
                'date': values[1],
                'transaction_id': values[3],
                'product_name': values[4],
                'movement_type': values[7]
            })
        
        # Confirmation dialog
        if len(selected_items) == 1:
            item = selected_items[0]
            message = (f"Are you sure you want to delete this stock history record?\n\n"
                      f"Date: {item['date']}\n"
                      f"Transaction ID: {item['transaction_id']}\n"
                      f"Product: {item['product_name']}\n"
                      f"Type: {item['movement_type']}\n\n"
                      f"⚠️ Warning: This action cannot be undone!")
        else:
            message = (f"Are you sure you want to delete {len(selected_items)} stock history records?\n\n"
                      f"⚠️ Warning: This action cannot be undone!")
        
        if not messagebox.askyesno("Confirm Delete", message):
            return
        
        try:
            deleted_count = 0
            failed_deletions = []
            
            for item in selected_items:
                sales_id = item['sales_id']
                transaction_id = item['transaction_id']
                
                try:
                    # Check if this is a sales record (not an initial stock record)
                    if transaction_id != 'INITIAL':
                        # Get the sale details before deletion to potentially restore stock
                        self.cursor.execute('''
                            SELECT product_id, quantity, product_name 
                            FROM sales 
                            WHERE id = ?
                        ''', (sales_id,))
                        sale_details = self.cursor.fetchone()
                        
                        if sale_details:
                            product_id, quantity, product_name = sale_details
                            
                            # Ask if user wants to restore stock to inventory
                            restore_stock = messagebox.askyesno(
                                "Restore Stock", 
                                f"Do you want to restore {quantity} units of '{product_name}' back to inventory?\n\n"
                                f"This will add {quantity} units to the current stock level."
                            )
                            
                            # Delete the sales record
                            self.cursor.execute('DELETE FROM sales WHERE id = ?', (sales_id,))
                            
                            if restore_stock:
                                # Add stock back to the product
                                self.cursor.execute('''
                                    UPDATE products 
                                    SET stock = stock + ? 
                                    WHERE product_id = ?
                                ''', (quantity, product_id))
                                
                                # Record the stock restoration in stock_movements table
                                self.cursor.execute('''
                                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                               reference_id, reason, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (product_id, product_name, 'IN', quantity, 
                                      f"RESTORE_{sales_id}", 'SALE_DELETION', 
                                      f'Stock restored due to deletion of sale record {transaction_id}'))
                        else:
                            # Sales record not found, just continue
                            pass
                    else:
                        # This is an initial stock record, just inform user
                        messagebox.showinfo("Info", 
                                          f"Cannot delete initial stock record for {item['product_name']}. "
                                          f"These records are created when products are first added.")
                        continue
                    
                    deleted_count += 1
                    
                except sqlite3.Error as e:
                    failed_deletions.append(f"Transaction {transaction_id}: {str(e)}")
                    continue
            
            # Commit the changes
            self.conn.commit()
            
            # Show results
            if deleted_count > 0:
                if failed_deletions:
                    message = (f"Successfully deleted {deleted_count} record(s).\n\n"
                              f"Failed to delete {len(failed_deletions)} record(s):\n" + 
                              "\n".join(failed_deletions))
                    messagebox.showwarning("Partial Success", message)
                else:
                    messagebox.showinfo("Success", f"Successfully deleted {deleted_count} stock history record(s)!")
            else:
                if failed_deletions:
                    message = "Failed to delete records:\n" + "\n".join(failed_deletions)
                    messagebox.showerror("Error", message)
                else:
                    messagebox.showinfo("Info", "No records were deleted.")
            
            # Refresh the display
            self.refresh_stock_history()
            
            # Refresh inventory if it's visible (in case stock was restored)
            if hasattr(self, 'inventory_frame') and self.inventory_frame and self.inventory_frame.winfo_viewable():
                self.refresh_products()
                
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete stock history: {str(e)}")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Unexpected error occurred: {str(e)}")

    def create_services_interface(self):
        """Create the services interface"""
        self.services_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.services_frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Services", style='PageTitle.TLabel').pack(side='left')
        
        # Content placeholder
        content_frame = ttk.Frame(self.services_frame, style='Content.TFrame')
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        ttk.Label(content_frame, text="Services management will be displayed here", 
                 style='Placeholder.TLabel').pack(expand=True)

    # Database helper methods
    def get_total_products(self):
        self.cursor.execute('SELECT COUNT(*) FROM products')
        return self.cursor.fetchone()[0]

    def get_total_sales(self):
        self.cursor.execute('SELECT SUM(total) FROM sales')
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def get_low_stock_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM products WHERE stock < 10')
        return self.cursor.fetchone()[0]

    def get_recent_sales_count(self):
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        self.cursor.execute('SELECT COUNT(*) FROM sales WHERE sale_date >= ?', (seven_days_ago,))
        return self.cursor.fetchone()[0]

    # Product management methods (from original code)
    def add_product(self):
        try:
            dialog = ProductDialog(self.root, "Add Product")
            if dialog.result:
                print(f"Dialog result: {dialog.result}")  
                
                # Validate required fields
                if not dialog.result.get('name'):
                    messagebox.showerror("Error", "Product name is required!")
                    return
                    
                if not dialog.result.get('product_id'):
                    messagebox.showerror("Error", "Product ID is required!")
                    return
                
                # Check if product_id already exists
                self.cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', 
                                  (dialog.result['product_id'],))
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Product ID already exists! Please use a unique Product ID.")
                    return
                
                # Insert the product
                self.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, product_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], 
                      dialog.result['price'], 
                      dialog.result['stock'],
                      dialog.result['category'], 
                      dialog.result['product_id']))
                
                # Record initial stock addition
                if dialog.result['stock'] > 0:
                    self.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                   reference_id, reason, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (dialog.result['product_id'], dialog.result['name'], 'IN', 
                          dialog.result['stock'], 'INITIAL', 'INITIAL_STOCK', 
                          'Initial stock when product was added to inventory'))
                
                self.conn.commit()
                messagebox.showinfo("Success", f"Product '{dialog.result['name']}' added successfully!")
                
                # Refresh inventory display if we're on the inventory page
                if hasattr(self, 'inventory_frame') and self.inventory_frame and self.inventory_frame.winfo_viewable():
                    self.refresh_products()
                
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Product ID already exists or constraint violation: {str(e)}")
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            print(f"Exception in add_product: {e}")  

    def edit_product(self):
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
            
        old_stock = product[3]  # Get current stock before editing
        
        dialog = ProductDialog(self.root, "Edit Product", product)
        if dialog.result:
            try:
                new_stock = dialog.result['stock']
                stock_difference = new_stock - old_stock
                
                self.cursor.execute('''
                    UPDATE products SET name = ?, price = ?, stock = ?, category = ?, product_id = ?
                    WHERE id = ?
                ''', (dialog.result['name'], dialog.result['price'], dialog.result['stock'],
                      dialog.result['category'], dialog.result['product_id'], product_id))
                
                # Record stock movement if stock changed
                if stock_difference != 0:
                    movement_type = 'IN' if stock_difference > 0 else 'OUT'
                    reason = 'STOCK_ADJUSTMENT'
                    notes = f"Stock adjusted from {old_stock} to {new_stock} (difference: {stock_difference:+d})"
                    
                    self.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                   reference_id, reason, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (dialog.result['product_id'], dialog.result['name'], movement_type, 
                          abs(stock_difference), f"EDIT_{product_id}", reason, notes))
                
                self.conn.commit()
                self.refresh_products()
                messagebox.showinfo("Success", "Product updated successfully!")
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Product ID already exists!")
                self.conn.rollback()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update product: {str(e)}")
                self.conn.rollback()

    def delete_product(self):
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            try:
                # First get the product_id for the sales deletion
                self.cursor.execute('SELECT product_id FROM products WHERE id = ?', (product_id,))
                product_code = self.cursor.fetchone()
                
                if product_code:
                    # Delete related sales records first
                    self.cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_code[0],))
                    # Delete related stock movements
                    self.cursor.execute('DELETE FROM stock_movements WHERE product_id = ?', (product_code[0],))
                    
                # Delete the product
                self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.conn.commit()
                self.refresh_products()
                messagebox.showinfo("Success", "Product deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                self.conn.rollback()

    def refresh_products(self):
        """Refresh the inventory display"""
        if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
            try:
                # Clear existing items
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                # Get all products from database
                self.cursor.execute('SELECT id, name, price, stock, category, product_id FROM products ORDER BY name')
                products = self.cursor.fetchall()
                
                # Insert products into treeview
                for product in products:
                    self.inventory_tree.insert('', 'end', values=(
                        product[0],  # id
                        product[1],  # name
                        f"₱{product[2]:.2f}",  # price
                        product[3],  # stock
                        product[4],  # category
                        product[5]   # product_id
                    ))
                    
                print(f"Loaded {len(products)} products into inventory")  # Debug print
                
            except Exception as e:
                print(f"Error refreshing products: {e}")
                messagebox.showerror("Error", f"Failed to load products: {str(e)}")
        else:
            print("Inventory tree not available yet")  # Debug print

    def refresh_stock_history(self):
        """Refresh the stock history display"""
        if not hasattr(self, 'stock_history_tree') or not self.stock_history_tree.winfo_exists():
            print("Stock history tree not available yet")
            return
            
        try:
            # Clear existing items
            for item in self.stock_history_tree.get_children():
                self.stock_history_tree.delete(item)
            
            # Build query based on filters
            date_filter = self.date_filter_var.get() if hasattr(self, 'date_filter_var') else 'All Time'
            category_filter = self.stock_category_var.get() if hasattr(self, 'stock_category_var') else 'All Categories'
            movement_filter = self.movement_type_var.get() if hasattr(self, 'movement_type_var') else 'All Movements'
            
            # Base query for sales (stock out) - now including the ID for deletion
            base_query = '''
                SELECT 
                    s.id,
                    DATE(s.sale_date) as sale_date,
                    TIME(s.sale_date) as sale_time,
                    s.transaction_id,
                    s.product_name,
                    s.product_id,
                    s.product_category,
                    'Sale (Out)' as movement_type,
                    s.quantity,
                    s.price,
                    s.total,
                    p.stock as current_stock
                FROM sales s
                LEFT JOIN products p ON s.product_id = p.product_id
                WHERE 1=1
            '''
            
            params = []
            
            # Add date filter
            if date_filter == 'Today':
                base_query += " AND DATE(s.sale_date) = DATE('now')"
            elif date_filter == 'Last 7 Days':
                base_query += " AND s.sale_date >= datetime('now', '-7 days')"
            elif date_filter == 'Last 30 Days':
                base_query += " AND s.sale_date >= datetime('now', '-30 days')"
            elif date_filter == 'Last 90 Days':
                base_query += " AND s.sale_date >= datetime('now', '-90 days')"
            
            # Add category filter
            if category_filter != 'All Categories':
                base_query += " AND s.product_category = ?"
                params.append(category_filter)
            
            # Add movement type filter
            if movement_filter == 'Sales (Out)':
                # Only show sales - this is the default query
                pass
            elif movement_filter == 'Stock Added (In)':
                # For now, we'll show when products were initially added
                base_query = '''
                    SELECT 
                        p.id,
                        DATE(p.date_added) as sale_date,
                        TIME(p.date_added) as sale_time,
                        'INITIAL' as transaction_id,
                        p.name as product_name,
                        p.product_id,
                        p.category as product_category,
                        'Stock Added (In)' as movement_type,
                        p.stock as quantity,
                        p.price,
                        (p.stock * p.price) as total,
                        p.stock as current_stock
                    FROM products p
                    WHERE 1=1
                '''
                if category_filter != 'All Categories':
                    base_query += " AND p.category = ?"
            
            base_query += " ORDER BY sale_date DESC, sale_time DESC"
            
            # Execute query
            self.cursor.execute(base_query, params)
            history_data = self.cursor.fetchall()
            
            # Insert data into treeview
            total_transactions = 0
            total_items_sold = 0
            total_revenue = 0
            
            for record in history_data:
                # Format the data for display
                record_id = record[0] if record[0] else 0
                date_str = record[1] if record[1] else 'N/A'
                time_str = record[2] if record[2] else 'N/A'
                transaction_id = record[3] if record[3] else 'N/A'
                product_name = record[4] if record[4] else 'Unknown Product'
                product_id = record[5] if record[5] else 'N/A'
                category = record[6] if record[6] else 'N/A'
                movement_type = record[7] if record[7] else 'N/A'
                quantity = int(record[8]) if record[8] else 0
                unit_price = float(record[9]) if record[9] else 0.0
                total_amount = float(record[10]) if record[10] else 0.0
                current_stock = int(record[11]) if record[11] else 0
                
                # Insert into treeview (ID is first but hidden)
                self.stock_history_tree.insert('', 'end', values=(
                    record_id,  # Hidden ID for deletion
                    date_str,
                    time_str,
                    transaction_id,
                    product_name,
                    product_id,
                    category,
                    movement_type,
                    f"{quantity:,}",  # Format quantity with commas
                    f"₱{unit_price:.2f}",
                    f"₱{total_amount:.2f}",
                    f"{current_stock:,}"
                ))
                
                # Update summary statistics
                total_transactions += 1
                if movement_type == 'Sale (Out)':
                    total_items_sold += quantity
                    total_revenue += total_amount
            
            # Update summary display
            if hasattr(self, 'total_transactions_var'):
                self.total_transactions_var.set(f"{total_transactions:,}")
                self.total_items_sold_var.set(f"{total_items_sold:,}")
                self.total_revenue_var.set(f"₱{total_revenue:,.2f}")
                
            print(f"Loaded {len(history_data)} stock movement records")  # Debug print
            
        except Exception as e:
            print(f"Error refreshing stock history: {e}")
            messagebox.showerror("Error", f"Failed to load stock history: {str(e)}")

    def filter_stock_history(self, event=None):
        """Filter stock history based on selected criteria"""
        self.refresh_stock_history()

    # CRITICAL INVENTORY METHODS - These handle the actual stock updates during checkout

    def record_sale(self, cart_items, payment_method='Cash'):
        """
        Record a sale transaction and update inventory
        
        Args:
            cart_items: List of dictionaries with sale data
            payment_method: Payment method used
            
        Returns:
            tuple: (success, transaction_id_or_error_message)
        """
        try:
            # Generate unique transaction ID
            transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            total_amount = 0
            sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Start transaction
            self.cursor.execute('BEGIN TRANSACTION')
            
            # Validate stock availability for all items first
            for item in cart_items:
                if not self.check_stock_availability(item['product_id'], item['quantity']):
                    self.cursor.execute('ROLLBACK')
                    return False, f"Insufficient stock for {item['product_name']}"
            
            # Process each item in the cart
            for item in cart_items:
                item_total = item['quantity'] * item['unit_price']
                total_amount += item_total
                
                # Insert into sales table
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, product_category, 
                                     quantity, price, total, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (transaction_id, item['product_id'], item['product_name'], 
                      item.get('category', 'N/A'), item['quantity'], item['unit_price'], 
                      item_total, sale_date))
                
                # Update product stock - CRITICAL PART
                self.cursor.execute('''
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE product_id = ?
                ''', (item['quantity'], item['product_id']))
                
                # Verify the stock was actually updated
                self.cursor.execute('''
                    SELECT stock FROM products WHERE product_id = ?
                ''', (item['product_id'],))
                
                updated_stock = self.cursor.fetchone()
                if updated_stock is None:
                    self.cursor.execute('ROLLBACK')
                    return False, f"Product {item['product_id']} not found in inventory"
                
                if updated_stock[0] < 0:
                    self.cursor.execute('ROLLBACK')
                    return False, f"Transaction would result in negative stock for {item['product_name']}"
                
                # Record stock movement for tracking
                self.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                               reference_id, reason, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item['product_id'], item['product_name'], 'OUT', 
                      item['quantity'], transaction_id, 'SALE', 
                      f'Sold {item["quantity"]} units. New stock: {updated_stock[0]}'))
            
            # Insert into transactions table
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, total_amount, payment_method, transaction_date)
                VALUES (?, ?, ?, ?)
            ''', (transaction_id, total_amount, payment_method, sale_date))
            
            # Commit the transaction
            self.cursor.execute('COMMIT')
            
            # Refresh inventory display if visible
            if hasattr(self, 'inventory_frame') and self.inventory_frame and self.inventory_frame.winfo_viewable():
                self.refresh_products()
            
            print(f"Sale recorded successfully. Transaction ID: {transaction_id}, Total: ₱{total_amount:.2f}")
            return True, transaction_id
            
        except sqlite3.Error as e:
            self.cursor.execute('ROLLBACK')
            print(f"Database error in record_sale: {e}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            self.cursor.execute('ROLLBACK')
            print(f"Unexpected error in record_sale: {e}")
            return False, f"Unexpected error: {str(e)}"

    def check_stock_availability(self, product_id, quantity):
        """
        Check if enough stock is available for a product
        
        Args:
            product_id: Product identifier
            quantity: Quantity to check
            
        Returns:
            bool: True if stock is available, False otherwise
        """
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

    def get_product_by_id(self, product_id):
        """
        Get product details by product_id
        
        Args:
            product_id: Product identifier
            
        Returns:
            tuple: Product details (name, price, stock, category) or None
        """
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

    def get_all_products(self):
        """
        Get all products from the database
        
        Returns:
            list: List of all products
        """
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

    def update_product_stock(self, product_id, new_stock, reason='Manual Update'):
        """
        Update product stock manually
        
        Args:
            product_id: Product identifier
            new_stock: New stock quantity
            reason: Reason for stock update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current stock
            self.cursor.execute('SELECT stock, name FROM products WHERE product_id = ?', (product_id,))
            result = self.cursor.fetchone()
            if not result:
                return False
            
            old_stock, product_name = result
            stock_difference = new_stock - old_stock
            
            # Update the stock
            self.cursor.execute('''
                UPDATE products 
                SET stock = ? 
                WHERE product_id = ?
            ''', (new_stock, product_id))
            
            # Record stock movement
            if stock_difference != 0:
                movement_type = 'IN' if stock_difference > 0 else 'OUT'
                self.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                               reference_id, reason, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product_id, product_name, movement_type, 
                      abs(stock_difference), f"MANUAL_{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                      reason, f'Stock updated from {old_stock} to {new_stock}'))
            
            self.conn.commit()
            
            # Refresh displays
            if hasattr(self, 'inventory_frame') and self.inventory_frame and self.inventory_frame.winfo_viewable():
                self.refresh_products()
            
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating stock for {product_id}: {e}")
            return False

    def get_recent_sales(self, limit=10):
        """Get recent sales for display"""
        try:
            self.cursor.execute('''
                SELECT sale_date, product_name, product_id, product_category, quantity, total
                FROM sales 
                ORDER BY sale_date DESC 
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting recent sales: {e}")
            return []

    def get_sales_summary(self, date_from=None, date_to=None):
        """
        Get sales summary for a date range
        
        Args:
            date_from: Start date (optional)
            date_to: End date (optional)
            
        Returns:
            dict: Sales summary data
        """
        try:
            base_query = '''
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(quantity) as total_items_sold,
                    SUM(total) as total_revenue
                FROM sales
            '''
            
            params = []
            if date_from and date_to:
                base_query += ' WHERE DATE(sale_date) BETWEEN ? AND ?'
                params = [date_from, date_to]
            elif date_from:
                base_query += ' WHERE DATE(sale_date) >= ?'
                params = [date_from]
            elif date_to:
                base_query += ' WHERE DATE(sale_date) <= ?'
                params = [date_to]
            
            self.cursor.execute(base_query, params)
            result = self.cursor.fetchone()
            
            return {
                'total_transactions': result[0] if result[0] else 0,
                'total_items_sold': result[1] if result[1] else 0,
                'total_revenue': result[2] if result[2] else 0.0
            }
            
        except sqlite3.Error as e:
            print(f"Error getting sales summary: {e}")
            return {
                'total_transactions': 0,
                'total_items_sold': 0,
                'total_revenue': 0.0
            }

    def validate_transaction(self, cart_items):
        """
        Validate a transaction before processing
        
        Args:
            cart_items: List of items in the cart
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not cart_items:
            return False, "Cart is empty"
        
        for item in cart_items:
            # Check required fields
            required_fields = ['product_id', 'product_name', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item or item[field] is None:
                    return False, f"Missing required field: {field}"
            
            # Check quantity is positive
            if item['quantity'] <= 0:
                return False, f"Invalid quantity for {item['product_name']}"
            
            # Check price is positive
            if item['unit_price'] <= 0:
                return False, f"Invalid price for {item['product_name']}"
            
            # Check stock availability
            if not self.check_stock_availability(item['product_id'], item['quantity']):
                current_stock = self.get_current_stock(item['product_id'])
                return False, f"Insufficient stock for {item['product_name']}. Available: {current_stock}, Requested: {item['quantity']}"
        
        return True, "Valid transaction"

    def get_current_stock(self, product_id):
        """
        Get current stock for a product
        
        Args:
            product_id: Product identifier
            
        Returns:
            int: Current stock quantity
        """
        try:
            self.cursor.execute('SELECT stock FROM products WHERE product_id = ?', (product_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error getting current stock for {product_id}: {e}")
            return 0

    def process_return(self, transaction_id, return_items):
        """
        Process a product return and update inventory
        
        Args:
            transaction_id: Original transaction ID
            return_items: List of items being returned
            
        Returns:
            tuple: (success, message)
        """
        try:
            return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return_transaction_id = f"RTN{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.cursor.execute('BEGIN TRANSACTION')
            
            for item in return_items:
                # Add stock back to inventory
                self.cursor.execute('''
                    UPDATE products 
                    SET stock = stock + ? 
                    WHERE product_id = ?
                ''', (item['quantity'], item['product_id']))
                
                # Record the return in sales table (negative quantity)
                self.cursor.execute('''
                    INSERT INTO sales (transaction_id, product_id, product_name, product_category, 
                                     quantity, price, total, sale_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (return_transaction_id, item['product_id'], item['product_name'], 
                      item.get('category', 'N/A'), -item['quantity'], item['unit_price'], 
                      -item['total'], return_date))
                
                # Record stock movement
                self.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                               reference_id, reason, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item['product_id'], item['product_name'], 'IN', 
                      item['quantity'], return_transaction_id, 'RETURN', 
                      f'Product returned from transaction {transaction_id}'))
            
            self.cursor.execute('COMMIT')
            
            # Refresh displays
            if hasattr(self, 'inventory_frame') and self.inventory_frame and self.inventory_frame.winfo_viewable():
                self.refresh_products()
            
            return True, f"Return processed successfully. Return ID: {return_transaction_id}"
            
        except sqlite3.Error as e:
            self.cursor.execute('ROLLBACK')
            return False, f"Database error: {str(e)}"
        except Exception as e:
            self.cursor.execute('ROLLBACK')
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