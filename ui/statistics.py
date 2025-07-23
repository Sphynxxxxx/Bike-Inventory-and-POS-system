import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatisticsModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the statistics interface with charts and top buyers"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Statistics & Analytics", style='PageTitle.TLabel').pack(side='left')
        
        # Refresh button
        ttk.Button(header_frame, text="🔄 Refresh", command=self.refresh_statistics,
                  style='Secondary.TButton').pack(side='right')
        
        # Filter controls
        filter_frame = ttk.Frame(self.frame, style='Content.TFrame')
        filter_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        ttk.Label(filter_frame, text="Time Period:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.stats_period_var = tk.StringVar(value='Last 30 Days')
        period_combo = ttk.Combobox(filter_frame, textvariable=self.stats_period_var,
                                   values=['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'This Year', 'All Time'],
                                   state='readonly', style='Modern.TCombobox', width=15)
        period_combo.pack(side='left', padx=(0, 20))
        period_combo.bind('<<ComboboxSelected>>', self.update_statistics)
        
        # Main statistics content
        stats_content = ttk.Frame(self.frame, style='Content.TFrame')
        stats_content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Top row - Charts
        charts_row = ttk.Frame(stats_content, style='Content.TFrame')
        charts_row.pack(fill='x', pady=(0, 20))
        
        # Left chart - Monthly Sales Trend
        left_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        left_chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_monthly_sales_chart(left_chart_frame)
        
        # Right chart - Sales by Category
        right_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        right_chart_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.create_category_sales_chart(right_chart_frame)
        
        # Bottom row - Tables
        tables_row = ttk.Frame(stats_content, style='Content.TFrame')
        tables_row.pack(fill='both', expand=True)
        
        # Left table - Top Buyers
        top_buyers_frame = ttk.Frame(tables_row, style='Card.TFrame')
        top_buyers_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_top_buyers_table(top_buyers_frame)
        
        # Right table - Product Performance
        product_performance_frame = ttk.Frame(tables_row, style='Card.TFrame')
        product_performance_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.create_product_performance_table(product_performance_frame)
        
        return self.frame

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
        monthly_data = self.main_app.get_monthly_sales_data()
        
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
        
        # Chart area
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(10, 15))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 3), dpi=80, facecolor='white')
        ax = fig.add_subplot(111)
        
        # Get category sales data
        category_data = self.main_app.get_category_sales_data()
        
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

    def create_top_buyers_table(self, parent):
        """Create top buyers table"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Top Buyers", style='SectionTitle.TLabel').pack(side='left')
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('Rank', 'Customer', 'Purchases', 'Total Amount')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=8)
        
        # Configure columns
        tree.heading('Rank', text='#')
        tree.heading('Customer', text='Customer')
        tree.heading('Purchases', text='Purchases')
        tree.heading('Total Amount', text='Total Amount')
        
        tree.column('Rank', width=30)
        tree.column('Customer', width=120)
        tree.column('Purchases', width=80)
        tree.column('Total Amount', width=100)
        
        # Get top buyers data
        top_buyers = self.main_app.get_top_buyers()
        for i, buyer in enumerate(top_buyers, 1):
            tree.insert('', 'end', values=(
                f"{i:02d}",
                buyer[0][:15] + "..." if len(buyer[0]) > 15 else buyer[0],  # customer_name
                buyer[1],  # purchase_count
                f"₱{buyer[2]:,.2f}"  # total_amount
            ))
        
        tree.pack(fill='both', expand=True)

    def create_product_performance_table(self, parent):
        """Create product performance table"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        ttk.Label(header_frame, text="Top Products", style='SectionTitle.TLabel').pack(side='left')
        
        # Table
        table_frame = ttk.Frame(parent, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        columns = ('Rank', 'Product', 'Sold', 'Revenue')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Dashboard.Treeview', height=8)
        
        # Configure columns
        tree.heading('Rank', text='#')
        tree.heading('Product', text='Product')
        tree.heading('Sold', text='Sold')
        tree.heading('Revenue', text='Revenue')
        
        tree.column('Rank', width=30)
        tree.column('Product', width=120)
        tree.column('Sold', width=60)
        tree.column('Revenue', width=100)
        
        # Get top products data
        top_products = self.main_app.get_top_products()
        for i, product in enumerate(top_products, 1):
            tree.insert('', 'end', values=(
                f"{i:02d}",
                product[0][:15] + "..." if len(product[0]) > 15 else product[0],  # product_name
                product[1],  # quantity_sold
                f"₱{product[2]:,.2f}"  # total_revenue
            ))
        
        tree.pack(fill='both', expand=True)

    def refresh_statistics(self):
        """Refresh statistics interface"""
        if self.frame:
            # Destroy and recreate the statistics frame
            self.frame.destroy()
            return self.create_interface()
        return None

    def update_statistics(self, event=None):
        """Update statistics based on filter changes"""
        return self.refresh_statistics()

    def refresh(self):
        """Refresh the statistics interface"""
        return self.refresh_statistics()