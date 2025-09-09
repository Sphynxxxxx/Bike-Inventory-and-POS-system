import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

class DashboardModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the simplified dashboard without charts"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Dashboard", style='PageTitle.TLabel').pack(side='left')
        
        # Stats cards container
        stats_container = ttk.Frame(self.frame, style='Content.TFrame')
        stats_container.pack(fill='x', padx=30, pady=(0, 20))
        
        # Create stats cards
        self.create_dashboard_stats_cards(stats_container)
        
        # Main content area with tables only
        main_content = ttk.Frame(self.frame, style='Content.TFrame')
        main_content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Quick Actions Section
        quick_actions_frame = ttk.Frame(main_content, style='Card.TFrame')
        quick_actions_frame.pack(fill='x', pady=(0, 20))
        
        # Header for quick actions
        qa_header = ttk.Frame(quick_actions_frame, style='Card.TFrame')
        qa_header.pack(fill='x', padx=20, pady=(15, 10))
        ttk.Label(qa_header, text="Quick Actions", style='SectionTitle.TLabel').pack(side='left')
        
        # Quick action buttons
        qa_content = ttk.Frame(quick_actions_frame, style='Card.TFrame')
        qa_content.pack(fill='x', padx=20, pady=(0, 15))
        
        ttk.Button(qa_content, text="🛒 New Sale", command=self.main_app.show_sales_entry,
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(qa_content, text="📦 Add Product", command=self.main_app.add_product,
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(qa_content, text="📊 View Statistics", command=self.main_app.show_statistics,
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(qa_content, text="📈 Stock History", command=self.main_app.show_stock_history,
                  style='Secondary.TButton').pack(side='left')
        
        # Tables row 
        tables_row = ttk.Frame(main_content, style='Content.TFrame')
        tables_row.pack(fill='both', expand=True)
        
        # Left table - Recent Sales
        recent_sales_frame = ttk.Frame(tables_row, style='Card.TFrame')
        recent_sales_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_recent_sales_table(recent_sales_frame)
        
        # Middle table - Low Stock Alert
        stock_alert_frame = ttk.Frame(tables_row, style='Card.TFrame')
        stock_alert_frame.pack(side='left', fill='both', expand=True, padx=(5, 5))
        self.create_stock_alert_table(stock_alert_frame)
        
        # Right section - Today's Summary
        summary_frame = ttk.Frame(tables_row, style='Card.TFrame')
        summary_frame.pack(side='right', fill='y', padx=(10, 0))
        self.create_today_summary(summary_frame)
        
        return self.frame

    def create_dashboard_stats_cards(self, parent):
        """Create modern statistics cards"""
        # Get statistics from database
        total_sales_count = self.main_app.get_total_sales_count()
        total_revenue = self.main_app.get_total_sales()
        total_products = self.main_app.get_total_products()
        total_stock_items = self.main_app.get_total_stock_items()
        
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

    def create_today_summary(self, parent):
        """Create today's sales summary"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Today's Summary", style='SectionTitle.TLabel').pack()
        
        # Content
        content_frame = ttk.Frame(parent, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Get today's data
        today_data = self.main_app.get_today_summary()
        
        # Today's Sales
        sales_frame = ttk.Frame(content_frame, style='Card.TFrame')
        sales_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(sales_frame, text="Sales Today", style='InsightTitle.TLabel').pack(anchor='w')
        ttk.Label(sales_frame, text=str(today_data['sales_count']), style='InsightValue.TLabel').pack(anchor='w')
        
        # Today's Revenue
        revenue_frame = ttk.Frame(content_frame, style='Card.TFrame')
        revenue_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(revenue_frame, text="Revenue Today", style='InsightTitle.TLabel').pack(anchor='w')
        ttk.Label(revenue_frame, text=f"₱{today_data['revenue']:.2f}", style='InsightValue.TLabel').pack(anchor='w')
        
        # Items Sold
        items_frame = ttk.Frame(content_frame, style='Card.TFrame')
        items_frame.pack(fill='x')
        
        ttk.Label(items_frame, text="Items Sold", style='InsightTitle.TLabel').pack(anchor='w')
        ttk.Label(items_frame, text=str(today_data['items_sold']), style='InsightValue.TLabel').pack(anchor='w')

    def create_recent_sales_table(self, parent):
        """Create recent sales table - UPDATED to show customer name"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Recent Sales", style='SectionTitle.TLabel').pack(side='left')
        ttk.Label(header_frame, text="View More →", style='ViewMore.TLabel').pack(side='right')
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('#', 'Date', 'Product', 'Customer', 'Amount')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=6)
        
        # Configure columns
        tree.heading('#', text='#')
        tree.heading('Date', text='Date')
        tree.heading('Product', text='Product')
        tree.heading('Customer', text='Customer')
        tree.heading('Amount', text='Amount')
        
        tree.column('#', width=30)
        tree.column('Date', width=70)
        tree.column('Product', width=100)
        tree.column('Customer', width=80)
        tree.column('Amount', width=80)
        
        # Get recent sales data
        recent_sales = self.main_app.get_recent_sales(5)
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
                sale[1][:12] + "..." if len(sale[1]) > 12 else sale[1],  # product_name
                sale[3][:10] + "..." if sale[3] and len(sale[3]) > 10 else (sale[3] or "N/A"),  # customer_name
                f"₱{sale[5]:,.2f}"  # total
            ))
        
        tree.pack(fill='both', expand=True)

    def show_all_stock_alerts(self):
        """Show all low stock products in a new window"""
        # Create new window
        alert_window = tk.Toplevel(self.frame)
        alert_window.title("Stock Alerts")
        alert_window.geometry("800x600")
        alert_window.transient(self.frame)
        
        # Center the window
        alert_window.update_idletasks()
        x = (alert_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (alert_window.winfo_screenheight() // 2) - (600 // 2)
        alert_window.geometry(f"800x600+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(alert_window, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(main_frame, text="All Stock Alerts", style='PageTitle.TLabel').pack(pady=(0, 20))
        
        # Table frame
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        # Create treeview
        columns = ('SKU', 'Product', 'Category', 'Current Stock', 'Min Stock', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns
        tree.heading('SKU', text='SKU')
        tree.heading('Product', text='Product Name')
        tree.heading('Category', text='Category')
        tree.heading('Current Stock', text='Current Stock')
        tree.heading('Min Stock', text='Min Stock')
        tree.heading('Status', text='Status')
        
        tree.column('SKU', width=100)
        tree.column('Product', width=200)
        tree.column('Category', width=150)
        tree.column('Current Stock', width=100)
        tree.column('Min Stock', width=100)
        tree.column('Status', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Get all low stock products
        low_stock_products = self.main_app.get_low_stock_products()
        
        # Insert data
        for product in low_stock_products:
            status = "OUT OF STOCK" if product[3] == 0 else "LOW STOCK"
            status_color = 'red' if product[3] == 0 else 'orange'
            
            tree.insert('', 'end', values=(
                product[4],  # SKU/product_id
                product[1],  # name
                product[2] if len(product) > 4 else "General",  # category
                product[3],  # current stock
                5,  # minimum stock threshold (you may want to make this configurable)
                status
            ), tags=(status_color,))
        
        # Configure tag colors
        tree.tag_configure('red', foreground='#ef4444')
        tree.tag_configure('orange', foreground='#f97316')
        
        # Add close button
        ttk.Button(main_frame, text="Close", command=alert_window.destroy,
                  style='Secondary.TButton').pack(pady=20)

    def create_stock_alert_table(self, parent):
        """Create stock alert table"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Stock Alert", style='SectionTitle.TLabel').pack(side='left')
        view_more_label = ttk.Label(header_frame, text="View More →", style='ViewMore.TLabel', cursor="hand2")
        view_more_label.pack(side='right')
        view_more_label.bind('<Button-1>', lambda e: self.show_all_stock_alerts())
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Get low stock products
        low_stock_products = self.main_app.get_low_stock_products()
        
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

    def refresh(self):
        """Refresh dashboard data"""
        if self.frame:
            # Destroy and recreate the dashboard
            self.frame.destroy()
            return self.create_interface()
        return None