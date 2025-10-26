import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import DateEntry  # You may need to pip install tkcalendar

class SalesModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.current_view = 'monthly'  # Default view
        self.custom_start_date = None
        self.custom_end_date = None

    def create_interface(self):
        """Create the sales analysis interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        title_label = ttk.Label(header_frame, text="Product Sales Analysis", style='PageTitle.TLabel')
        title_label.pack(side='left')
        
        # Controls frame
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Time period selector
        period_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        period_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(period_frame, text="View:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=15)
        
        self.period_var = tk.StringVar(value='monthly')
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var,
                                  values=['Daily', 'Weekly', 'Monthly', 'Yearly', 'Custom Range'],
                                  state='readonly', style='Modern.TCombobox', width=15)
        period_combo.pack(side='left', padx=(0, 15), pady=15)
        period_combo.bind('<<ComboboxSelected>>', self.on_period_change)
        
        # Year selector for monthly/yearly views
        self.year_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        self.year_frame.pack(side='left', fill='x', padx=(20, 0))
        
        ttk.Label(self.year_frame, text="Year:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=15)
        
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(self.year_frame, textvariable=self.year_var,
                                     state='readonly', style='Modern.TCombobox', width=10)
        self.year_combo.pack(side='left', padx=(0, 15), pady=15)
        self.year_combo.bind('<<ComboboxSelected>>', self.on_year_change)
        
        # Custom date range frame
        self.date_range_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        # Initially hidden, will be shown when 'Custom Range' is selected
        
        ttk.Label(self.date_range_frame, text="From:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 5), pady=15)
        
        # Start date picker
        today = datetime.now()
        default_start = today - timedelta(days=30)
        
        self.start_date_picker = DateEntry(
            self.date_range_frame, 
            width=12, 
            background='darkblue', 
            foreground='white', 
            borderwidth=2, 
            date_pattern='yyyy-mm-dd',
            year=default_start.year,
            month=default_start.month,
            day=default_start.day
        )
        self.start_date_picker.pack(side='left', padx=(0, 10), pady=15)
        
        ttk.Label(self.date_range_frame, text="To:", style='FieldLabel.TLabel').pack(side='left', padx=(5, 5), pady=15)
        
        # End date picker
        self.end_date_picker = DateEntry(
            self.date_range_frame, 
            width=12, 
            background='darkblue', 
            foreground='white', 
            borderwidth=2, 
            date_pattern='yyyy-mm-dd',
            year=today.year,
            month=today.month,
            day=today.day
        )
        self.end_date_picker.pack(side='left', padx=(0, 10), pady=15)
        
        # Apply button for date range
        self.apply_btn = ttk.Button(
            self.date_range_frame, 
            text="Apply", 
            command=self.apply_date_range,
            style='Primary.TButton',
            width=10
        )
        self.apply_btn.pack(side='left', padx=(5, 15), pady=15)
        
        # Main content area
        content_frame = ttk.Frame(self.frame, style='Content.TFrame')
        content_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.summary_frame, text="Summary")
        
        # Charts tab
        self.charts_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.charts_frame, text="Charts")
        
        # Detailed tab
        self.detailed_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.detailed_frame, text="Detailed Data")
        
        # Load initial data
        self.update_year_selector()
        self.load_sales_data()
        
        return self.frame
    
    def apply_date_range(self):
        """Apply the selected custom date range"""
        try:
            start_date = self.start_date_picker.get_date()
            end_date = self.end_date_picker.get_date()
            
            # Validate date range
            if start_date > end_date:
                messagebox.showerror("Invalid Date Range", "Start date cannot be later than end date.")
                return
            
            self.custom_start_date = start_date
            self.custom_end_date = end_date
            
            # Load data with custom date range
            self.load_sales_data()
            
        except Exception as e:
            print(f"Error applying custom date range: {e}")
            messagebox.showerror("Error", f"Failed to apply date range: {str(e)}")

    def update_year_selector(self):
        """Update available years in the year selector"""
        try:
            available_years = self.main_app.get_available_years()
            self.year_combo['values'] = available_years
            if available_years:
                self.year_var.set(available_years[0])  # Set to most recent year
        except Exception as e:
            print(f"Error updating year selector: {e}")

    def on_period_change(self, event=None):
        """Handle period selection change"""
        self.current_view = self.period_var.get().lower()
        
        # Show/hide appropriate frames based on the selected view
        if self.current_view == 'custom range':
            # Hide year selector, show date range selector
            self.year_frame.pack_forget()
            self.date_range_frame.pack(side='left', fill='x', padx=(20, 0))
        else:
            # Hide date range selector
            if self.date_range_frame.winfo_ismapped():
                self.date_range_frame.pack_forget()
            
            # Show year selector for monthly and yearly views
            if self.current_view in ['monthly', 'yearly']:
                if not self.year_frame.winfo_ismapped():
                    self.year_frame.pack(side='left', fill='x', padx=(20, 0))
            else:
                # Hide year selector for daily and weekly views
                if self.year_frame.winfo_ismapped():
                    self.year_frame.pack_forget()
        
        self.load_sales_data()

    def on_year_change(self, event=None):
        """Handle year selection change"""
        self.load_sales_data()

    def load_sales_data(self):
        """Load and display sales data based on current view"""
        try:
            # Clear previous data
            self.clear_frames()
            
            # Get data based on current view
            if self.current_view == 'daily':
                data = self.get_daily_sales_data()
                self.display_daily_summary(data)
                self.create_daily_charts(data)
                self.display_detailed_data(data, 'Daily')
                
            elif self.current_view == 'weekly':
                data = self.get_weekly_sales_data()
                self.display_weekly_summary(data)
                self.create_weekly_charts(data)
                self.display_detailed_data(data, 'Weekly')
                
            elif self.current_view == 'monthly':
                year = int(self.year_var.get())
                data = self.get_monthly_sales_data(year)
                self.display_monthly_summary(data, year)
                self.create_monthly_charts(data, year)
                self.display_detailed_data(data, 'Monthly')
                
            elif self.current_view == 'yearly':
                data = self.get_yearly_sales_data()
                self.display_yearly_summary(data)
                self.create_yearly_charts(data)
                self.display_detailed_data(data, 'Yearly')
                
            elif self.current_view == 'custom range':
                data = self.get_custom_range_sales_data()
                self.display_custom_range_summary(data)
                self.create_custom_range_charts(data)
                self.display_detailed_data(data, 'Custom Range')
                
        except Exception as e:
            print(f"Error loading sales data: {e}")
            messagebox.showerror("Error", f"Failed to load sales data: {str(e)}")

    def clear_frames(self):
        """Clear all display frames"""
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        for widget in self.detailed_frame.winfo_children():
            widget.destroy()

    def get_daily_sales_data(self):
        """Get daily sales data for the last 30 days"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    DATE(sale_date) as date,
                    product_name,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-30 days')
                GROUP BY DATE(sale_date), product_name
                ORDER BY date DESC, product_name ASC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting daily sales data: {e}")
            return []

    def get_weekly_sales_data(self):
        """Get weekly sales data for the last 12 weeks"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%Y-W%W', sale_date) as week,
                    MIN(DATE(sale_date, 'weekday 0', '-6 days')) as week_start,
                    MAX(DATE(sale_date, 'weekday 0')) as week_end,
                    product_name,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-84 days')
                GROUP BY week, product_name
                ORDER BY week DESC, product_name ASC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting weekly sales data: {e}")
            return []

    def get_monthly_sales_data(self, year):
        """Get monthly sales data for a specific year"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%m', sale_date) as month,
                    product_name,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE strftime('%Y', sale_date) = ?
                GROUP BY month, product_name
                ORDER BY month ASC, product_name ASC
            ''', (str(year),))
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting monthly sales data: {e}")
            return []

    def get_yearly_sales_data(self):
        """Get yearly sales data"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%Y', sale_date) as year,
                    product_name,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                GROUP BY year, product_name
                ORDER BY year DESC, product_name ASC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting yearly sales data: {e}")
            return []
            
    def get_custom_range_sales_data(self):
        """Get sales data for custom date range"""
        try:
            # Default to last 30 days if no custom range is specified
            if not self.custom_start_date or not self.custom_end_date:
                today = datetime.now().date()
                default_start = today - timedelta(days=30)
                start_date = default_start.strftime('%Y-%m-%d')
                end_date = today.strftime('%Y-%m-%d')
            else:
                start_date = self.custom_start_date.strftime('%Y-%m-%d')
                end_date = self.custom_end_date.strftime('%Y-%m-%d')
            
            # Print date range for debugging
            print(f"Fetching custom range data from {start_date} to {end_date}")
            
            # Get data with daily granularity within the specified date range
            self.main_app.cursor.execute('''
                SELECT 
                    DATE(sale_date) as date,
                    product_name,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE DATE(sale_date) BETWEEN ? AND ?
                GROUP BY DATE(sale_date), product_name
                ORDER BY date ASC, product_name ASC
            ''', (start_date, end_date))
            
            result = self.main_app.cursor.fetchall()
            print(f"Found {len(result)} records for custom date range")
            return result
        except Exception as e:
            print(f"Error getting custom range sales data: {e}")
            # Return empty list instead of raising exception to avoid crashes
            return []

    # Add display methods for custom range
    def display_custom_range_summary(self, data):
        """Display custom range sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No sales data available for the selected date range")
            return
            
        # Create summary frame
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Format the date range for display
        if self.custom_start_date and self.custom_end_date:
            start_date_str = self.custom_start_date.strftime('%b %d, %Y')
            end_date_str = self.custom_end_date.strftime('%b %d, %Y')
            date_range_str = f"{start_date_str} - {end_date_str}"
        else:
            today = datetime.now().date()
            default_start = today - timedelta(days=30)
            start_date_str = default_start.strftime('%b %d, %Y')
            end_date_str = today.strftime('%b %d, %Y')
            date_range_str = f"{start_date_str} - {end_date_str} (Default)"
        
        # Extract and calculate summary metrics
        total_revenue = sum(row[2] for row in data)
        total_items_sold = sum(row[3] for row in data)
        total_transactions = sum(row[4] for row in data)
        
        unique_dates = set(row[0] for row in data)
        num_days = len(unique_dates)
        
        # Calculate averages
        avg_daily_revenue = total_revenue / num_days if num_days > 0 else 0
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Summary title
        ttk.Label(summary_frame, text=f"Sales Summary ({date_range_str})", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create cards grid (2x3)
        card_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        card_frame.pack(fill='x', pady=(0, 20))
        
        # Create metric cards
        metrics = [
            {"title": "Total Revenue", "value": f"₱{total_revenue:,.2f}", "color": "#4caf50", "icon": "📈"},
            {"title": "Total Items Sold", "value": f"{total_items_sold:,}", "color": "#2196f3", "icon": "📦"},
            {"title": "Total Transactions", "value": f"{total_transactions:,}", "color": "#9c27b0", "icon": "🛒"},
            {"title": "Avg. Daily Revenue", "value": f"₱{avg_daily_revenue:,.2f}", "color": "#f44336", "icon": "💰"},
            {"title": "Avg. Transaction Value", "value": f"₱{avg_transaction_value:,.2f}", "color": "#ff9800", "icon": "💳"},
            {"title": "Days in Range", "value": f"{num_days:,}", "color": "#607d8b", "icon": "📆"}
        ]
        
        # Create product-specific summary
        product_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        product_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(product_frame, text=f"Top Products ({date_range_str})", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Group by product
        product_data = {}
        for row in data:
            product_name = row[1]
            if product_name not in product_data:
                product_data[product_name] = [0, 0]  # [revenue, items_sold]
            product_data[product_name][0] += row[2]  # revenue
            product_data[product_name][1] += row[3]  # items_sold
        
        # Sort by revenue
        sorted_products = sorted(product_data.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create product table
        columns = ('Product', 'Revenue', 'Items Sold', 'Avg. Price')
        tree = ttk.Treeview(product_frame, columns=columns, show='headings', style='Modern.Treeview', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')  # Center-align all columns
        
        tree.column('Product', width=200)
        tree.column('Revenue', width=100)
        tree.column('Items Sold', width=100)
        tree.column('Avg. Price', width=100)
        
        for product_name, (revenue, items_sold) in sorted_products[:10]:  # Top 10 products
            avg_price = revenue / items_sold if items_sold > 0 else 0
            tree.insert('', 'end', values=(
                product_name,
                f"₱{revenue:,.2f}",
                f"{items_sold:,}",
                f"₱{avg_price:,.2f}"
            ))
            
        scrollbar = ttk.Scrollbar(product_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Metrics display
        row = 0
        col = 0
        for i, metric in enumerate(metrics):
            card = ttk.Frame(card_frame, style='Card.TFrame', padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=f"{metric['icon']} {metric['title']}", style='CardTitle.TLabel').pack(anchor='w')
            ttk.Label(card, text=metric['value'], style='CardValue.TLabel', foreground=metric['color']).pack(anchor='w')
            
            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1
                
        # Configure grid
        for i in range(3):
            card_frame.columnconfigure(i, weight=1, uniform='card')
        for i in range(2):
            card_frame.rowconfigure(i, weight=1, uniform='card')

    def create_custom_range_charts(self, data):
        """Create charts for custom date range data"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No sales data available for charting")
            return
            
        # Get date range for chart title
        if self.custom_start_date and self.custom_end_date:
            start_date_str = self.custom_start_date.strftime('%b %d, %Y')
            end_date_str = self.custom_end_date.strftime('%b %d, %Y')
            date_range_str = f"{start_date_str} - {end_date_str}"
        else:
            today = datetime.now().date()
            default_start = today - timedelta(days=30)
            start_date_str = default_start.strftime('%b %d, %Y')
            end_date_str = today.strftime('%b %d, %Y')
            date_range_str = f"{start_date_str} - {end_date_str} (Default)"
            
        # Group by date
        dates_data = {}
        products_data = {}
        
        for row in data:
            date = row[0]
            product_name = row[1]
            revenue = row[2]
            items_sold = row[3]
            
            # For date-based chart
            if date not in dates_data:
                dates_data[date] = [0, 0]  # [revenue, items_sold]
            dates_data[date][0] += revenue
            dates_data[date][1] += items_sold
            
            # For product-based chart
            if product_name not in products_data:
                products_data[product_name] = [0, 0]  # [revenue, items_sold]
            products_data[product_name][0] += revenue
            products_data[product_name][1] += items_sold
        
        # Sort dates and decide how many to display
        sorted_dates = sorted(dates_data.keys())
        num_dates = len(sorted_dates)
        
        # If there are too many dates, sample to show a reasonable number
        if num_dates > 20:
            step = max(1, num_dates // 20)  # Show at most 20 dates
            dates_to_plot = sorted_dates[::step]
            if sorted_dates[-1] not in dates_to_plot:
                dates_to_plot.append(sorted_dates[-1])  # Make sure to include the last date
        else:
            dates_to_plot = sorted_dates
        
        # Extract data for plotting
        dates = []
        revenues = []
        items_sold = []
        
        for date in dates_to_plot:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%b %d')
            dates.append(formatted_date)
            revenues.append(dates_data[date][0])
            items_sold.append(dates_data[date][1])
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Revenue chart
        ax1.bar(dates, revenues, color='#2196f3', alpha=0.7)
        ax1.set_title(f'Daily Revenue ({date_range_str})', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Items sold chart
        ax2.bar(dates, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title(f'Daily Items Sold ({date_range_str})', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Date')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        # Create product breakdown chart
        fig2, ax = plt.subplots(figsize=(10, 5))
        
        # Sort products by revenue and get top 5
        sorted_products = sorted(products_data.items(), key=lambda x: x[1][0], reverse=True)[:5]
        product_names = [p[0] for p in sorted_products]
        product_revenues = [p[1][0] for p in sorted_products]
        
        # Product revenue chart
        bars = ax.bar(product_names, product_revenues, color='#ff9800', alpha=0.7)
        ax.set_title(f'Top 5 Products by Revenue ({date_range_str})', fontweight='bold')
        ax.set_ylabel('Revenue (₱)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add revenue labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₱{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas2 = FigureCanvasTkAgg(fig2, self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(10, 20))

    def display_daily_summary(self, data):
        """Display daily sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No daily sales data available for the last 30 days")
            return
            
        # Create summary cards
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Extract and calculate summary metrics
        total_revenue = sum(row[2] for row in data)
        total_items_sold = sum(row[3] for row in data)
        total_transactions = sum(row[4] for row in data)
        
        unique_days = set(row[0] for row in data)
        num_days = len(unique_days)
        
        # Calculate averages
        avg_daily_revenue = total_revenue / num_days if num_days > 0 else 0
        avg_daily_items = total_items_sold / num_days if num_days > 0 else 0
        avg_daily_transactions = total_transactions / num_days if num_days > 0 else 0
        
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Create cards grid (2x3)
        card_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        card_frame.pack(fill='x', pady=(0, 20))
        
        # Summary title
        ttk.Label(summary_frame, text="Daily Sales Summary (Last 30 Days)", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create metric cards
        metrics = [
            {"title": "Total Revenue", "value": f"₱{total_revenue:,.2f}", "color": "#4caf50", "icon": "📈"},
            {"title": "Total Items Sold", "value": f"{total_items_sold:,}", "color": "#2196f3", "icon": "📦"},
            {"title": "Total Transactions", "value": f"{total_transactions:,}", "color": "#9c27b0", "icon": "🛒"},
            {"title": "Avg. Daily Revenue", "value": f"₱{avg_daily_revenue:,.2f}", "color": "#f44336", "icon": "💰"},
            {"title": "Avg. Transaction Value", "value": f"₱{avg_transaction_value:,.2f}", "color": "#ff9800", "icon": "💳"},
            {"title": "Days with Sales", "value": f"{num_days:,}", "color": "#607d8b", "icon": "📆"}
        ]
        
        # Create product-specific summary
        product_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        product_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(product_frame, text="Top Products (Last 30 Days)", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Group by product
        product_data = {}
        for row in data:
            product_name = row[1]
            if product_name not in product_data:
                product_data[product_name] = [0, 0]  # [revenue, items_sold]
            product_data[product_name][0] += row[2]  # revenue
            product_data[product_name][1] += row[3]  # items_sold
        
        # Sort by revenue
        sorted_products = sorted(product_data.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create product table
        columns = ('Product', 'Revenue', 'Items Sold', 'Avg. Price')
        tree = ttk.Treeview(product_frame, columns=columns, show='headings', style='Modern.Treeview', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column('Product', width=200, anchor='center')
        tree.column('Revenue', width=100, anchor='center')
        tree.column('Items Sold', width=100, anchor='center')
        tree.column('Avg. Price', width=100, anchor='center')
        
        for product_name, (revenue, items_sold) in sorted_products[:10]:  # Top 10 products
            avg_price = revenue / items_sold if items_sold > 0 else 0
            tree.insert('', 'end', values=(
                product_name,
                f"₱{revenue:,.2f}",
                f"{items_sold:,}",
                f"₱{avg_price:,.2f}"
            ))
            
        scrollbar = ttk.Scrollbar(product_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Metrics display
        row = 0
        col = 0
        for i, metric in enumerate(metrics):
            card = ttk.Frame(card_frame, style='Card.TFrame', padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=f"{metric['icon']} {metric['title']}", style='CardTitle.TLabel').pack(anchor='w')
            ttk.Label(card, text=metric['value'], style='CardValue.TLabel', foreground=metric['color']).pack(anchor='w')
            
            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1
                
        # Configure grid
        for i in range(3):
            card_frame.columnconfigure(i, weight=1, uniform='card')
        for i in range(2):
            card_frame.rowconfigure(i, weight=1, uniform='card')

    def display_weekly_summary(self, data):
        """Display weekly sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No weekly sales data available for the last 12 weeks")
            return
            
        # Create summary frame
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Extract and calculate summary metrics
        total_revenue = sum(row[4] for row in data)
        total_items_sold = sum(row[5] for row in data)
        total_transactions = sum(row[6] for row in data)
        
        unique_weeks = set(row[0] for row in data)
        num_weeks = len(unique_weeks)
        
        # Calculate averages
        avg_weekly_revenue = total_revenue / num_weeks if num_weeks > 0 else 0
        avg_weekly_items = total_items_sold / num_weeks if num_weeks > 0 else 0
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Summary title
        ttk.Label(summary_frame, text="Weekly Sales Summary (Last 12 Weeks)", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create cards grid (2x3)
        card_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        card_frame.pack(fill='x', pady=(0, 20))
        
        # Create metric cards
        metrics = [
            {"title": "Total Revenue", "value": f"₱{total_revenue:,.2f}", "color": "#4caf50", "icon": "📈"},
            {"title": "Total Items Sold", "value": f"{total_items_sold:,}", "color": "#2196f3", "icon": "📦"},
            {"title": "Total Transactions", "value": f"{total_transactions:,}", "color": "#9c27b0", "icon": "🛒"},
            {"title": "Avg. Weekly Revenue", "value": f"₱{avg_weekly_revenue:,.2f}", "color": "#f44336", "icon": "💰"},
            {"title": "Avg. Transaction Value", "value": f"₱{avg_transaction_value:,.2f}", "color": "#ff9800", "icon": "💳"},
            {"title": "Weeks with Sales", "value": f"{num_weeks:,}", "color": "#607d8b", "icon": "📆"}
        ]
        
        # Create product-specific summary
        product_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        product_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(product_frame, text="Top Products (Last 12 Weeks)", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Group by product
        product_data = {}
        for row in data:
            product_name = row[3]
            if product_name not in product_data:
                product_data[product_name] = [0, 0]  # [revenue, items_sold]
            product_data[product_name][0] += row[4]  # revenue
            product_data[product_name][1] += row[5]  # items_sold
        
        # Sort by revenue
        sorted_products = sorted(product_data.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create product table
        columns = ('Product', 'Revenue', 'Items Sold', 'Avg. Price')
        tree = ttk.Treeview(product_frame, columns=columns, show='headings', style='Modern.Treeview', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column('Product', width=200, anchor='center')
        tree.column('Revenue', width=100, anchor='center')
        tree.column('Items Sold', width=100, anchor='center')
        tree.column('Avg. Price', width=100, anchor='center')
        
        for product_name, (revenue, items_sold) in sorted_products[:10]:  # Top 10 products
            avg_price = revenue / items_sold if items_sold > 0 else 0
            tree.insert('', 'end', values=(
                product_name,
                f"₱{revenue:,.2f}",
                f"{items_sold:,}",
                f"₱{avg_price:,.2f}"
            ))
            
        scrollbar = ttk.Scrollbar(product_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Metrics display
        row = 0
        col = 0
        for i, metric in enumerate(metrics):
            card = ttk.Frame(card_frame, style='Card.TFrame', padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=f"{metric['icon']} {metric['title']}", style='CardTitle.TLabel').pack(anchor='w')
            ttk.Label(card, text=metric['value'], style='CardValue.TLabel', foreground=metric['color']).pack(anchor='w')
            
            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1
                
        # Configure grid
        for i in range(3):
            card_frame.columnconfigure(i, weight=1, uniform='card')
        for i in range(2):
            card_frame.rowconfigure(i, weight=1, uniform='card')

    def display_monthly_summary(self, data, year):
        """Display monthly sales summary for a specific year"""
        if not data:
            self.show_no_data_message(self.summary_frame, f"No monthly sales data available for {year}")
            return
            
        # Create summary frame
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Extract and calculate summary metrics
        total_revenue = sum(row[2] for row in data)
        total_items_sold = sum(row[3] for row in data)
        total_transactions = sum(row[4] for row in data)
        
        unique_months = set(row[0] for row in data)
        num_months = len(unique_months)
        
        # Calculate averages
        avg_monthly_revenue = total_revenue / num_months if num_months > 0 else 0
        avg_monthly_items = total_items_sold / num_months if num_months > 0 else 0
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Summary title
        ttk.Label(summary_frame, text=f"Monthly Sales Summary ({year})", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create cards grid (2x3)
        card_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        card_frame.pack(fill='x', pady=(0, 20))
        
        # Create metric cards
        metrics = [
            {"title": "Total Revenue", "value": f"₱{total_revenue:,.2f}", "color": "#4caf50", "icon": "📈"},
            {"title": "Total Items Sold", "value": f"{total_items_sold:,}", "color": "#2196f3", "icon": "📦"},
            {"title": "Total Transactions", "value": f"{total_transactions:,}", "color": "#9c27b0", "icon": "🛒"},
            {"title": "Avg. Monthly Revenue", "value": f"₱{avg_monthly_revenue:,.2f}", "color": "#f44336", "icon": "💰"},
            {"title": "Avg. Transaction Value", "value": f"₱{avg_transaction_value:,.2f}", "color": "#ff9800", "icon": "💳"},
            {"title": "Months with Sales", "value": f"{num_months:,}", "color": "#607d8b", "icon": "📆"}
        ]
        
        # Create product-specific summary
        product_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        product_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(product_frame, text=f"Top Products ({year})", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Group by product
        product_data = {}
        for row in data:
            product_name = row[1]
            if product_name not in product_data:
                product_data[product_name] = [0, 0]  # [revenue, items_sold]
            product_data[product_name][0] += row[2]  # revenue
            product_data[product_name][1] += row[3]  # items_sold
        
        # Sort by revenue
        sorted_products = sorted(product_data.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create product table
        columns = ('Product', 'Revenue', 'Items Sold', 'Avg. Price')
        tree = ttk.Treeview(product_frame, columns=columns, show='headings', style='Modern.Treeview', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column('Product', width=200, anchor='center')
        tree.column('Revenue', width=100, anchor='center')
        tree.column('Items Sold', width=100, anchor='center')
        tree.column('Avg. Price', width=100, anchor='center')
        
        for product_name, (revenue, items_sold) in sorted_products[:10]:  # Top 10 products
            avg_price = revenue / items_sold if items_sold > 0 else 0
            tree.insert('', 'end', values=(
                product_name,
                f"₱{revenue:,.2f}",
                f"{items_sold:,}",
                f"₱{avg_price:,.2f}"
            ))
            
        scrollbar = ttk.Scrollbar(product_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Metrics display
        row = 0
        col = 0
        for i, metric in enumerate(metrics):
            card = ttk.Frame(card_frame, style='Card.TFrame', padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=f"{metric['icon']} {metric['title']}", style='CardTitle.TLabel').pack(anchor='w')
            ttk.Label(card, text=metric['value'], style='CardValue.TLabel', foreground=metric['color']).pack(anchor='w')
            
            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1
                
        # Configure grid
        for i in range(3):
            card_frame.columnconfigure(i, weight=1, uniform='card')
        for i in range(2):
            card_frame.rowconfigure(i, weight=1, uniform='card')
            
    def display_yearly_summary(self, data):
        """Display yearly sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No yearly sales data available")
            return
            
        # Create summary frame
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Extract and calculate summary metrics
        total_revenue = sum(row[2] for row in data)
        total_items_sold = sum(row[3] for row in data)
        total_transactions = sum(row[4] for row in data)
        
        unique_years = set(row[0] for row in data)
        num_years = len(unique_years)
        
        # Calculate averages
        avg_yearly_revenue = total_revenue / num_years if num_years > 0 else 0
        avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Summary title
        ttk.Label(summary_frame, text="Yearly Sales Summary", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create cards grid (2x3)
        card_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        card_frame.pack(fill='x', pady=(0, 20))
        
        # Create metric cards
        metrics = [
            {"title": "Total Revenue", "value": f"₱{total_revenue:,.2f}", "color": "#4caf50", "icon": "📈"},
            {"title": "Total Items Sold", "value": f"{total_items_sold:,}", "color": "#2196f3", "icon": "📦"},
            {"title": "Total Transactions", "value": f"{total_transactions:,}", "color": "#9c27b0", "icon": "🛒"},
            {"title": "Avg. Yearly Revenue", "value": f"₱{avg_yearly_revenue:,.2f}", "color": "#f44336", "icon": "💰"},
            {"title": "Avg. Transaction Value", "value": f"₱{avg_transaction_value:,.2f}", "color": "#ff9800", "icon": "💳"},
            {"title": "Years with Sales", "value": f"{num_years:,}", "color": "#607d8b", "icon": "📆"}
        ]
        
        # Create product-specific summary
        product_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        product_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(product_frame, text="Top Products (All Time)", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Group by product
        product_data = {}
        for row in data:
            product_name = row[1]
            if product_name not in product_data:
                product_data[product_name] = [0, 0]  # [revenue, items_sold]
            product_data[product_name][0] += row[2]  # revenue
            product_data[product_name][1] += row[3]  # items_sold
        
        # Sort by revenue
        sorted_products = sorted(product_data.items(), key=lambda x: x[1][0], reverse=True)
        
        # Create product table
        columns = ('Product', 'Revenue', 'Items Sold', 'Avg. Price')
        tree = ttk.Treeview(product_frame, columns=columns, show='headings', style='Modern.Treeview', height=5)
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column('Product', width=200, anchor='center')
        tree.column('Revenue', width=100, anchor='center')
        tree.column('Items Sold', width=100, anchor='center')
        tree.column('Avg. Price', width=100, anchor='center')
        
        for product_name, (revenue, items_sold) in sorted_products[:10]:  # Top 10 products
            avg_price = revenue / items_sold if items_sold > 0 else 0
            tree.insert('', 'end', values=(
                product_name,
                f"₱{revenue:,.2f}",
                f"{items_sold:,}",
                f"₱{avg_price:,.2f}"
            ))
            
        scrollbar = ttk.Scrollbar(product_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Metrics display
        row = 0
        col = 0
        for i, metric in enumerate(metrics):
            card = ttk.Frame(card_frame, style='Card.TFrame', padding=15)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(card, text=f"{metric['icon']} {metric['title']}", style='CardTitle.TLabel').pack(anchor='w')
            ttk.Label(card, text=metric['value'], style='CardValue.TLabel', foreground=metric['color']).pack(anchor='w')
            
            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1
                
        # Configure grid
        for i in range(3):
            card_frame.columnconfigure(i, weight=1, uniform='card')
        for i in range(2):
            card_frame.rowconfigure(i, weight=1, uniform='card')

    def create_daily_charts(self, data):
        """Create daily sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No daily sales data available for charting")
            return
            
        # Group by date
        dates_data = {}
        products_data = {}
        
        for row in data:
            date = row[0]
            product_name = row[1]
            revenue = row[2]
            items_sold = row[3]
            
            # For date-based chart
            if date not in dates_data:
                dates_data[date] = [0, 0]  # [revenue, items_sold]
            dates_data[date][0] += revenue
            dates_data[date][1] += items_sold
            
            # For product-based chart
            if product_name not in products_data:
                products_data[product_name] = [0, 0]  # [revenue, items_sold]
            products_data[product_name][0] += revenue
            products_data[product_name][1] += items_sold
        
        # Sort dates and get the last 14 days
        sorted_dates = sorted(dates_data.keys())[-14:]
        dates_to_plot = sorted_dates
        
        # Extract data for plotting
        dates = []
        revenues = []
        items_sold = []
        
        for date in dates_to_plot:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%b %d')
            dates.append(formatted_date)
            revenues.append(dates_data[date][0])
            items_sold.append(dates_data[date][1])
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Revenue chart
        ax1.bar(dates, revenues, color='#2196f3', alpha=0.7)
        ax1.set_title('Daily Revenue (Last 14 Days)', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        plt.setp(ax1.get_xticklabels(), rotation=0, ha='right')
        
        # Items sold chart
        ax2.bar(dates, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Daily Items Sold (Last 14 Days)', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Date')
        plt.setp(ax2.get_xticklabels(), rotation=0, ha='right')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        # Create product breakdown chart
        fig2, ax = plt.subplots(figsize=(10, 5))
        
        # Sort products by revenue and get top 5
        sorted_products = sorted(products_data.items(), key=lambda x: x[1][0], reverse=True)[:5]
        product_names = [p[0] for p in sorted_products]
        product_revenues = [p[1][0] for p in sorted_products]
        
        # Product revenue chart
        bars = ax.bar(product_names, product_revenues, color='#ff9800', alpha=0.7)
        ax.set_title('Top 5 Products by Revenue (Last 30 Days)', fontweight='bold')
        ax.set_ylabel('Revenue (₱)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add revenue labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₱{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas2 = FigureCanvasTkAgg(fig2, self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(10, 20))

    def create_weekly_charts(self, data):
        """Create weekly sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No weekly sales data available for charting")
            return
            
        # Group by week
        weeks_data = {}
        products_data = {}
        
        for row in data:
            week = row[0]
            product_name = row[3]
            revenue = row[4]
            items_sold = row[5]
            
            # For week-based chart
            if week not in weeks_data:
                weeks_data[week] = [row[1], row[2], 0, 0]  # [start_date, end_date, revenue, items_sold]
            weeks_data[week][2] += revenue
            weeks_data[week][3] += items_sold
            
            # For product-based chart
            if product_name not in products_data:
                products_data[product_name] = [0, 0]  # [revenue, items_sold]
            products_data[product_name][0] += revenue
            products_data[product_name][1] += items_sold
        
        # Sort weeks and get the last 8 weeks
        sorted_weeks = sorted(weeks_data.keys())[-8:]
        
        # Extract data for plotting
        week_labels = []
        revenues = []
        items_sold = []
        
        for week in sorted_weeks:
            start_date = datetime.strptime(weeks_data[week][0], '%Y-%m-%d').strftime('%b %d')
            week_num = week.split('-W')[1]
            week_labels.append(f"W{week_num}\n{start_date}")
            revenues.append(weeks_data[week][2])
            items_sold.append(weeks_data[week][3])
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Revenue chart
        ax1.bar(week_labels, revenues, color='#2196f3', alpha=0.7)
        ax1.set_title('Weekly Revenue (Last 8 Weeks)', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        
        # Items sold chart
        ax2.bar(week_labels, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Weekly Items Sold (Last 8 Weeks)', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Week')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        # Create product breakdown chart
        fig2, ax = plt.subplots(figsize=(10, 5))
        
        # Sort products by revenue and get top 5
        sorted_products = sorted(products_data.items(), key=lambda x: x[1][0], reverse=True)[:5]
        product_names = [p[0] for p in sorted_products]
        product_revenues = [p[1][0] for p in sorted_products]
        
        # Product revenue chart
        bars = ax.bar(product_names, product_revenues, color='#ff9800', alpha=0.7)
        ax.set_title('Top 5 Products by Revenue (Last 12 Weeks)', fontweight='bold')
        ax.set_ylabel('Revenue (₱)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add revenue labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₱{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas2 = FigureCanvasTkAgg(fig2, self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(10, 20))

    def create_monthly_charts(self, data, year):
        """Create monthly sales charts for a specific year"""
        if not data:
            self.show_no_data_message(self.charts_frame, f"No monthly sales data available for {year}")
            return
            
        # Group by month
        months_data = {}
        products_data = {}
        
        for row in data:
            month_num = row[0]
            product_name = row[1]
            revenue = row[2]
            items_sold = row[3]
            
            # For month-based chart
            if month_num not in months_data:
                months_data[month_num] = [0, 0]  # [revenue, items_sold]
            months_data[month_num][0] += revenue
            months_data[month_num][1] += items_sold
            
            # For product-based chart
            if product_name not in products_data:
                products_data[product_name] = [0, 0]  # [revenue, items_sold]
            products_data[product_name][0] += revenue
            products_data[product_name][1] += items_sold
        
        # Prepare month names
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        # Fill in missing months
        all_months = {}
        for i in range(1, 13):
            month_str = f"{i:02d}"
            if month_str in months_data:
                all_months[month_str] = months_data[month_str]
            else:
                all_months[month_str] = [0, 0]  # [revenue, items_sold]
        
        # Extract data for plotting
        month_labels = []
        revenues = []
        items_sold = []
        
        for month_num in sorted(all_months.keys()):
            month_idx = int(month_num) - 1
            month_labels.append(month_names[month_idx][:3])  # Abbreviated month names
            revenues.append(all_months[month_num][0])
            items_sold.append(all_months[month_num][1])
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Revenue chart
        ax1.bar(month_labels, revenues, color='#2196f3', alpha=0.7)
        ax1.set_title(f'Monthly Revenue ({year})', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        
        # Items sold chart
        ax2.bar(month_labels, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title(f'Monthly Items Sold ({year})', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Month')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(20, 10))
        
        # Create product breakdown chart
        fig2, ax = plt.subplots(figsize=(10, 5))
        
        # Sort products by revenue and get top 5
        sorted_products = sorted(products_data.items(), key=lambda x: x[1][0], reverse=True)[:5]
        product_names = [p[0] for p in sorted_products]
        product_revenues = [p[1][0] for p in sorted_products]
        
        # Product revenue chart
        bars = ax.bar(product_names, product_revenues, color='#ff9800', alpha=0.7)
        ax.set_title(f'Top 5 Products by Revenue ({year})', fontweight='bold')
        ax.set_ylabel('Revenue (₱)')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add revenue labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₱{height:,.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas2 = FigureCanvasTkAgg(fig2, self.charts_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=(10, 20))

    def create_yearly_charts(self, data):
        """Create yearly sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No yearly sales data available for charting")
            return
            
        # Group by year
        years_data = {}
        products_data = {}
        
        for row in data:
            year = row[0]
            product_name = row[1]
            revenue = row[2]
            items_sold = row[3]
            
            # For year-based chart
            if year not in years_data:
                years_data[year] = [0, 0]  # [revenue, items_sold]
            years_data[year][0] += revenue
            years_data[year][1] += items_sold
            
            # For product-based chart
            if product_name not in products_data:
                products_data[product_name] = [0, 0]  # [revenue, items_sold]
            products_data[product_name][0] += revenue
            products_data[product_name][1] += items_sold
        
        # Extract data for plotting
        years = sorted(years_data.keys())
        revenues = [years_data[y][0] for y in years]
        items_sold = [years_data[y][1] for y in years]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Revenue chart
        ax1.bar(years, revenues, color='#2196f3', alpha=0.7)
        ax1.set_title('Yearly Revenue', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Revenue (₱)')
        
        # Items sold chart
        ax2.bar(years, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Yearly Items Sold', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Year')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

    def display_detailed_data(self, data, period_type):
        """Display detailed data in table format"""
        if not data:
            self.show_no_data_message(self.detailed_frame, f"No {period_type.lower()} sales data available")
            return
            
        table_frame = ttk.Frame(self.detailed_frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Get date range string for custom range
        if period_type == 'Custom Range':
            if self.custom_start_date and self.custom_end_date:
                start_date_str = self.custom_start_date.strftime('%b %d, %Y')
                end_date_str = self.custom_end_date.strftime('%b %d, %Y')
                period_label = f"Custom Range Sales Data ({start_date_str} - {end_date_str})"
            else:
                today = datetime.now().date()
                default_start = today - timedelta(days=30)
                start_date_str = default_start.strftime('%b %d, %Y')
                end_date_str = today.strftime('%b %d, %Y')
                period_label = f"Custom Range Sales Data ({start_date_str} - {end_date_str}, Default)"
        else:
            period_label = f"{period_type} Sales Detailed Data"
            
        ttk.Label(table_frame, text=period_label, style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Initialize tree variable with a default value
        tree = None
        
        # Create treeview based on period type
        if period_type in ['Daily', 'Custom Range']:
            columns = ('Date', 'Product', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Transaction Value')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center')  # Center align all columns
            
            tree.column('Date', width=100)
            tree.column('Product', width=200)
            tree.column('Revenue', width=100)
            tree.column('Items Sold', width=100)
            tree.column('Transactions', width=100)
            tree.column('Avg. Transaction Value', width=150)
            
            for row in data:
                date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%b %d, %Y')
                avg_txn = row[2] / row[4] if row[4] > 0 else 0
                
                tree.insert('', 'end', values=(
                    formatted_date,
                    row[1],  # Product name
                    f"₱{row[2]:,.2f}",
                    f"{row[3]:,}",
                    f"{row[4]:,}",
                    f"₱{avg_txn:,.2f}"
                ))
                
        elif period_type == 'Weekly':
            columns = ('Week', 'Period', 'Product', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Daily Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center')  # Center align all columns
            
            tree.column('Week', width=80)
            tree.column('Period', width=150)
            tree.column('Product', width=200)
            tree.column('Revenue', width=100)
            tree.column('Items Sold', width=100)
            tree.column('Transactions', width=100)
            tree.column('Avg. Daily Revenue', width=120)
            
            for row in data:
                week_num = row[0].split('-W')[1]
                start_date = datetime.strptime(row[1], '%Y-%m-%d').strftime('%b %d')
                end_date = datetime.strptime(row[2], '%Y-%m-%d').strftime('%b %d')
                period = f"{start_date} - {end_date}"
                avg_daily = row[4] / 7  # Approximation
                
                tree.insert('', 'end', values=(
                    f"Week {week_num}",
                    period,
                    row[3],  # Product name
                    f"₱{row[4]:,.2f}",
                    f"{row[5]:,}",
                    f"{row[6]:,}",
                    f"₱{avg_daily:,.2f}"
                ))
                
        elif period_type == 'Monthly':
            columns = ('Month', 'Product', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Daily Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center')  # Center align all columns
            
            tree.column('Month', width=100)
            tree.column('Product', width=200)
            tree.column('Revenue', width=100)
            tree.column('Items Sold', width=100)
            tree.column('Transactions', width=100)
            tree.column('Avg. Daily Revenue', width=120)
            
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                        'July', 'August', 'September', 'October', 'November', 'December']
            
            for row in data:
                month_index = int(row[0]) - 1
                month_name = month_names[month_index]
                avg_daily = row[2] / 30  # Approximation
                
                tree.insert('', 'end', values=(
                    month_name,
                    row[1],  # Product name
                    f"₱{row[2]:,.2f}",
                    f"{row[3]:,}",
                    f"{row[4]:,}",
                    f"₱{avg_daily:,.2f}"
                ))
                
        elif period_type == 'Yearly':
            columns = ('Year', 'Product', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Monthly Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=8)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor='center')  # Center align all columns
            
            tree.column('Year', width=80)
            tree.column('Product', width=200)
            tree.column('Revenue', width=100)
            tree.column('Items Sold', width=100)
            tree.column('Transactions', width=100)
            tree.column('Avg. Monthly Revenue', width=120)
            
            for row in data:
                avg_monthly = row[2] / 12  # Approximation
                
                tree.insert('', 'end', values=(
                    row[0],
                    row[1],  # Product name
                    f"₱{row[2]:,.2f}",
                    f"{row[3]:,}",
                    f"{row[4]:,}",
                    f"₱{avg_monthly:,.2f}"
                ))
        
        # Check if tree was created - if not, show a message
        if tree is None:
            self.show_no_data_message(table_frame, f"Unable to display {period_type.lower()} data")
            return
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_no_data_message(self, parent, message):
        """Show message when no data is available"""
        msg_frame = ttk.Frame(parent, style='Content.TFrame')
        msg_frame.pack(fill='both', expand=True)
        
        ttk.Label(msg_frame, text=message, style='Placeholder.TLabel', justify='center').pack(expand=True)

    