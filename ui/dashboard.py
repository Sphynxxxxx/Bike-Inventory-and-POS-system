import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import numpy as np
import sqlite3

class DashboardModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the dashboard with product stock chart"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Sales Dashboard", style='PageTitle.TLabel').pack(side='left')
        
        # Stats cards container
        stats_container = ttk.Frame(self.frame, style='Content.TFrame')
        stats_container.pack(fill='x', padx=30, pady=(0, 20))
        
        # Create stats cards
        self.create_dashboard_stats_cards(stats_container)
        
        # Main content area
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
        
        # Chart and Tables row
        content_row = ttk.Frame(main_content, style='Content.TFrame')
        content_row.pack(fill='both', expand=True)
        
        # Left side - Product Stock Chart
        chart_frame = ttk.Frame(content_row, style='Card.TFrame')
        chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_product_stock_chart(chart_frame)
        
        # Right side - Tables
        tables_frame = ttk.Frame(content_row, style='Content.TFrame')
        tables_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Recent Sales Table
        recent_sales_frame = ttk.Frame(tables_frame, style='Card.TFrame')
        recent_sales_frame.pack(fill='both', expand=True, pady=(0, 10))
        self.create_recent_sales_table(recent_sales_frame)
        
        # Stock Alert and Summary row
        bottom_tables = ttk.Frame(tables_frame, style='Content.TFrame')
        bottom_tables.pack(fill='x', pady=(10, 0))
        
        # Stock Alert Table
        stock_alert_frame = ttk.Frame(bottom_tables, style='Card.TFrame')
        stock_alert_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        self.create_stock_alert_table(stock_alert_frame)
        
        # Today's Summary
        summary_frame = ttk.Frame(bottom_tables, style='Card.TFrame')
        summary_frame.pack(side='right', fill='y', padx=(5, 0))
        self.create_today_summary(summary_frame)
        
        return self.frame

    def create_product_stock_chart(self, parent):
        """Create a bar chart showing product stock levels"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Product Stock Levels", style='SectionTitle.TLabel').pack(side='left')
        
        # Chart frame
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Get product data
        try:
            self.main_app.cursor.execute('''
                SELECT name, stock, id FROM products 
                ORDER BY stock ASC 
                LIMIT 10
            ''')
            products = self.main_app.cursor.fetchall()
            
            if products:
                # Create matplotlib figure
                fig, ax = plt.subplots(figsize=(8, 5))
                fig.patch.set_facecolor('white')
                ax.set_facecolor('white')
                
                # Extract data
                product_names = [product[0][:15] + '...' if len(product[0]) > 15 else product[0] 
                               for product in products]
                stock_levels = [product[1] for product in products]
                
                # Create color map based on stock levels
                colors = []
                for stock in stock_levels:
                    if stock == 0:
                        colors.append('#ef4444')  # Red for out of stock
                    elif stock <= 5:
                        colors.append('#f97316')  # Orange for low stock
                    elif stock <= 10:
                        colors.append('#eab308')  # Yellow for medium stock
                    else:
                        colors.append('#22c55e')  # Green for good stock
                
                # Create horizontal bar chart
                bars = ax.barh(product_names, stock_levels, color=colors, alpha=0.8)
                
                # Customize chart
                ax.set_xlabel('Stock Quantity', fontsize=10, color='#374151')
                ax.set_ylabel('Products', fontsize=10, color='#374151')
                ax.set_title('Product Stock Overview (Lowest 10)', fontsize=12, color='#1f2937', pad=20)
                
                # Add value labels on bars
                for i, (bar, value) in enumerate(zip(bars, stock_levels)):
                    ax.text(value + 0.5, bar.get_y() + bar.get_height()/2, 
                           str(value), va='center', ha='left', fontsize=9, color='#374151')
                
                # Customize grid
                ax.grid(axis='x', alpha=0.3, linestyle='-', linewidth=0.5)
                ax.set_axisbelow(True)
                
                # Remove top and right spines
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#d1d5db')
                ax.spines['bottom'].set_color('#d1d5db')
                
                # Set tick colors
                ax.tick_params(colors='#374151', labelsize=9)
                
                # Adjust layout
                plt.tight_layout()
                
                # Create canvas and add to tkinter
                canvas = FigureCanvasTkAgg(fig, chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                
                # Add legend
                legend_frame = ttk.Frame(parent, style='Card.TFrame')
                legend_frame.pack(fill='x', padx=20, pady=(0, 15))
                
                legend_items = [
                    ("● Out of Stock (0)", "#ef4444"),
                    ("● Low Stock (1-5)", "#f97316"),
                    ("● Medium Stock (6-10)", "#eab308"),
                    ("● Good Stock (11+)", "#22c55e")
                ]
                
                for i, (text, color) in enumerate(legend_items):
                    legend_label = ttk.Label(legend_frame, text=text, foreground=color, 
                                           font=('Arial', 8), background='#ffffff')
                    legend_label.pack(side='left', padx=(0, 15))
                
            else:
                # No products message
                no_data_label = ttk.Label(chart_frame, text="No products available", 
                                        style='NoData.TLabel')
                no_data_label.pack(expand=True)
                
        except Exception as e:
            print(f"Error creating stock chart: {e}")
            error_label = ttk.Label(chart_frame, text="Error loading chart data", 
                                  style='NoData.TLabel')
            error_label.pack(expand=True)

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
        """Create recent sales table - FIXED amount formatting to always show proper decimals"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Recent Sales", style='SectionTitle.TLabel').pack(side='left')
        view_more_label = ttk.Label(header_frame, text="", style='ViewMore.TLabel', cursor="hand2")
        view_more_label.pack(side='right')
        view_more_label.bind('<Button-1>', lambda e: self.show_all_recent_sales())
        # Add hover effects for better UX
        view_more_label.bind('<Enter>', lambda e: view_more_label.configure(foreground='#2563eb'))
        view_more_label.bind('<Leave>', lambda e: view_more_label.configure(foreground='#3b82f6'))
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('#', 'Date', 'Product', 'Customer')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=6)
        
        # Configure columns
        tree.heading('#', text='#', anchor='center')
        tree.heading('Date', text='Date', anchor='center')
        tree.heading('Product', text='Product', anchor='center')
        tree.heading('Customer', text='Customer', anchor='center')
        #tree.heading('Amount', text='Amount')
        
        tree.column('#', width=30, anchor='center')
        tree.column('Date', width=70, anchor='center')
        tree.column('Product', width=100, anchor='center')
        tree.column('Customer', width=80, anchor='center')
        #tree.column('Amount', width=80)
        
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
            
            try:
                total_amount = sale[5]
                if total_amount is None:
                    total_amount = 0.0
                elif isinstance(total_amount, str):
                    total_amount = float(total_amount.replace(',', '').replace('₱', '').strip())
                else:
                    total_amount = float(total_amount)
                
                if total_amount >= 1000:
                    formatted_amount = f"₱{total_amount:,.2f}"  
                else:
                    formatted_amount = f"₱{total_amount:.2f}"   
                    
            except (ValueError, TypeError, IndexError) as e:
                print(f"Error formatting amount for sale {sale}: {e}")
                formatted_amount = "₱0"
            
            tree.insert('', 'end', values=(
                f"{i:02d}",
                formatted_date,
                sale[1][:12] + "..." if len(sale[1]) > 12 else sale[1],  
                sale[3][:10] + "..." if sale[3] and len(sale[3]) > 10 else (sale[3] or "N/A"),
                formatted_amount  # Now properly formatted with consistent decimal places
            ))
        
        tree.pack(fill='both', expand=True)

    def show_all_recent_sales(self):
        """Show all recent sales in a new window"""
        # Create new window
        sales_window = tk.Toplevel(self.frame)
        sales_window.title("All Recent Sales")
        sales_window.geometry("1000x700")
        sales_window.transient(self.frame)
        
        # Center the window
        sales_window.update_idletasks()
        x = (sales_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (sales_window.winfo_screenheight() // 2) - (700 // 2)
        sales_window.geometry(f"1000x700+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(sales_window, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with controls
        header_frame = ttk.Frame(main_frame, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="All Recent Sales", style='PageTitle.TLabel').pack(side='left')
        
        # Filter controls
        filter_frame = ttk.Frame(header_frame, style='Content.TFrame')
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame, text="Show:", style='Content.TLabel').pack(side='left', padx=(0, 5))
        
        # Limit dropdown
        self.sales_limit_var = tk.StringVar(value="50")
        limit_combo = ttk.Combobox(filter_frame, textvariable=self.sales_limit_var, 
                                  values=["25", "50", "100", "200", "All"], 
                                  width=8, state="readonly")
        limit_combo.pack(side='left', padx=(0, 10))
        limit_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_sales_table(tree))
        
        ttk.Button(filter_frame, text="Refresh", 
                  command=lambda: self.refresh_sales_table(tree),
                  style='Secondary.TButton').pack(side='left')
        
        # Stats frame
        stats_frame = ttk.Frame(main_frame, style='Card.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Table frame
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create treeview
        columns = ('Sale ID', 'Date', 'Time', 'Product Name', 'Customer', 'Quantity', 'Unit Price', 'Total', 'Payment Method')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns
        tree.heading('Sale ID', text='Sale ID')
        tree.heading('Date', text='Date')
        tree.heading('Time', text='Time')
        tree.heading('Product Name', text='Product Name')
        tree.heading('Customer', text='Customer')
        tree.heading('Quantity', text='Qty')
        tree.heading('Unit Price', text='Unit Price')
        tree.heading('Total', text='Total')
        tree.heading('Payment Method', text='Payment')
        
        tree.column('Sale ID', width=80)
        tree.column('Date', width=100)
        tree.column('Time', width=80)
        tree.column('Product Name', width=200)
        tree.column('Customer', width=120)
        tree.column('Quantity', width=60)
        tree.column('Unit Price', width=100)
        tree.column('Total', width=100)
        tree.column('Payment Method', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load initial data
        self.refresh_sales_table(tree)
        
        # Summary stats in stats frame
        self.update_sales_stats(stats_frame, tree)
        
        # Add close button
        button_frame = ttk.Frame(main_frame, style='Content.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Close", command=sales_window.destroy,
                  style='Secondary.TButton').pack(side='right')
        ttk.Button(button_frame, text="Export to CSV", 
                  command=lambda: self.export_sales_data(tree),
                  style='Primary.TButton').pack(side='right', padx=(0, 10))
    
    def refresh_sales_table(self, tree):
        """Refresh the sales table with current data - Fixed amount formatting"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Get limit
        limit = self.sales_limit_var.get()
        
        # Get all recent sales data
        try:
            if limit == "All":
                query = '''
                    SELECT 
                        id,
                        sale_date,
                        product_name,
                        customer_name,
                        quantity,
                        unit_price,
                        total,
                        payment_method
                    FROM sales
                    ORDER BY sale_date DESC
                '''
                self.main_app.cursor.execute(query)
            else:
                query = '''
                    SELECT 
                        id,
                        sale_date,
                        product_name,
                        customer_name,
                        quantity,
                        unit_price,
                        total,
                        payment_method
                    FROM sales
                    ORDER BY sale_date DESC
                    LIMIT ?
                '''
                self.main_app.cursor.execute(query, (int(limit),))
            
            sales = self.main_app.cursor.fetchall()
            
            # Insert data
            for sale in sales:
                try:
                    # Format date and time - handle different datetime formats
                    if isinstance(sale[1], str) and sale[1]:
                        if ' ' in sale[1]:  
                            try:
                                date_time = datetime.strptime(sale[1], '%Y-%m-%d %H:%M:%S')
                                date_str = date_time.strftime('%b %d, %Y')
                                time_str = date_time.strftime('%I:%M %p')
                            except ValueError:
                                try:
                                    date_time = datetime.strptime(sale[1], '%Y-%m-%d %H:%M:%S.%f')
                                    date_str = date_time.strftime('%b %d, %Y')
                                    time_str = date_time.strftime('%I:%M %p')
                                except ValueError:
                                    date_str = str(sale[1])[:10]
                                    time_str = 'N/A'
                        else:  
                            try:
                                date_obj = datetime.strptime(sale[1], '%Y-%m-%d')
                                date_str = date_obj.strftime('%b %d, %Y')
                                time_str = 'N/A'
                            except ValueError:
                                date_str = str(sale[1])[:10]
                                time_str = 'N/A'
                    elif hasattr(sale[1], 'strftime'):  
                        date_str = sale[1].strftime('%b %d, %Y')
                        time_str = sale[1].strftime('%I:%M %p')
                    else:
                        date_str = 'N/A'
                        time_str = 'N/A'
                    
                    # Safe value extraction with defaults
                    sale_id = sale[0] if sale[0] is not None else 0
                    product_name = sale[2] if sale[2] is not None else "N/A"
                    customer_name = sale[3] if sale[3] is not None else "Guest"
                    quantity = sale[4] if sale[4] is not None else 0
                    
                    # Fix unit price formatting
                    try:
                        unit_price = sale[5] if sale[5] is not None else 0.0
                        if isinstance(unit_price, str):
                            unit_price = float(unit_price.replace(',', '').replace('₱', '').strip())
                        else:
                            unit_price = float(unit_price)
                        
                        # Format with comma only for amounts >= 1000
                        if unit_price >= 1000:
                            formatted_unit_price = f"₱{unit_price:,.2f}"
                        else:
                            formatted_unit_price = f"₱{unit_price:.2f}"
                            
                    except (ValueError, TypeError):
                        formatted_unit_price = "₱0.00"
                    
                    # Fix total amount formatting
                    try:
                        total = sale[6] if sale[6] is not None else 0.0
                        if isinstance(total, str):
                            total = float(total.replace(',', '').replace('₱', '').strip())
                        else:
                            total = float(total)
                        
                        # Format with comma only for amounts >= 1000
                        if total >= 1000:
                            formatted_total = f"₱{total:,.2f}"
                        else:
                            formatted_total = f"₱{total:.2f}"
                            
                    except (ValueError, TypeError):
                        formatted_total = "₱0.00"
                    
                    payment_method = sale[7] if sale[7] is not None else "Cash"
                    
                    tree.insert('', 'end', values=(
                        f"#{sale_id:04d}",  # Sale ID
                        date_str,           # Date
                        time_str,           # Time
                        product_name[:25] + "..." if len(product_name) > 25 else product_name,  # Product name
                        customer_name[:15] + "..." if len(customer_name) > 15 else customer_name,  # Customer
                        quantity,           # Quantity
                        formatted_unit_price,  # Unit price - properly formatted
                        formatted_total,    # Total - properly formatted
                        payment_method      # Payment method
                    ))
                except Exception as row_error:
                    print(f"Error processing row {sale}: {row_error}")
                    tree.insert('', 'end', values=(
                        "Error", str(row_error)[:20], "", "", "", "", "", "", ""
                    ))
                    
        except sqlite3.Error as e:
            print(f"Database error in refresh_sales_table: {e}")
            tree.insert('', 'end', values=(
                "DB Error", str(e)[:30], "", "", "", "", "", "", ""
            ))
        except Exception as e:
            print(f"General error in refresh_sales_table: {e}")
            tree.insert('', 'end', values=(
                "Error", str(e)[:30], "", "", "", "", "", "", ""
            ))

    def debug_sales_data(self):
        """Debug method to check the actual values in the database"""
        try:
            self.main_app.cursor.execute('''
                SELECT id, total, unit_price, quantity, typeof(total), typeof(unit_price)
                FROM sales 
                ORDER BY id DESC 
                LIMIT 5
            ''')
            results = self.main_app.cursor.fetchall()
            
            print("=== DEBUG: Recent Sales Data ===")
            for row in results:
                print(f"ID: {row[0]}, Total: {row[1]} (type: {row[4]}), Unit Price: {row[2]} (type: {row[5]}), Quantity: {row[3]}")
            print("================================")
            
        except Exception as e:
            print(f"Debug error: {e}")
    
    def update_sales_stats(self, parent, tree):
        """Update sales statistics display"""
        try:
            # Get summary statistics based on current filter
            limit = self.sales_limit_var.get()
            
            # Total sales and revenue for current view
            if limit == "All":
                query = '''
                    SELECT 
                        COUNT(*) as total_sales,
                        COALESCE(SUM(total), 0) as total_revenue,
                        COALESCE(SUM(quantity), 0) as total_items
                    FROM sales
                    ORDER BY sale_date DESC
                '''
                self.main_app.cursor.execute(query)
            else:
                query = '''
                    SELECT 
                        COUNT(*) as total_sales,
                        COALESCE(SUM(total), 0) as total_revenue,
                        COALESCE(SUM(quantity), 0) as total_items
                    FROM (
                        SELECT total, quantity
                        FROM sales
                        ORDER BY sale_date DESC
                        LIMIT ?
                    ) limited_sales
                '''
                self.main_app.cursor.execute(query, (int(limit),))
            
            stats = self.main_app.cursor.fetchone()
            total_sales = stats[0] if stats and stats[0] is not None else 0
            total_revenue = stats[1] if stats and stats[1] is not None else 0.0
            total_items = stats[2] if stats and stats[2] is not None else 0
            
            # Clear previous stats
            for widget in parent.winfo_children():
                widget.destroy()
            
            # Create stats display
            stats_content = ttk.Frame(parent, style='Card.TFrame')
            stats_content.pack(fill='x', padx=20, pady=15)
            
            ttk.Label(stats_content, text="Summary Statistics", 
                     style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
            
            # Stats row
            stats_row = ttk.Frame(stats_content, style='Card.TFrame')
            stats_row.pack(fill='x')
            
            # Total Sales
            sales_frame = ttk.Frame(stats_row, style='Card.TFrame')
            sales_frame.pack(side='left', padx=(0, 30))
            ttk.Label(sales_frame, text="Total Sales:", style='InsightTitle.TLabel').pack(anchor='w')
            ttk.Label(sales_frame, text=str(total_sales), style='InsightValue.TLabel').pack(anchor='w')
            
            # Total Revenue
            revenue_frame = ttk.Frame(stats_row, style='Card.TFrame')
            revenue_frame.pack(side='left', padx=(0, 30))
            ttk.Label(revenue_frame, text="Total Revenue:", style='InsightTitle.TLabel').pack(anchor='w')
            ttk.Label(revenue_frame, text=f"₱{total_revenue:,.2f}", style='InsightValue.TLabel').pack(anchor='w')
            
            # Total Items
            items_frame = ttk.Frame(stats_row, style='Card.TFrame')
            items_frame.pack(side='left')
            ttk.Label(items_frame, text="Items Sold:", style='InsightTitle.TLabel').pack(anchor='w')
            ttk.Label(items_frame, text=str(total_items), style='InsightValue.TLabel').pack(anchor='w')
            
        except sqlite3.Error as e:
            print(f"Database error in update_sales_stats: {e}")
            # Show error in stats area
            error_label = ttk.Label(parent, text=f"Stats Error: {str(e)[:50]}", 
                                   style='SectionTitle.TLabel')
            error_label.pack(padx=20, pady=15)
        except Exception as e:
            print(f"Error updating sales stats: {e}")
            error_label = ttk.Label(parent, text=f"Stats Error: {str(e)[:50]}", 
                                   style='SectionTitle.TLabel')
            error_label.pack(padx=20, pady=15)
    
    def export_sales_data(self, tree):
        """Export sales data to CSV file"""
        try:
            from tkinter import filedialog
            import csv
            
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Sales Data As"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    headers = ['Sale ID', 'Date', 'Time', 'Product Name', 'Customer', 
                              'Quantity', 'Unit Price', 'Total', 'Payment Method']
                    writer.writerow(headers)
                    
                    # Write data
                    for item in tree.get_children():
                        values = tree.item(item)['values']
                        writer.writerow(values)
                
                messagebox.showinfo("Success", f"Sales data exported successfully to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def show_all_stock_alerts(self):
        """Show all low stock products in a new window"""
        # Create new window
        alert_window = tk.Toplevel(self.frame)
        alert_window.title("Stock Alerts")
        alert_window.geometry("900x600")
        alert_window.transient(self.frame)
        
        # Center the window
        alert_window.update_idletasks()
        x = (alert_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (alert_window.winfo_screenheight() // 2) - (600 // 2)
        alert_window.geometry(f"900x600+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(alert_window, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(main_frame, text="All Stock Alerts", style='PageTitle.TLabel').pack(pady=(0, 20))
        
        # Table frame with padding
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create treeview
        columns = ('Product ID', 'Product Name', 'Category', 'Current Stock', 'Min Stock', 'Status')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        # Configure columns with proper widths and anchors
        tree.heading('Product ID', text='Product ID', anchor='center')
        tree.heading('Product Name', text='Product Name', anchor='center')
        tree.heading('Category', text='Category', anchor='center')
        tree.heading('Current Stock', text='Current Stock', anchor='center')
        tree.heading('Min Stock', text='Min Stock', anchor='center')
        tree.heading('Status', text='Status', anchor='center')
        
        tree.column('Product ID', width=100, minwidth=80, anchor='center')
        tree.column('Product Name', width=250, minwidth=200, anchor='center')
        tree.column('Category', width=150, minwidth=120, anchor='center')
        tree.column('Current Stock', width=120, minwidth=100, anchor='center')
        tree.column('Min Stock', width=100, minwidth=80, anchor='center')
        tree.column('Status', width=130, minwidth=100, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Get all low stock products
        low_stock_products = self.main_app.get_low_stock_products()
        
        # Insert data with proper formatting
        for product in low_stock_products:
            status = "OUT OF STOCK" if product[3] == 0 else "LOW STOCK"
            status_color = 'red' if product[3] == 0 else 'orange'
            
            tree.insert('', 'end', values=(
                product[4] if len(product) > 4 else product[0],  # Product ID
                product[1],  # Product Name
                product[2] if len(product) > 2 else "160.0",  # Category
                product[3],  # Current Stock
                5,  # Min Stock
                status
            ), tags=(status_color,))
        
        # Configure tag colors
        tree.tag_configure('red', foreground='#ef4444')
        tree.tag_configure('orange', foreground='#f97316')
        
        # Add close button
        button_frame = ttk.Frame(main_frame, style='Content.TFrame')
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Close", command=alert_window.destroy,
                style='Secondary.TButton').pack()

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
            columns = ('Product ID', 'Product', 'Quantity')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=6)
            
            # Configure columns
            tree.heading('Product ID', text='Product ID', anchor='center')
            tree.heading('Product', text='Product', anchor='center')
            tree.heading('Quantity', text='Quantity', anchor='center')
            
            tree.column('Product ID', width=80, anchor='center')
            tree.column('Product', width=150, anchor='center')
            tree.column('Quantity', width=80, anchor='center')
            
            for product in low_stock_products:
                tree.insert('', 'end', values=(
                    product[4] if len(product) > 4 else product[0], 
                    product[1][:20] + "..." if len(product[1]) > 20 else product[1],
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