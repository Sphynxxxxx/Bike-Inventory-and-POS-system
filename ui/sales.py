import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class SalesModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.current_view = 'monthly'  # Default view

    def create_interface(self):
        """Create the sales analysis interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        title_label = ttk.Label(header_frame, text="Procuct Sales Analysis", style='PageTitle.TLabel')
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
                                  values=['Daily', 'Weekly', 'Monthly', 'Yearly'],
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
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-30 days')
                GROUP BY DATE(sale_date)
                ORDER BY date DESC
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
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE DATE(sale_date) >= DATE('now', '-84 days')
                GROUP BY week
                ORDER BY week DESC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting weekly sales data: {e}")
            return []

    def get_monthly_sales_data(self, year):
        """Get monthly sales data for specific year"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%m', sale_date) as month,
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                WHERE strftime('%Y', sale_date) = ?
                GROUP BY month
                ORDER BY month
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
                    SUM(total) as revenue,
                    SUM(quantity) as items_sold,
                    COUNT(DISTINCT transaction_id) as transactions
                FROM sales 
                GROUP BY year
                ORDER BY year DESC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting yearly sales data: {e}")
            return []

    def display_daily_summary(self, data):
        """Display daily sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No daily sales data available")
            return
            
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_items = sum(row[2] for row in data)
        total_transactions = sum(row[3] for row in data)
        avg_revenue = total_revenue / len(data) if data else 0
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text="Total Revenue (30 days)", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Average Daily Revenue Card
        avg_card = ttk.Frame(cards_frame, style='Card.TFrame')
        avg_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(avg_card, text="📊", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(avg_card, text="Average Daily Revenue", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(avg_card, text=f"₱{avg_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Items Sold Card
        items_card = ttk.Frame(cards_frame, style='Card.TFrame')
        items_card.pack(side='left', fill='x', expand=True)
        ttk.Label(items_card, text="📦", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(items_card, text="Total Items Sold", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(items_card, text=f"{total_items:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Recent days table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Recent Daily Sales", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Date', 'Revenue', 'Items Sold', 'Transactions')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add data
        for row in data[:10]:  # Show last 10 days
            date_obj = datetime.strptime(row[0], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%b %d, %Y')
            tree.insert('', 'end', values=(
                formatted_date,
                f"₱{row[1]:,.2f}",
                f"{row[2]:,}",
                f"{row[3]:,}"
            ))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

    def display_weekly_summary(self, data):
        """Display weekly sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No weekly sales data available")
            return
            
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[3] for row in data)
        total_items = sum(row[4] for row in data)
        total_transactions = sum(row[5] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text="Total Revenue (12 weeks)", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Items Sold Card
        items_card = ttk.Frame(cards_frame, style='Card.TFrame')
        items_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(items_card, text="📦", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(items_card, text="Total Items Sold", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(items_card, text=f"{total_items:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Transactions Card
        trans_card = ttk.Frame(cards_frame, style='Card.TFrame')
        trans_card.pack(side='left', fill='x', expand=True)
        ttk.Label(trans_card, text="🛒", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(trans_card, text="Total Transactions", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(trans_card, text=f"{total_transactions:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Weekly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Weekly Sales Summary", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Week', 'Period', 'Revenue', 'Items Sold', 'Transactions')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=8)
        
        tree.heading('Week', text='Week')
        tree.heading('Period', text='Period')
        tree.heading('Revenue', text='Revenue')
        tree.heading('Items Sold', text='Items Sold')
        tree.heading('Transactions', text='Transactions')
        
        tree.column('Week', width=80)
        tree.column('Period', width=150)
        tree.column('Revenue', width=120)
        tree.column('Items Sold', width=100)
        tree.column('Transactions', width=100)
        
        # Add data
        for row in data:
            week_num = row[0].split('-W')[1]
            start_date = datetime.strptime(row[1], '%Y-%m-%d').strftime('%b %d')
            end_date = datetime.strptime(row[2], '%Y-%m-%d').strftime('%b %d')
            period = f"{start_date} - {end_date}"
            
            tree.insert('', 'end', values=(
                f"Week {week_num}",
                period,
                f"₱{row[3]:,.2f}",
                f"{row[4]:,}",
                f"{row[5]:,}"
            ))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

    def display_monthly_summary(self, data, year):
        """Display monthly sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, f"No monthly sales data available for {year}")
            return
            
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_items = sum(row[2] for row in data)
        total_transactions = sum(row[3] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text=f"Total Revenue ({year})", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Items Sold Card
        items_card = ttk.Frame(cards_frame, style='Card.TFrame')
        items_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(items_card, text="📦", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(items_card, text="Total Items Sold", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(items_card, text=f"{total_items:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Transactions Card
        trans_card = ttk.Frame(cards_frame, style='Card.TFrame')
        trans_card.pack(side='left', fill='x', expand=True)
        ttk.Label(trans_card, text="🛒", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(trans_card, text="Total Transactions", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(trans_card, text=f"{total_transactions:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Monthly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text=f"Monthly Sales Summary - {year}", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Month', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Revenue/Day')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Month names
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        # Add data
        for row in data:
            month_index = int(row[0]) - 1
            month_name = month_names[month_index]
            days_in_month = 30  # Approximation
            avg_daily = row[1] / days_in_month if days_in_month > 0 else 0
            
            tree.insert('', 'end', values=(
                month_name,
                f"₱{row[1]:,.2f}",
                f"{row[2]:,}",
                f"{row[3]:,}",
                f"₱{avg_daily:,.2f}"
            ))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

    def display_yearly_summary(self, data):
        """Display yearly sales summary"""
        if not data:
            self.show_no_data_message(self.summary_frame, "No yearly sales data available")
            return
            
        summary_frame = ttk.Frame(self.summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_items = sum(row[2] for row in data)
        total_transactions = sum(row[3] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text="Total Revenue (All Years)", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Items Sold Card
        items_card = ttk.Frame(cards_frame, style='Card.TFrame')
        items_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(items_card, text="📦", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(items_card, text="Total Items Sold", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(items_card, text=f"{total_items:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Transactions Card
        trans_card = ttk.Frame(cards_frame, style='Card.TFrame')
        trans_card.pack(side='left', fill='x', expand=True)
        ttk.Label(trans_card, text="🛒", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(trans_card, text="Total Transactions", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(trans_card, text=f"{total_transactions:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Yearly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Yearly Sales Summary", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Year', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Monthly Revenue')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add data
        for row in data:
            avg_monthly = row[1] / 12  # Approximation
            
            tree.insert('', 'end', values=(
                row[0],
                f"₱{row[1]:,.2f}",
                f"{row[2]:,}",
                f"{row[3]:,}",
                f"₱{avg_monthly:,.2f}"
            ))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

    def create_daily_charts(self, data):
        """Create daily sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No daily sales data available for charts")
            return
            
        # Reverse data for chronological order
        data.reverse()
        
        dates = [datetime.strptime(row[0], '%Y-%m-%d').strftime('%m-%d') for row in data]
        revenues = [row[1] for row in data]
        items_sold = [row[2] for row in data]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle('Daily Sales Analysis (Last 30 Days)', fontsize=14, fontweight='bold')
        
        # Revenue chart
        ax1.bar(dates, revenues, color='#00bcd4', alpha=0.7)
        ax1.set_title('Daily Revenue', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        ax1.tick_params(axis='x', rotation=0)
        
        # Items sold chart
        ax2.bar(dates, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Daily Items Sold', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Date')
        ax2.tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

    def create_weekly_charts(self, data):
        """Create weekly sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No weekly sales data available for charts")
            return
            
        # Reverse data for chronological order
        data.reverse()
        
        weeks = [f"Week {row[0].split('-W')[1]}" for row in data]
        revenues = [row[3] for row in data]
        items_sold = [row[4] for row in data]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle('Weekly Sales Analysis (Last 12 Weeks)', fontsize=14, fontweight='bold')
        
        # Revenue chart
        ax1.bar(weeks, revenues, color='#00bcd4', alpha=0.7)
        ax1.set_title('Weekly Revenue', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        ax1.tick_params(axis='x', rotation=0)
        
        # Items sold chart
        ax2.bar(weeks, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Weekly Items Sold', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Week')
        ax2.tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

    def create_monthly_charts(self, data, year):
        """Create monthly sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, f"No monthly sales data available for {year}")
            return
            
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create full year data (include months with 0 sales)
        full_data = []
        for i in range(1, 13):
            month_data = next((row for row in data if int(row[0]) == i), None)
            if month_data:
                full_data.append(month_data)
            else:
                full_data.append((str(i).zfill(2), 0.0, 0, 0))
        
        months = [month_names[i] for i in range(12)]
        revenues = [row[1] for row in full_data]
        items_sold = [row[2] for row in full_data]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle(f'Monthly Sales Analysis - {year}', fontsize=14, fontweight='bold')
        
        # Revenue chart
        ax1.bar(months, revenues, color='#00bcd4', alpha=0.7)
        ax1.set_title('Monthly Revenue', fontweight='bold')
        ax1.set_ylabel('Revenue (₱)')
        
        # Items sold chart
        ax2.bar(months, items_sold, color='#4caf50', alpha=0.7)
        ax2.set_title('Monthly Items Sold', fontweight='bold')
        ax2.set_ylabel('Items Sold')
        ax2.set_xlabel('Month')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

    def create_yearly_charts(self, data):
        """Create yearly sales charts"""
        if not data:
            self.show_no_data_message(self.charts_frame, "No yearly sales data available for charts")
            return
            
        years = [row[0] for row in data]
        revenues = [row[1] for row in data]
        items_sold = [row[2] for row in data]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle('Yearly Sales Analysis', fontsize=14, fontweight='bold')
        
        # Revenue chart
        ax1.bar(years, revenues, color='#00bcd4', alpha=0.7)
        ax1.set_title('Yearly Revenue', fontweight='bold')
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
        
        ttk.Label(table_frame, text=f"{period_type} Sales Detailed Data", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create treeview based on period type
        if period_type == 'Daily':
            columns = ('Date', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Transaction Value')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140)
            
            for row in data:
                date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%b %d, %Y')
                avg_txn = row[1] / row[3] if row[3] > 0 else 0
                
                tree.insert('', 'end', values=(
                    formatted_date,
                    f"₱{row[1]:,.2f}",
                    f"{row[2]:,}",
                    f"{row[3]:,}",
                    f"₱{avg_txn:,.2f}"
                ))
                
        elif period_type == 'Weekly':
            columns = ('Week', 'Period', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Daily Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
            
            tree.heading('Week', text='Week')
            tree.heading('Period', text='Period')
            tree.heading('Revenue', text='Revenue')
            tree.heading('Items Sold', text='Items Sold')
            tree.heading('Transactions', text='Transactions')
            tree.heading('Avg. Daily Revenue', text='Avg. Daily Revenue')
            
            tree.column('Week', width=80)
            tree.column('Period', width=150)
            tree.column('Revenue', width=120)
            tree.column('Items Sold', width=100)
            tree.column('Transactions', width=100)
            tree.column('Avg. Daily Revenue', width=120)
            
            for row in data:
                week_num = row[0].split('-W')[1]
                start_date = datetime.strptime(row[1], '%Y-%m-%d').strftime('%b %d')
                end_date = datetime.strptime(row[2], '%Y-%m-%d').strftime('%b %d')
                period = f"{start_date} - {end_date}"
                avg_daily = row[3] / 7  # Approximation
                
                tree.insert('', 'end', values=(
                    f"Week {week_num}",
                    period,
                    f"₱{row[3]:,.2f}",
                    f"{row[4]:,}",
                    f"{row[5]:,}",
                    f"₱{avg_daily:,.2f}"
                ))
                
        elif period_type == 'Monthly':
            columns = ('Month', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Daily Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            
            for row in data:
                month_index = int(row[0]) - 1
                month_name = month_names[month_index]
                avg_daily = row[1] / 30  # Approximation
                
                tree.insert('', 'end', values=(
                    month_name,
                    f"₱{row[1]:,.2f}",
                    f"{row[2]:,}",
                    f"{row[3]:,}",
                    f"₱{avg_daily:,.2f}"
                ))
                
        elif period_type == 'Yearly':
            columns = ('Year', 'Revenue', 'Items Sold', 'Transactions', 'Avg. Monthly Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=8)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            for row in data:
                avg_monthly = row[1] / 12  # Approximation
                
                tree.insert('', 'end', values=(
                    row[0],
                    f"₱{row[1]:,.2f}",
                    f"{row[2]:,}",
                    f"{row[3]:,}",
                    f"₱{avg_monthly:,.2f}"
                ))
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_no_data_message(self, parent, message):
        """Show message when no data is available"""
        msg_frame = ttk.Frame(parent, style='Content.TFrame')
        msg_frame.pack(fill='both', expand=True)
        
        ttk.Label(msg_frame, text=message, style='Placeholder.TLabel', justify='center').pack(expand=True)

    def export_sales_report(self):
        """Export sales report to CSV"""
        try:
            # Get current view data
            if self.current_view == 'daily':
                data = self.get_daily_sales_data()
                filename = f"daily_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                headers = ['Date', 'Revenue', 'Items_Sold', 'Transactions']
                
            elif self.current_view == 'weekly':
                data = self.get_weekly_sales_data()
                filename = f"weekly_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                headers = ['Week', 'Week_Start', 'Week_End', 'Revenue', 'Items_Sold', 'Transactions']
                
            elif self.current_view == 'monthly':
                year = int(self.year_var.get())
                data = self.get_monthly_sales_data(year)
                filename = f"monthly_sales_report_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                headers = ['Month', 'Revenue', 'Items_Sold', 'Transactions']
                
            elif self.current_view == 'yearly':
                data = self.get_yearly_sales_data()
                filename = f"yearly_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                headers = ['Year', 'Revenue', 'Items_Sold', 'Transactions']
            
            if not data:
                messagebox.showinfo("Export", "No data available to export.")
                return
            
            # Create CSV content
            csv_content = ','.join(headers) + '\n'
            for row in data:
                csv_content += ','.join(str(field) for field in row) + '\n'
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            messagebox.showinfo("Export Successful", f"Sales report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export sales report: {str(e)}")