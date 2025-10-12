import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np

class StatisticsModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.left_chart_frame = None
        self.right_chart_frame = None
        self.top_buyers_frame = None
        self.product_performance_frame = None
        self.line_anim = None  # Store animation reference
        self.pie_anim = None   # Store animation reference
        
    def create_interface(self):
        """Create the statistics interface with charts and top buyers"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Statistics & Analytics", style='PageTitle.TLabel').pack(side='left')
        
        # Filter controls
        filter_frame = ttk.Frame(self.frame, style='Content.TFrame')
        filter_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        # Year selector
        ttk.Label(filter_frame, text="Year:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.year_var = tk.StringVar(value=str(self.main_app.get_available_years()[0]))
        year_combo = ttk.Combobox(filter_frame, textvariable=self.year_var,
                                  values=self.main_app.get_available_years(),
                                  state='readonly', style='Modern.TCombobox', width=10)
        year_combo.pack(side='left', padx=(0, 20))
        year_combo.bind('<<ComboboxSelected>>', self.on_year_changed)
        
        # Month selector
        ttk.Label(filter_frame, text="Month:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.month_var = tk.StringVar(value='All Months')
        month_values = ['All Months', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_combo = ttk.Combobox(filter_frame, textvariable=self.month_var,
                                   values=month_values,
                                   state='readonly', style='Modern.TCombobox', width=12)
        month_combo.pack(side='left', padx=(0, 20))
        month_combo.bind('<<ComboboxSelected>>', self.update_statistics)
        
        # Report Type selector
        ttk.Label(filter_frame, text="Report Type:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.report_type_var = tk.StringVar(value='Monthly')
        report_type_combo = ttk.Combobox(filter_frame, textvariable=self.report_type_var,
                                        values=['Daily', 'Weekly', 'Monthly', 'Yearly'],
                                        state='readonly', style='Modern.TCombobox', width=12)
        report_type_combo.pack(side='left')
        report_type_combo.bind('<<ComboboxSelected>>', self.update_statistics)
        
        # Main statistics content
        stats_content = ttk.Frame(self.frame, style='Content.TFrame')
        stats_content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Top row - Charts
        charts_row = ttk.Frame(stats_content, style='Content.TFrame')
        charts_row.pack(fill='x', pady=(0, 20))
        
        # Left chart - Sales Trend
        self.left_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        self.left_chart_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_sales_trend_chart(self.left_chart_frame)
        
        # Right chart - Sales by Category
        self.right_chart_frame = ttk.Frame(charts_row, style='Card.TFrame')
        self.right_chart_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.create_category_sales_chart(self.right_chart_frame)
        
        # Bottom row - Tables
        tables_row = ttk.Frame(stats_content, style='Content.TFrame')
        tables_row.pack(fill='both', expand=True)
        
        # Left table - Top Buyers
        self.top_buyers_frame = ttk.Frame(tables_row, style='Card.TFrame')
        self.top_buyers_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.create_top_buyers_table(self.top_buyers_frame)
        
        # Right table - Product Performance
        self.product_performance_frame = ttk.Frame(tables_row, style='Card.TFrame')
        self.product_performance_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.create_product_performance_table(self.product_performance_frame)
        
        return self.frame

    def on_year_changed(self, event=None):
        """Handle year selection change"""
        # Reset month to 'All Months' when year changes
        self.month_var.set('All Months')
        self.update_statistics()

    def create_sales_trend_chart(self, parent):
        """Create sales trend chart based on filters with animation"""
        report_type = self.report_type_var.get() if hasattr(self, 'report_type_var') else 'Monthly'
        selected_month = self.month_var.get() if hasattr(self, 'month_var') else 'All Months'
        selected_year = self.year_var.get() if hasattr(self, 'year_var') else None
        
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        # Determine chart title based on selection
        if selected_month != 'All Months':
            chart_title = f"Daily Sales - {selected_month} {selected_year}"
        else:
            chart_title = f"{report_type} Sales Trend"
        
        ttk.Label(header_frame, text=chart_title, style='SectionTitle.TLabel').pack(side='left')
        
        # Chart area
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(10, 15))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor='white')  
        ax = fig.add_subplot(111)
        
        # Get sales data based on selection
        if selected_month != 'All Months':
            sales_data = self.main_app.get_specific_month_sales_data(selected_month, selected_year)
            xlabel = 'Day'
        elif report_type == 'Daily':
            sales_data = self.main_app.get_daily_sales_data()
            xlabel = 'Date'
        elif report_type == 'Weekly':
            sales_data = self.main_app.get_weekly_sales_data()
            xlabel = 'Week'
        elif report_type == 'Yearly':
            sales_data = self.main_app.get_yearly_sales_data()
            xlabel = 'Year'
        else:  # Monthly
            sales_data = self.main_app.get_monthly_sales_data(selected_year)
            xlabel = 'Month'
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        
        if sales_data:
            labels = [row[0] for row in sales_data]
            revenue = [row[1] for row in sales_data]
            items_sold = [row[2] for row in sales_data]
            
            # Create dual axis chart
            ax2 = ax.twinx()
            
            # Initialize empty plots
            line, = ax.plot([], [], color='#3b82f6', linewidth=2, marker='o', 
                           markersize=4, label='Sales Revenue (₱)')
            bars = ax2.bar(range(len(labels)), [0] * len(items_sold), alpha=0.3, 
                          color='#94a3b8', label='Items Sold')
            
            ax.set_xlabel(xlabel, fontsize=9)
            ax.set_ylabel('Sales Revenue (₱)', color='#3b82f6', fontsize=9)
            ax2.set_ylabel('Items Sold', color='#94a3b8', fontsize=9)
            ax.tick_params(axis='y', labelcolor='#3b82f6', labelsize=8)
            ax2.tick_params(axis='y', labelcolor='#94a3b8', labelsize=8)
            
            # Set x-axis labels
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            
            # Set axis limits
            ax.set_xlim(-0.5, len(labels) - 0.5)
            max_revenue = max(revenue) if revenue else 1
            max_items = max(items_sold) if items_sold else 1
            ax.set_ylim(0, max_revenue * 1.1)
            ax2.set_ylim(0, max_items * 1.2)
            
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('white')
            
            # Animation function
            frames = 40  # Number of frames for animation
            
            def animate(frame):
                # Calculate progress (0 to 1)
                progress = (frame + 1) / frames
                
                # Animate line - show points progressively
                num_points = max(1, int(progress * len(labels)))
                line.set_data(range(num_points), revenue[:num_points])
                
                # Animate bars - grow height
                for i, bar in enumerate(bars):
                    bar.set_height(items_sold[i] * progress)
                
                return [line] + list(bars)
            
            # Create animation and store reference
            self.line_anim = FuncAnimation(fig, animate, frames=frames, 
                                          interval=25, blit=True, repeat=False)
            
        else:
            ax.text(0.5, 0.5, 'No sales data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='#6b7280')
            ax.set_facecolor('white')
        
        fig.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_category_sales_chart(self, parent):
        """Create sales by category pie chart with progressive drawing animation"""
        # Header
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(15, 0))
        
        ttk.Label(header_frame, text="Sales by Category", style='SectionTitle.TLabel').pack(side='left')
        
        # Chart area
        chart_frame = ttk.Frame(parent, style='Card.TFrame')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=(10, 15))
        
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 5), dpi=100, facecolor='white')  
        ax = fig.add_subplot(111)
        
        # Get category sales data
        category_data = self.main_app.get_category_sales_data()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
        if category_data:
            categories = [row[0] if row[0] else 'Other' for row in category_data]
            amounts = [row[1] for row in category_data]
            
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            
            # Calculate cumulative percentages for each slice
            total = sum(amounts)
            percentages = [(amount / total) * 100 for amount in amounts]
            cumulative_percentages = []
            cumsum = 0
            for p in percentages:
                cumsum += p
                cumulative_percentages.append(cumsum)
            
            # Animation function - PROGRESSIVE CIRCLE DRAWING
            frames = 50  # Number of frames for animation
            
            def animate(frame):
                # Calculate progress (0 to 100%)
                progress = ((frame + 1) / frames) * 100
                
                # Clear the axes
                ax.clear()
                
                # Calculate which slices to show based on progress
                visible_amounts = []
                visible_labels = []
                visible_colors = []
                
                for i, (amount, label, color, cum_pct) in enumerate(zip(amounts, categories, colors[:len(amounts)], cumulative_percentages)):
                    if i == 0:
                        prev_cum = 0
                    else:
                        prev_cum = cumulative_percentages[i-1]
                    
                    if progress >= cum_pct:
                        # Fully visible
                        visible_amounts.append(amount)
                        visible_labels.append(label)
                        visible_colors.append(color)
                    elif progress > prev_cum:
                        # Partially visible - calculate partial amount
                        slice_percentage = percentages[i]
                        slice_progress = (progress - prev_cum) / slice_percentage
                        partial_amount = amount * slice_progress
                        visible_amounts.append(partial_amount)
                        visible_labels.append(label)
                        visible_colors.append(color)
                
                if visible_amounts and sum(visible_amounts) > 0:
                    try:
                        # Draw pie chart with visible slices
                        wedges, texts, autotexts = ax.pie(
                            visible_amounts, 
                            labels=visible_labels,
                            autopct=lambda pct: f'{pct:.1f}%' if progress > 30 else '',
                            colors=visible_colors, 
                            startangle=90,
                            counterclock=False  # Draw clockwise
                        )
                        
                        # Style the text
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontsize(8)
                            autotext.set_weight('bold')
                        
                        ax.set_facecolor('white')
                        
                    except Exception as e:
                        print(f"Animation error: {e}")
                
                canvas.draw_idle()
                return []
            
            # Create animation and store reference
            self.pie_anim = FuncAnimation(
                fig, 
                animate, 
                frames=frames, 
                interval=30,  # 30ms between frames
                blit=False,   # blit=False is important for pie charts
                repeat=False  # Play once
            )
            
        else:
            ax.text(0.5, 0.5, 'No sales data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12, color='#6b7280')
            ax.set_facecolor('white')
            canvas.draw()
        
        fig.tight_layout()

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
        
        # Configure columns with CENTER alignment
        tree.heading('Rank', text='#', anchor='center')
        tree.heading('Customer', text='Customer', anchor='center')
        tree.heading('Purchases', text='Purchases', anchor='center')
        tree.heading('Total Amount', text='Total Amount', anchor='center')
        
        tree.column('Rank', width=30, anchor='center')
        tree.column('Customer', width=120, anchor='center')
        tree.column('Purchases', width=80, anchor='center')
        tree.column('Total Amount', width=100, anchor='center')
        
        # Get top buyers data
        top_buyers = self.main_app.get_top_buyers()
        for i, buyer in enumerate(top_buyers, 1):
            tree.insert('', 'end', values=(
                f"{i:02d}",
                buyer[0][:15] + "..." if len(buyer[0]) > 15 else buyer[0],
                buyer[1],
                f"₱{buyer[2]:,.2f}"
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
        
        # Configure columns with CENTER alignment
        tree.heading('Rank', text='#', anchor='center')
        tree.heading('Product', text='Product', anchor='center')
        tree.heading('Sold', text='Sold', anchor='center')
        tree.heading('Revenue', text='Revenue', anchor='center')
        
        tree.column('Rank', width=30, anchor='center')
        tree.column('Product', width=120, anchor='center')
        tree.column('Sold', width=60, anchor='center')
        tree.column('Revenue', width=100, anchor='center')
        
        # Get top products data
        top_products = self.main_app.get_top_products()
        for i, product in enumerate(top_products, 1):
            tree.insert('', 'end', values=(
                f"{i:02d}",
                product[0][:15] + "..." if len(product[0]) > 15 else product[0],
                product[1],
                f"₱{product[2]:,.2f}"
            ))
        
        tree.pack(fill='both', expand=True)

    def refresh_statistics(self):
        """Refresh statistics interface"""
        if self.frame:
            self.frame.destroy()
            return self.create_interface()
        return None

    def update_statistics(self, event=None):
        """Update statistics based on filter changes"""
        try:
            if self.left_chart_frame:
                for widget in self.left_chart_frame.winfo_children():
                    widget.destroy()
                self.create_sales_trend_chart(self.left_chart_frame)
            
            if self.right_chart_frame:
                for widget in self.right_chart_frame.winfo_children():
                    widget.destroy()
                self.create_category_sales_chart(self.right_chart_frame)
            
            if self.top_buyers_frame:
                for widget in self.top_buyers_frame.winfo_children():
                    widget.destroy()
                self.create_top_buyers_table(self.top_buyers_frame)
            
            if self.product_performance_frame:
                for widget in self.product_performance_frame.winfo_children():
                    widget.destroy()
                self.create_product_performance_table(self.product_performance_frame)
                
        except Exception as e:
            print(f"Error updating statistics: {e}")

    def refresh(self):
        """Refresh the statistics interface"""
        return self.refresh_statistics()