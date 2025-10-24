import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3

class ServiceDialog:
    def __init__(self, parent, title, service_data=None):
        self.result = None
        try:
            self.dialog = tk.Toplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("500x400")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.configure(bg='#ffffff')
            
            # Center the dialog
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
            self.dialog.geometry(f"500x400+{x}+{y}")
            
            self.create_widgets(service_data)
            
            # Focus on the first entry
            self.name_entry.focus_set()
            
            self.dialog.wait_window()
        except Exception as e:
            print(f"Error creating ServiceDialog: {e}")
            messagebox.showerror("Error", f"Failed to create service dialog: {str(e)}")

    def create_widgets(self, service_data):
        try:
            main_frame = ttk.Frame(self.dialog, padding="30")
            main_frame.pack(fill='both', expand=True)

            # Title
            title_label = ttk.Label(main_frame, text="Service Information", 
                                   font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')

            # Service Name
            ttk.Label(main_frame, text="Service Name*:", font=('Arial', 10, 'bold')).grid(
                row=1, column=0, sticky='w', pady=8)
            self.name_var = tk.StringVar(value=service_data[1] if service_data else "")
            self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
            self.name_entry.grid(row=1, column=1, pady=8, sticky='ew')

            # Service ID
            ttk.Label(main_frame, text="Service ID*:", font=('Arial', 10, 'bold')).grid(
                row=2, column=0, sticky='w', pady=8)
            self.service_id_var = tk.StringVar(value=service_data[6] if service_data else "")
            self.service_id_entry = ttk.Entry(main_frame, textvariable=self.service_id_var, width=40)
            self.service_id_entry.grid(row=2, column=1, pady=8, sticky='ew')

            # Category
            ttk.Label(main_frame, text="Category*:", font=('Arial', 10, 'bold')).grid(
                row=3, column=0, sticky='w', pady=8)
            self.category_var = tk.StringVar(value=service_data[5] if service_data else "Cleaning")
            self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=37)
            self.category_combo['values'] = ('Cleaning', 'Assembly', 'Suspension', 'Drivetrain', 'Wheels', 'Brakes', 'General')
            self.category_combo.state(['readonly'])
            self.category_combo.grid(row=3, column=1, pady=8, sticky='ew')

            # Price
            ttk.Label(main_frame, text="Price (₱)*:", font=('Arial', 10, 'bold')).grid(
                row=4, column=0, sticky='w', pady=8)
            self.price_var = tk.StringVar(value=str(service_data[3]) if service_data else "0.00")
            self.price_entry = ttk.Entry(main_frame, textvariable=self.price_var, width=40)
            self.price_entry.grid(row=4, column=1, pady=8, sticky='ew')

            # Duration - FIXED: Use correct index
            ttk.Label(main_frame, text="Duration:", font=('Arial', 10, 'bold')).grid(
                row=5, column=0, sticky='w', pady=8)
            duration_value = service_data[4] if service_data and len(service_data) > 4 else "30 minutes"
            self.duration_var = tk.StringVar(value=duration_value)
            self.duration_entry = ttk.Entry(main_frame, textvariable=self.duration_var, width=40)
            self.duration_entry.grid(row=5, column=1, pady=8, sticky='ew')

            # Status (only for edit mode)
            if service_data:
                ttk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(
                    row=6, column=0, sticky='w', pady=8)
                # service_data[7] is is_active boolean
                self.status_var = tk.StringVar(value="Active" if service_data[7] else "Inactive")
                self.status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, width=37)
                self.status_combo['values'] = ('Active', 'Inactive')
                self.status_combo.state(['readonly'])
                self.status_combo.grid(row=6, column=1, pady=8, sticky='ew')
            else:
                self.status_var = tk.StringVar(value="Active")  # Default for new services

            # Configure column weights
            main_frame.columnconfigure(1, weight=1)

            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=7, column=0, columnspan=2, pady=30, sticky='ew')

            cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel)
            cancel_btn.pack(side='right', padx=(10, 0))
            
            save_btn = ttk.Button(button_frame, text="Save Service", command=self.save)
            save_btn.pack(side='right')
            
            # Bind Enter key to save
            self.dialog.bind('<Return>', lambda e: self.save())
            self.dialog.bind('<Escape>', lambda e: self.cancel())
            
        except Exception as e:
            print(f"Error creating widgets in ServiceDialog: {e}")

    def save(self):
        try:
            # Get values and strip whitespace
            name = self.name_var.get().strip()
            service_id = self.service_id_var.get().strip()
            category = self.category_var.get().strip()
            price_str = self.price_var.get().strip()
            duration = self.duration_var.get().strip()
            status = self.status_var.get().strip()

            # Validate required fields
            if not name:
                messagebox.showerror("Validation Error", "Service name is required!")
                self.name_entry.focus_set()
                return
                
            if not service_id:
                messagebox.showerror("Validation Error", "Service ID is required!")
                self.service_id_entry.focus_set()
                return

            if not category:
                messagebox.showerror("Validation Error", "Category is required!")
                self.category_combo.focus_set()
                return

            # Validate and convert price
            try:
                price = float(price_str) if price_str else 0.0
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid price!")
                self.price_entry.focus_set()
                return

            # Validate price range
            if price < 0:
                messagebox.showerror("Validation Error", "Price cannot be negative!")
                self.price_entry.focus_set()
                return

            # Set default duration if empty
            if not duration:
                duration = "30 minutes"

            # Convert status to boolean
            is_active = 1 if status == "Active" else 0

            # Create result dictionary
            self.result = {
                'name': name,
                'service_id': service_id,
                'category': category,
                'price': price,
                'duration': duration,
                'description': '',  
                'is_active': is_active
            }
            
            print(f"ServiceDialog result: {self.result}")  
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            print(f"Error in ServiceDialog.save(): {e}")

    def cancel(self):
        try:
            self.result = None
            self.dialog.destroy()
        except Exception as e:
            print(f"Error in ServiceDialog.cancel(): {e}")

class ServicesModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.init_services_database()
        
        # NEW: Initialize variables for service sales
        self.sales_period_var = None
        self.service_year_var = None
        self.service_year_combo = None
        self.service_year_frame = None
        self.service_sales_notebook = None
        self.service_summary_frame = None
        self.service_charts_frame = None
        self.service_detailed_frame = None
        
    def insert_default_services(self):
        """Insert default services into the database"""
        default_services = [
            ('Basic Tune-Up', 'Complete bike inspection, adjustment of brakes, gears, and bearings', 500.00, '1 hour', 'General', 'SRV001'),
            ('Full Bike Service', 'Comprehensive service including cleaning, lubrication, and full adjustment', 1000.00, '2 hours', 'General', 'SRV002'),
            ('Wheel Truing', 'Straightening and tensioning of wheel', 300.00, '45 minutes', 'Wheels', 'SRV003'),
            ('Brake Service', 'Brake pad replacement and adjustment', 250.00, '30 minutes', 'Brakes', 'SRV004'),
            ('Drivetrain Cleaning', 'Deep cleaning of chain, cassette, and chainrings', 350.00, '1 hour', 'Drivetrain', 'SRV005'),
            ('Basic Bike Wash', 'External cleaning and basic lubrication', 200.00, '30 minutes', 'Cleaning', 'SRV006'),
            ('Suspension Service', 'Fork and shock maintenance', 800.00, '2 hours', 'Suspension', 'SRV007'),
            ('Bike Assembly', 'Complete bike assembly from box', 1500.00, '3 hours', 'Assembly', 'SRV008')
        ]
        
        try:
            self.main_app.cursor.executemany('''
                INSERT INTO services (name, description, price, duration, category, service_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', default_services)
            self.main_app.conn.commit()
            print("Default services inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting default services: {e}")
            
    def init_services_database(self):
        """Initialize services-related database tables"""
        try:
            # Create services table
            self.main_app.cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL DEFAULT 0.0,
                    duration TEXT DEFAULT '30 minutes',
                    category TEXT DEFAULT 'Service',
                    service_id TEXT UNIQUE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create service_bookings table
            self.main_app.cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id TEXT UNIQUE NOT NULL,
                    service_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_contact TEXT,
                    bike_details TEXT,
                    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scheduled_date TEXT,
                    scheduled_time TEXT,
                    status TEXT DEFAULT 'Pending',
                    notes TEXT,
                    price REAL NOT NULL,
                    payment_status TEXT DEFAULT 'Unpaid',
                    completed_date TIMESTAMP
                )
            ''')
            
            # Insert default services if table is empty
            self.main_app.cursor.execute('SELECT COUNT(*) FROM services')
            if self.main_app.cursor.fetchone()[0] == 0:
                self.insert_default_services()
            
            self.main_app.conn.commit()
            print("Services database initialized successfully")
            
        except sqlite3.Error as e:
            print(f"Error initializing services database: {e}")
    
        
    def create_interface(self):
        """Create the services interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Services", style='PageTitle.TLabel').pack(side='left')
        
        # Tab control for Services and Service History
        try:
            notebook = ttk.Notebook(self.frame)
            notebook.pack(fill='both', expand=True, padx=30, pady=(0, 20))
            
            # Services tab
            services_tab = ttk.Frame(notebook, style='Content.TFrame')
            notebook.add(services_tab, text='Available Services')
            self.create_services_tab(services_tab)
            
            # Service History tab
            history_tab = ttk.Frame(notebook, style='Content.TFrame')
            notebook.add(history_tab, text='Service History')
            self.create_service_history_tab(history_tab)
            
            # Service Sales tab - UPDATED: Use the new chart-based version
            sales_tab = ttk.Frame(notebook, style='Content.TFrame')
            notebook.add(sales_tab, text='Service Sales')
            self.create_service_sales_tab(sales_tab)
            
        except Exception as e:
            print(f"Error creating notebook: {e}")
            # Fall back to simple frame if notebook fails
            self.create_services_tab(self.frame)
        
        return self.frame

    def create_service_sales_tab(self, parent):
        """Create the service sales analysis tab with charts and time period analysis"""
        # Header
        header_frame = ttk.Frame(parent, style='Content.TFrame')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Service Sales Analysis", 
                 style='SectionTitle.TLabel').pack(side='left')
        
        # Controls frame
        controls_frame = ttk.Frame(parent, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Time period selector
        period_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        period_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Label(period_frame, text="View:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=10)
        
        self.sales_period_var = tk.StringVar(value='Monthly')
        period_combo = ttk.Combobox(period_frame, textvariable=self.sales_period_var,
                              values=['Daily', 'Weekly', 'Monthly', 'Yearly'],
                              state='readonly', style='Modern.TCombobox', width=15)
        period_combo.pack(side='left', padx=(0, 15), pady=10)
        period_combo.bind('<<ComboboxSelected>>', self.load_service_sales_data)
        
        # Year selector for monthly/yearly views
        self.service_year_frame = ttk.Frame(controls_frame, style='Card.TFrame')
        self.service_year_frame.pack(side='left', fill='x', padx=(20, 0))
        
        ttk.Label(self.service_year_frame, text="Year:", style='FieldLabel.TLabel').pack(side='left', padx=(15, 10), pady=10)
        
        self.service_year_var = tk.StringVar(value=str(datetime.now().year))
        self.service_year_combo = ttk.Combobox(self.service_year_frame, textvariable=self.service_year_var,
                                         state='readonly', style='Modern.TCombobox', width=10)
        self.service_year_combo.pack(side='left', padx=(0, 15), pady=10)
        self.service_year_combo.bind('<<ComboboxSelected>>', self.load_service_sales_data)
        

        
        # Main content area with notebook for different views
        content_frame = ttk.Frame(parent, style='Content.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create notebook for different views
        self.service_sales_notebook = ttk.Notebook(content_frame)
        self.service_sales_notebook.pack(fill='both', expand=True)
        
        # Summary tab
        self.service_summary_frame = ttk.Frame(self.service_sales_notebook, style='Content.TFrame')
        self.service_sales_notebook.add(self.service_summary_frame, text="Summary")
        
        # Charts tab
        self.service_charts_frame = ttk.Frame(self.service_sales_notebook, style='Content.TFrame')
        self.service_sales_notebook.add(self.service_charts_frame, text="Charts")
        
        # Detailed Data tab
        self.service_detailed_frame = ttk.Frame(self.service_sales_notebook, style='Content.TFrame')
        self.service_sales_notebook.add(self.service_detailed_frame, text="Detailed Data")
        
        # Initialize year selector and load data
        self.update_service_year_selector()
        self.load_service_sales_data()

    def update_service_year_selector(self):
        """Update available years in the service year selector"""
        try:
            self.main_app.cursor.execute('''
                SELECT DISTINCT strftime('%Y', booking_date) as year
                FROM service_bookings 
                WHERE booking_date IS NOT NULL
                ORDER BY year DESC
            ''')
            results = self.main_app.cursor.fetchall()
            available_years = [row[0] for row in results] if results else [str(datetime.now().year)]
            self.service_year_combo['values'] = available_years
            if available_years:
                self.service_year_var.set(available_years[0])
        except Exception as e:
            print(f"Error updating service year selector: {e}")

    def load_service_sales_data(self, event=None):
        """Load service sales data based on current view"""
        try:
            period = self.sales_period_var.get().lower()
            
            # Clear previous data
            self.clear_service_sales_frames()
            
            # Get data based on current view
            if period == 'daily':
                data = self.get_service_daily_data()
                self.display_service_daily_summary(data)
                self.create_service_daily_charts(data)
                self.display_service_detailed_data(data, 'Daily')
                
            elif period == 'weekly':
                data = self.get_service_weekly_data()
                self.display_service_weekly_summary(data)
                self.create_service_weekly_charts(data)
                self.display_service_detailed_data(data, 'Weekly')
                
            elif period == 'monthly':
                year = int(self.service_year_var.get())
                data = self.get_service_monthly_data(year)
                self.display_service_monthly_summary(data, year)
                self.create_service_monthly_charts(data, year)
                self.display_service_detailed_data(data, 'Monthly')
                
            elif period == 'yearly':
                data = self.get_service_yearly_data()
                self.display_service_yearly_summary(data)
                self.create_service_yearly_charts(data)
                self.display_service_detailed_data(data, 'Yearly')
                
        except Exception as e:
            print(f"Error loading service sales data: {e}")
            messagebox.showerror("Error", f"Failed to load service sales data: {str(e)}")

    def clear_service_sales_frames(self):
        """Clear all service sales display frames"""
        for widget in self.service_summary_frame.winfo_children():
            widget.destroy()
        for widget in self.service_charts_frame.winfo_children():
            widget.destroy()
        for widget in self.service_detailed_frame.winfo_children():
            widget.destroy()

    def get_service_daily_data(self):
        """Get daily service data for the last 30 days"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    DATE(booking_date) as date,
                    SUM(price) as revenue,
                    COUNT(*) as services_count,
                    COUNT(DISTINCT customer_name) as unique_customers
                FROM service_bookings 
                WHERE DATE(booking_date) >= DATE('now', '-30 days')
                GROUP BY DATE(booking_date)
                ORDER BY date DESC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting daily service data: {e}")
            return []

    def get_service_weekly_data(self):
        """Get weekly service data for the last 12 weeks"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%Y-W%W', booking_date) as week,
                    MIN(DATE(booking_date, 'weekday 0', '-6 days')) as week_start,
                    MAX(DATE(booking_date, 'weekday 0')) as week_end,
                    SUM(price) as revenue,
                    COUNT(*) as services_count,
                    COUNT(DISTINCT customer_name) as unique_customers
                FROM service_bookings 
                WHERE DATE(booking_date) >= DATE('now', '-84 days')
                GROUP BY week
                ORDER BY week DESC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting weekly service data: {e}")
            return []

    def get_service_monthly_data(self, year):
        """Get monthly service data for specific year"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%m', booking_date) as month,
                    SUM(price) as revenue,
                    COUNT(*) as services_count,
                    COUNT(DISTINCT customer_name) as unique_customers
                FROM service_bookings 
                WHERE strftime('%Y', booking_date) = ?
                GROUP BY month
                ORDER BY month
            ''', (str(year),))
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting monthly service data: {e}")
            return []

    def get_service_yearly_data(self):
        """Get yearly service data"""
        try:
            self.main_app.cursor.execute('''
                SELECT 
                    strftime('%Y', booking_date) as year,
                    SUM(price) as revenue,
                    COUNT(*) as services_count,
                    COUNT(DISTINCT customer_name) as unique_customers
                FROM service_bookings 
                GROUP BY year
                ORDER BY year DESC
            ''')
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting yearly service data: {e}")
            return []

    def display_service_daily_summary(self, data):
        """Display daily service sales summary"""
        if not data:
            self.show_no_service_data_message(self.service_summary_frame, "No daily service data available")
            return
            
        summary_frame = ttk.Frame(self.service_summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_services = sum(row[2] for row in data)
        total_customers = sum(row[3] for row in data)
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
        
        # Services Completed Card
        services_card = ttk.Frame(cards_frame, style='Card.TFrame')
        services_card.pack(side='left', fill='x', expand=True)
        ttk.Label(services_card, text="🔧", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(services_card, text="Services Completed", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(services_card, text=f"{total_services:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Recent days table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Recent Daily Service Sales", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Date', 'Revenue', 'Services', 'Customers')
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

    def display_service_weekly_summary(self, data):
        """Display weekly service sales summary"""
        if not data:
            self.show_no_service_data_message(self.service_summary_frame, "No weekly service data available")
            return
            
        summary_frame = ttk.Frame(self.service_summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[3] for row in data)
        total_services = sum(row[4] for row in data)
        total_customers = sum(row[5] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text="Total Revenue (12 weeks)", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Services Completed Card
        services_card = ttk.Frame(cards_frame, style='Card.TFrame')
        services_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(services_card, text="🔧", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(services_card, text="Services Completed", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(services_card, text=f"{total_services:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Unique Customers Card
        customers_card = ttk.Frame(cards_frame, style='Card.TFrame')
        customers_card.pack(side='left', fill='x', expand=True)
        ttk.Label(customers_card, text="👥", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(customers_card, text="Unique Customers", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(customers_card, text=f"{total_customers:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Weekly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Weekly Service Sales Summary", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Week', 'Period', 'Revenue', 'Services', 'Customers')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=8)
        
        tree.heading('Week', text='Week')
        tree.heading('Period', text='Period')
        tree.heading('Revenue', text='Revenue')
        tree.heading('Services', text='Services')
        tree.heading('Customers', text='Customers')
        
        tree.column('Week', width=80)
        tree.column('Period', width=150)
        tree.column('Revenue', width=120)
        tree.column('Services', width=100)
        tree.column('Customers', width=100)
        
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

    def display_service_monthly_summary(self, data, year):
        """Display monthly service sales summary"""
        if not data:
            self.show_no_service_data_message(self.service_summary_frame, f"No monthly service data available for {year}")
            return
            
        summary_frame = ttk.Frame(self.service_summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_services = sum(row[2] for row in data)
        total_customers = sum(row[3] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text=f"Total Revenue ({year})", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Services Completed Card
        services_card = ttk.Frame(cards_frame, style='Card.TFrame')
        services_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(services_card, text="🔧", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(services_card, text="Services Completed", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(services_card, text=f"{total_services:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Unique Customers Card
        customers_card = ttk.Frame(cards_frame, style='Card.TFrame')
        customers_card.pack(side='left', fill='x', expand=True)
        ttk.Label(customers_card, text="👥", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(customers_card, text="Unique Customers", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(customers_card, text=f"{total_customers:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Monthly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text=f"Monthly Service Sales Summary - {year}", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Month', 'Revenue', 'Services', 'Customers', 'Avg. Revenue/Day')
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

    def display_service_yearly_summary(self, data):
        """Display yearly service sales summary"""
        if not data:
            self.show_no_service_data_message(self.service_summary_frame, "No yearly service data available")
            return
            
        summary_frame = ttk.Frame(self.service_summary_frame, style='Content.TFrame')
        summary_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Calculate totals
        total_revenue = sum(row[1] for row in data)
        total_services = sum(row[2] for row in data)
        total_customers = sum(row[3] for row in data)
        
        # Summary cards
        cards_frame = ttk.Frame(summary_frame, style='Content.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        # Total Revenue Card
        revenue_card = ttk.Frame(cards_frame, style='Card.TFrame')
        revenue_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(revenue_card, text="💰", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(revenue_card, text="Total Revenue (All Years)", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(revenue_card, text=f"₱{total_revenue:,.2f}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Services Completed Card
        services_card = ttk.Frame(cards_frame, style='Card.TFrame')
        services_card.pack(side='left', fill='x', expand=True, padx=(0, 15))
        ttk.Label(services_card, text="🔧", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(services_card, text="Total Services", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(services_card, text=f"{total_services:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Unique Customers Card
        customers_card = ttk.Frame(cards_frame, style='Card.TFrame')
        customers_card.pack(side='left', fill='x', expand=True)
        ttk.Label(customers_card, text="👥", style='CardIcon.TLabel').pack(anchor='w', padx=20, pady=(20, 5))
        ttk.Label(customers_card, text="Unique Customers", style='CardTitle.TLabel').pack(anchor='w', padx=20, pady=(0, 5))
        ttk.Label(customers_card, text=f"{total_customers:,}", style='CardValue.TLabel').pack(anchor='w', padx=20, pady=(0, 20))
        
        # Yearly table
        table_frame = ttk.Frame(summary_frame, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        ttk.Label(table_frame, text="Yearly Service Sales Summary", style='SectionTitle.TLabel').pack(anchor='w', padx=20, pady=20)
        
        # Create treeview
        columns = ('Year', 'Revenue', 'Services', 'Customers', 'Avg. Monthly Revenue')
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

    def create_service_daily_charts(self, data):
        """Create daily service sales charts"""
        if not data:
            self.show_no_service_data_message(self.service_charts_frame, "No daily service data available for charts")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Reverse data for chronological order
            data.reverse()
            
            dates = [datetime.strptime(row[0], '%Y-%m-%d').strftime('%m-%d') for row in data]
            revenues = [row[1] for row in data]
            services_count = [row[2] for row in data]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            fig.suptitle('Daily Service Sales Analysis (Last 30 Days)', fontsize=14, fontweight='bold')
            
            # Revenue chart
            ax1.bar(dates, revenues, color='#00bcd4', alpha=0.7)
            ax1.set_title('Daily Service Revenue', fontweight='bold')
            ax1.set_ylabel('Revenue (₱)')
            ax1.tick_params(axis='x', rotation=0)
            ax1.grid(axis='y', alpha=0.3)
            
            # Services count chart
            ax2.bar(dates, services_count, color='#4caf50', alpha=0.7)
            ax2.set_title('Daily Services Completed', fontweight='bold')
            ax2.set_ylabel('Services Count')
            ax2.set_xlabel('Date')
            ax2.tick_params(axis='x', rotation=0)
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.service_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
            
        except ImportError:
            self.show_no_service_data_message(self.service_charts_frame, "Matplotlib not available for charts")
        except Exception as e:
            print(f"Error creating daily charts: {e}")
            self.show_no_service_data_message(self.service_charts_frame, f"Error creating charts: {str(e)}")

    def create_service_weekly_charts(self, data):
        """Create weekly service sales charts"""
        if not data:
            self.show_no_service_data_message(self.service_charts_frame, "No weekly service data available for charts")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            # Reverse data for chronological order
            data.reverse()
            
            weeks = [f"Week {row[0].split('-W')[1]}" for row in data]
            revenues = [row[3] for row in data]
            services_count = [row[4] for row in data]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            fig.suptitle('Weekly Service Sales Analysis (Last 12 Weeks)', fontsize=14, fontweight='bold')
            
            # Revenue chart
            ax1.bar(weeks, revenues, color='#00bcd4', alpha=0.7)
            ax1.set_title('Weekly Service Revenue', fontweight='bold')
            ax1.set_ylabel('Revenue (₱)')
            ax1.tick_params(axis='x', rotation=0)
            ax1.grid(axis='y', alpha=0.3)
            
            # Services count chart
            ax2.bar(weeks, services_count, color='#4caf50', alpha=0.7)
            ax2.set_title('Weekly Services Completed', fontweight='bold')
            ax2.set_ylabel('Services Count')
            ax2.set_xlabel('Week')
            ax2.tick_params(axis='x', rotation=0)
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.service_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
            
        except ImportError:
            self.show_no_service_data_message(self.service_charts_frame, "Matplotlib not available for charts")
        except Exception as e:
            print(f"Error creating weekly charts: {e}")
            self.show_no_service_data_message(self.service_charts_frame, f"Error creating charts: {str(e)}")

    def create_service_monthly_charts(self, data, year):
        """Create monthly service sales charts"""
        if not data:
            self.show_no_service_data_message(self.service_charts_frame, f"No monthly service data available for {year}")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
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
            services_count = [row[2] for row in full_data]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            fig.suptitle(f'Monthly Service Sales Analysis - {year}', fontsize=14, fontweight='bold')
            
            # Revenue chart
            ax1.bar(months, revenues, color='#00bcd4', alpha=0.7)
            ax1.set_title('Monthly Service Revenue', fontweight='bold')
            ax1.set_ylabel('Revenue (₱)')
            ax1.grid(axis='y', alpha=0.3)
            
            # Services count chart
            ax2.bar(months, services_count, color='#4caf50', alpha=0.7)
            ax2.set_title('Monthly Services Completed', fontweight='bold')
            ax2.set_ylabel('Services Count')
            ax2.set_xlabel('Month')
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.service_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
            
        except ImportError:
            self.show_no_service_data_message(self.service_charts_frame, "Matplotlib not available for charts")
        except Exception as e:
            print(f"Error creating monthly charts: {e}")
            self.show_no_service_data_message(self.service_charts_frame, f"Error creating charts: {str(e)}")

    def create_service_yearly_charts(self, data):
        """Create yearly service sales charts"""
        if not data:
            self.show_no_service_data_message(self.service_charts_frame, "No yearly service data available for charts")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            
            years = [row[0] for row in data]
            revenues = [row[1] for row in data]
            services_count = [row[2] for row in data]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            fig.suptitle('Yearly Service Sales Analysis', fontsize=14, fontweight='bold')
            
            # Revenue chart
            ax1.bar(years, revenues, color='#00bcd4', alpha=0.7)
            ax1.set_title('Yearly Service Revenue', fontweight='bold')
            ax1.set_ylabel('Revenue (₱)')
            ax1.grid(axis='y', alpha=0.3)
            
            # Services count chart
            ax2.bar(years, services_count, color='#4caf50', alpha=0.7)
            ax2.set_title('Yearly Services Completed', fontweight='bold')
            ax2.set_ylabel('Services Count')
            ax2.set_xlabel('Year')
            ax2.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.service_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
            
        except ImportError:
            self.show_no_service_data_message(self.service_charts_frame, "Matplotlib not available for charts")
        except Exception as e:
            print(f"Error creating yearly charts: {e}")
            self.show_no_service_data_message(self.service_charts_frame, f"Error creating charts: {str(e)}")

    def display_service_detailed_data(self, data, period_type):
        """Display detailed service data in table format"""
        if not data:
            self.show_no_service_data_message(self.service_detailed_frame, f"No {period_type.lower()} service data available")
            return
            
        table_frame = ttk.Frame(self.service_detailed_frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(table_frame, text=f"{period_type} Service Sales Detailed Data", style='SectionTitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Create treeview based on period type
        if period_type == 'Daily':
            columns = ('Date', 'Revenue', 'Services', 'Customers', 'Avg. Service Value')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140)
            
            for row in data:
                date_obj = datetime.strptime(row[0], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%b %d, %Y')
                avg_service = row[1] / row[2] if row[2] > 0 else 0
                
                tree.insert('', 'end', values=(
                    formatted_date,
                    f"₱{row[1]:,.2f}",
                    f"{row[2]:,}",
                    f"{row[3]:,}",
                    f"₱{avg_service:,.2f}"
                ))
                
        elif period_type == 'Weekly':
            columns = ('Week', 'Period', 'Revenue', 'Services', 'Customers', 'Avg. Daily Revenue')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview', height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
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
            columns = ('Month', 'Revenue', 'Services', 'Customers', 'Avg. Daily Revenue')
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
            columns = ('Year', 'Revenue', 'Services', 'Customers', 'Avg. Monthly Revenue')
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

    def show_no_service_data_message(self, parent, message):
        """Show message when no service data is available"""
        msg_frame = ttk.Frame(parent, style='Content.TFrame')
        msg_frame.pack(fill='both', expand=True)
        
        ttk.Label(msg_frame, text=message, style='Placeholder.TLabel', justify='center').pack(expand=True)

    def export_service_sales_report(self):
        """Export service sales report to CSV"""
        try:
            period = self.sales_period_var.get().lower()
            filename = f"service_sales_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Get data based on period
            if period == 'daily':
                data = self.get_service_daily_data()
                headers = ['Date', 'Revenue', 'Services_Count', 'Unique_Customers']
            elif period == 'weekly':
                data = self.get_service_weekly_data()
                headers = ['Week', 'Week_Start', 'Week_End', 'Revenue', 'Services_Count', 'Unique_Customers']
            elif period == 'monthly':
                year = int(self.service_year_var.get())
                data = self.get_service_monthly_data(year)
                headers = ['Month', 'Revenue', 'Services_Count', 'Unique_Customers']
            elif period == 'yearly':
                data = self.get_service_yearly_data()
                headers = ['Year', 'Revenue', 'Services_Count', 'Unique_Customers']
            
            if not data:
                messagebox.showinfo("Export", "No service sales data available to export.")
                return
            
            # Create CSV content
            csv_content = ','.join(headers) + '\n'
            for row in data:
                csv_content += ','.join(str(field) for field in row) + '\n'
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            messagebox.showinfo("Export Successful", f"Service sales report exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export service sales report: {str(e)}")

    # ... (rest of the existing methods for services management remain the same)
    # The existing create_services_tab, create_service_history_tab, and all other methods continue below...

    def create_services_tab(self, parent):
        """Create the services management tab with search"""
        # Services controls
        controls_frame = ttk.Frame(parent, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(controls_frame, text="Add", command=self.add_service,
                style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit", command=self.edit_service,
                style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete", command=self.delete_service,
                style='Danger.TButton').pack(side='left', padx=(0, 10))
        
        # Search and Filter frame
        search_filter_frame = ttk.Frame(parent, style='Content.TFrame')
        search_filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Search box
        ttk.Label(search_filter_frame, text="Search:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.services_search_var = tk.StringVar()
        self.services_search_var.trace('w', lambda *args: self.search_services())
        search_entry = ttk.Entry(search_filter_frame, textvariable=self.services_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 20))
        
        # Category filter
        ttk.Label(search_filter_frame, text="Filter by Category:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.category_filter_var = tk.StringVar(value='All Categories')
        category_filter = ttk.Combobox(search_filter_frame, textvariable=self.category_filter_var,
                                    values=['All Categories', 'Cleaning', 'Assembly', 'Suspension', 
                                        'Drivetrain', 'Wheels', 'Brakes', 'General'],
                                    state='readonly', style='Modern.TCombobox', width=15)
        category_filter.pack(side='left')
        category_filter.bind('<<ComboboxSelected>>', self.filter_services)
        
        # Services table
        table_frame = ttk.Frame(parent, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for services
        columns = ('ID', 'Service ID', 'Name', 'Category', 'Price', 'Duration', 'Status')
        self.services_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                        style='Modern.Treeview')
        
        # Configure columns with CENTER alignment
        column_widths = {
            'ID': 50,
            'Service ID': 100,
            'Name': 200,
            'Category': 120,
            'Price': 100,
            'Duration': 120,
            'Status': 80
        }
        
        for col in columns:
            self.services_tree.heading(col, text=col, anchor='center')
            self.services_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Hide ID column
        self.services_tree.column('ID', width=0, stretch=False)
        self.services_tree.heading('ID', text='')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.services_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click for booking
        self.services_tree.bind('<Double-1>', self.book_service_from_tree)
        
        action_frame = ttk.Frame(parent, style='Content.TFrame')
        action_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(action_frame, text="📅 Select Service", 
                command=self.book_selected_service,
                style='Success.TButton').pack(side='left', padx=(0, 10))
        
        # Load services
        self.load_services()

    def create_service_history_tab(self, parent):
        """Create the service history tab with search"""
        # History controls
        history_controls = ttk.Frame(parent, style='Content.TFrame')
        history_controls.pack(fill='x', padx=20, pady=10)
        
        # Search box for history
        ttk.Label(history_controls, text="Search:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.history_search_var = tk.StringVar()
        self.history_search_var.trace('w', lambda *args: self.search_service_history())
        search_entry = ttk.Entry(history_controls, textvariable=self.history_search_var, width=30)
        search_entry.pack(side='left', padx=(0, 20))
        
        # Status filter
        ttk.Label(history_controls, text="Filter by Status:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.status_filter_var = tk.StringVar(value='All Status')
        status_filter = ttk.Combobox(history_controls, textvariable=self.status_filter_var,
                                values=['All Status', 'Pending', 'In Progress', 'Completed', 'Cancelled'],
                                state='readonly', style='Modern.TCombobox', width=15)
        status_filter.pack(side='left', padx=(0, 20))
        status_filter.bind('<<ComboboxSelected>>', self.filter_service_history)
        
        # Action buttons
        ttk.Button(history_controls, text="Delete Record", command=self.delete_service_history,
                style='Danger.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(history_controls, text="Update Status", command=self.update_booking_status,
                style='Secondary.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(history_controls, text="View Details", command=self.view_booking_details,
                style='Primary.TButton').pack(side='right', padx=(10, 0))
        
        # Service history table
        history_table_frame = ttk.Frame(parent, style='Content.TFrame')
        history_table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for service history
        history_columns = ('ID', 'Booking ID', 'Date', 'Customer', 'Service', 'Contact', 
                        'Status', 'Payment', 'Price')
        self.history_tree = ttk.Treeview(history_table_frame, columns=history_columns, 
                                        show='headings', style='Modern.Treeview')
        
        # Configure history columns with CENTER alignment
        history_widths = {
            'ID': 50,
            'Booking ID': 100,
            'Date': 100,
            'Customer': 150,
            'Service': 180,
            'Contact': 120,
            'Status': 100,
            'Payment': 100,
            'Price': 100
        }
        
        for col in history_columns:
            self.history_tree.heading(col, text=col, anchor='center')
            self.history_tree.column(col, width=history_widths.get(col, 100), anchor='center')
        
        # Hide ID column
        self.history_tree.column('ID', width=0, stretch=False)
        self.history_tree.heading('ID', text='')
        
        # Scrollbars for history
        h_v_scrollbar = ttk.Scrollbar(history_table_frame, orient='vertical', command=self.history_tree.yview)
        h_h_scrollbar = ttk.Scrollbar(history_table_frame, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=h_v_scrollbar.set, xscrollcommand=h_h_scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky='nsew')
        h_v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        history_table_frame.grid_rowconfigure(0, weight=1)
        history_table_frame.grid_columnconfigure(0, weight=1)
        
        # Load service history
        self.load_service_history()


    def search_services(self):
        """Search services by name, service ID, or category"""
        try:
            search_term = self.services_search_var.get().strip().lower()
            
            # Clear existing items
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)
            
            # Get category filter
            category_filter = self.category_filter_var.get()
            
            # Build query based on search and filter
            if category_filter == 'All Categories':
                if search_term:
                    self.main_app.cursor.execute('''
                        SELECT id, service_id, name, category, price, duration, is_active
                        FROM services 
                        WHERE LOWER(name) LIKE ? OR LOWER(service_id) LIKE ? OR LOWER(category) LIKE ?
                        ORDER BY category, name
                    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
                else:
                    self.main_app.cursor.execute('''
                        SELECT id, service_id, name, category, price, duration, is_active
                        FROM services 
                        ORDER BY category, name
                    ''')
            else:
                if search_term:
                    self.main_app.cursor.execute('''
                        SELECT id, service_id, name, category, price, duration, is_active
                        FROM services 
                        WHERE category = ? AND (LOWER(name) LIKE ? OR LOWER(service_id) LIKE ?)
                        ORDER BY name
                    ''', (category_filter, f'%{search_term}%', f'%{search_term}%'))
                else:
                    self.main_app.cursor.execute('''
                        SELECT id, service_id, name, category, price, duration, is_active
                        FROM services 
                        WHERE category = ?
                        ORDER BY name
                    ''', (category_filter,))
            
            services = self.main_app.cursor.fetchall()
            
            for service in services:
                status = 'Active' if service[6] else 'Inactive'
                self.services_tree.insert('', 'end', values=(
                    service[0],  # id (hidden)
                    service[1],  # service_id
                    service[2],  # name
                    service[3],  # category
                    f"₱{service[4]:.2f}",  # price
                    service[5],  # duration
                    status      # status
                ))
                
        except Exception as e:
            print(f"Error searching services: {e}")
            messagebox.showerror("Error", f"Failed to search services: {str(e)}")

    def search_service_history(self):
        """Search service history by customer name, booking ID, or service name"""
        try:
            search_term = self.history_search_var.get().strip().lower()
            
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Get status filter
            status_filter = self.status_filter_var.get()
            
            # Build query based on search and filter - REMOVED scheduled_date from SELECT
            if status_filter == 'All Status':
                if search_term:
                    self.main_app.cursor.execute('''
                        SELECT id, booking_id, booking_date, customer_name, service_name, 
                            customer_contact, status, payment_status, price
                        FROM service_bookings 
                        WHERE LOWER(customer_name) LIKE ? OR LOWER(booking_id) LIKE ? OR LOWER(service_name) LIKE ?
                        ORDER BY booking_date DESC
                    ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
                else:
                    self.main_app.cursor.execute('''
                        SELECT id, booking_id, booking_date, customer_name, service_name, 
                            customer_contact, status, payment_status, price
                        FROM service_bookings 
                        ORDER BY booking_date DESC
                    ''')
            else:
                if search_term:
                    self.main_app.cursor.execute('''
                        SELECT id, booking_id, booking_date, customer_name, service_name, 
                            customer_contact, status, payment_status, price
                        FROM service_bookings 
                        WHERE status = ? AND (LOWER(customer_name) LIKE ? OR LOWER(booking_id) LIKE ? OR LOWER(service_name) LIKE ?)
                        ORDER BY booking_date DESC
                    ''', (status_filter, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
                else:
                    self.main_app.cursor.execute('''
                        SELECT id, booking_id, booking_date, customer_name, service_name, 
                            customer_contact, status, payment_status, price
                        FROM service_bookings 
                        WHERE status = ?
                        ORDER BY booking_date DESC
                    ''', (status_filter,))
            
            bookings = self.main_app.cursor.fetchall()
            
            for booking in bookings:
                # Format date
                booking_date = booking[2]
                if isinstance(booking_date, str):
                    try:
                        date_obj = datetime.strptime(booking_date.split()[0], '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    except:
                        formatted_date = booking_date[:10]
                else:
                    formatted_date = str(booking_date)[:10]
                
                self.history_tree.insert('', 'end', values=(
                    booking[0],  # id (hidden)
                    booking[1],  # booking_id
                    formatted_date,  # booking_date
                    booking[3],  # customer_name
                    booking[4],  # service_name
                    booking[5] or 'N/A',  # customer_contact
                    booking[6],  # status
                    booking[7],  # payment_status
                    f"₱{booking[8]:.2f}"  # price
                ))
                
        except Exception as e:
            print(f"Error searching service history: {e}")
            messagebox.showerror("Error", f"Failed to search service history: {str(e)}")
    
    def load_services(self):
        """Load all services into the services tree"""
        try:
            # Clear existing items
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)
            
            # Get services based on filter
            category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else 'All Categories'
            
            if category_filter == 'All Categories':
                self.main_app.cursor.execute('''
                    SELECT id, service_id, name, category, price, duration, is_active
                    FROM services 
                    ORDER BY category, name
                ''')
            else:
                self.main_app.cursor.execute('''
                    SELECT id, service_id, name, category, price, duration, is_active
                    FROM services 
                    WHERE category = ?
                    ORDER BY name
                ''', (category_filter,))
            
            services = self.main_app.cursor.fetchall()
            
            for service in services:
                status = 'Active' if service[6] else 'Inactive'
                self.services_tree.insert('', 'end', values=(
                    service[0],  # id (hidden)
                    service[1],  # service_id
                    service[2],  # name
                    service[3],  # category
                    f"₱{service[4]:.2f}",  # price
                    service[5],  # duration
                    status      # status
                ))
                
        except Exception as e:
            print(f"Error loading services: {e}")
            messagebox.showerror("Error", f"Failed to load services: {str(e)}")
    
    def load_service_history(self):
        """Load service booking history"""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Get bookings based on filter
            status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else 'All Status'
            
            if status_filter == 'All Status':
                self.main_app.cursor.execute('''
                    SELECT id, booking_id, booking_date, customer_name, service_name, 
                        customer_contact, status, payment_status, price
                    FROM service_bookings 
                    ORDER BY booking_date DESC
                ''')
            else:
                self.main_app.cursor.execute('''
                    SELECT id, booking_id, booking_date, customer_name, service_name, 
                        customer_contact, status, payment_status, price
                    FROM service_bookings 
                    WHERE status = ?
                    ORDER BY booking_date DESC
                ''', (status_filter,))
            
            bookings = self.main_app.cursor.fetchall()
            
            for booking in bookings:
                # Format date
                booking_date = booking[2]
                if isinstance(booking_date, str):
                    try:
                        date_obj = datetime.strptime(booking_date.split()[0], '%Y-%m-%d')
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    except:
                        formatted_date = booking_date[:10]
                else:
                    formatted_date = str(booking_date)[:10]
                
                self.history_tree.insert('', 'end', values=(
                    booking[0],  # id (hidden)
                    booking[1],  # booking_id
                    formatted_date,  # booking_date
                    booking[3],  # customer_name
                    booking[4],  # service_name
                    booking[5] or 'N/A',  # customer_contact
                    booking[6],  # status
                    booking[7],  # payment_status
                    f"₱{booking[8]:.2f}"  # price
                ))
                
        except Exception as e:
            print(f"Error loading service history: {e}")
            messagebox.showerror("Error", f"Failed to load service history: {str(e)}")
    
    def filter_services(self, event=None):
        """Filter services by category"""
        self.load_services()
    
    def filter_service_history(self, event=None):
        """Filter service history by status"""
        self.load_service_history()
    
    def book_service_from_tree(self, event):
        """Book service from double-click"""
        self.book_selected_service()
    
    def book_selected_service(self):
        """Book the selected service - FIXED VERSION"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service.")
            return
        
        try:
            item = self.services_tree.item(selection[0])
            service_data = item['values']
            
            service_db_id = service_data[0]  # Database ID (hidden)
            service_id = service_data[1]     # Service ID 
            service_name = service_data[2]   # Service name
            price_str = service_data[4]      # Price string with ₱ symbol
            
            # Clean and convert price
            price = float(price_str.replace('₱', '').replace(',', ''))
            
            print(f"Service: ID={service_db_id}, Name={service_name}, Price={price}")
            
            # Open booking dialog with corrected parameters
            self.open_booking_dialog(service_db_id, service_name, price)
            
        except Exception as e:
            print(f"Error in book_selected_service: {e}")
            messagebox.showerror("Error", f"Failed to initiate booking: {str(e)}")
    
    def open_booking_dialog(self, service_id, service_name, price):
        """Open service booking dialog - SIMPLIFIED VERSION with fixed height"""
        try:
            # Create dialog window with smaller height
            dialog = tk.Toplevel()
            dialog.title("Book Service")
            dialog.geometry("480x500")  
            dialog.configure(bg='white')
            dialog.resizable(False, False)
            dialog.minsize(480, 350)  
            dialog.maxsize(480, 800) 
            
            # Make dialog modal
            dialog.transient(self.main_app.root if hasattr(self.main_app, 'root') else None)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
            y = (dialog.winfo_screenheight() // 2) - (500 // 2)  # Changed from 400 to 350
            dialog.geometry(f"480x500+{x}+{y}")
            
            # Main content frame
            content_frame = tk.Frame(dialog, bg='white', padx=30, pady=20)  # Reduced pady
            content_frame.pack(fill='both', expand=True)
            
            # Title
            title_label = tk.Label(content_frame, text=f"Book Service: {service_name}", 
                                font=('Arial', 16, 'bold'), bg='white', fg='#1e293b')
            title_label.pack(pady=(0, 20))  # Reduced bottom padding
            
            # Service details card
            details_card = tk.Frame(content_frame, bg='#f8fafc', relief='solid', bd=1)
            details_card.pack(fill='x', pady=(0, 15))  # Reduced bottom padding
            
            details_header = tk.Frame(details_card, bg='#3b82f6', height=35)
            details_header.pack(fill='x')
            details_header.pack_propagate(False)
            
            tk.Label(details_header, text="📋 Service Details", 
                    font=('Arial', 12, 'bold'), bg='#3b82f6', fg='white').pack(pady=8)
            
            details_content = tk.Frame(details_card, bg='#f8fafc', padx=20, pady=12)  # Reduced padding
            details_content.pack(fill='x')
            
            tk.Label(details_content, text=f"Service: {service_name}", 
                    font=('Arial', 11, 'bold'), bg='#f8fafc', fg='#1e293b').pack(anchor='w', pady=2)
            tk.Label(details_content, text=f"Price: ₱{price:.2f}", 
                    font=('Arial', 11, 'bold'), bg='#f8fafc', fg='#059669').pack(anchor='w', pady=2)
            
            # Customer information card
            customer_card = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
            customer_card.pack(fill='x', pady=(0, 15))  # Reduced bottom padding
            
            customer_header = tk.Frame(customer_card, bg='#10b981', height=35)
            customer_header.pack(fill='x')
            customer_header.pack_propagate(False)
            
            tk.Label(customer_header, text="👤 Customer Information", 
                    font=('Arial', 12, 'bold'), bg='#10b981', fg='white').pack(pady=8)
            
            customer_content = tk.Frame(customer_card, bg='white', padx=20, pady=15)  # Reduced padding
            customer_content.pack(fill='x')
            
            # Customer Name (Required)
            tk.Label(customer_content, text="Customer Name*:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            customer_var = tk.StringVar()
            customer_entry = tk.Entry(customer_content, textvariable=customer_var, 
                                    font=('Arial', 10), relief='solid', bd=1)
            customer_entry.pack(fill='x', pady=(0, 10))  # Reduced bottom padding
            customer_entry.focus_set()
            
            # Contact Number
            tk.Label(customer_content, text="Contact Number:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            contact_var = tk.StringVar()
            contact_entry = tk.Entry(customer_content, textvariable=contact_var, 
                                    font=('Arial', 10), relief='solid', bd=1)
            contact_entry.pack(fill='x', pady=(0, 5))  # Reduced bottom padding
            
            # Action buttons
            button_container = tk.Frame(content_frame, bg='white')
            button_container.pack(fill='x', pady=(15, 0))  # Reduced top padding
            
            def confirm_booking():
                try:
                    # Validate required fields
                    if not customer_var.get().strip():
                        messagebox.showerror("Error", "Customer name is required!")
                        customer_entry.focus_set()
                        return
                    
                    # Generate unique booking ID
                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Insert booking into database
                    self.main_app.cursor.execute('''
                        INSERT INTO service_bookings 
                        (booking_id, service_id, service_name, customer_name, customer_contact, price)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (booking_id, service_id, service_name, customer_var.get().strip(),
                        contact_var.get().strip(), price))
                    
                    self.main_app.conn.commit()
                    
                    # Show success message
                    messagebox.showinfo("Success", 
                                    f"Service booked successfully!\n\n"
                                    f"Booking ID: {booking_id}\n"
                                    f"Customer: {customer_var.get()}\n"
                                    f"Service: {service_name}\n"
                                    f"Price: ₱{price:.2f}")
                    
                    # Close dialog and refresh history
                    dialog.destroy()
                    self.load_service_history()
                    self.load_service_sales_data()  # Refresh sales tab too
                    
                except Exception as e:
                    print(f"Error confirming booking: {e}")
                    messagebox.showerror("Error", f"Failed to book service: {str(e)}")
            
            def cancel_booking():
                dialog.destroy()
            
            # Styled buttons
            cancel_btn = tk.Button(button_container, text="Cancel", command=cancel_booking,
                                bg='#6b7280', fg='white', font=('Arial', 10, 'bold'), 
                                relief='flat', padx=20, pady=8, cursor='hand2')
            cancel_btn.pack(side='right', padx=(8, 0))
            
            confirm_btn = tk.Button(button_container, text="Confirm Booking", command=confirm_booking,
                                bg='#3b82f6', fg='white', font=('Arial', 10, 'bold'), 
                                relief='flat', padx=20, pady=8, cursor='hand2')
            confirm_btn.pack(side='right')
            
            # Bind Enter key to confirm and Escape to cancel
            dialog.bind('<Return>', lambda e: confirm_booking())
            dialog.bind('<Escape>', lambda e: cancel_booking())
            
        except Exception as e:
            print(f"Error creating booking dialog: {e}")
            messagebox.showerror("Error", f"Failed to open booking dialog: {str(e)}")
    
    def add_service(self):
        """Add a new service"""
        dialog = ServiceDialog(self.main_app.root, "Add Service")
        if dialog.result:
            try:
                # Check if service_id already exists
                self.main_app.cursor.execute('SELECT COUNT(*) FROM services WHERE service_id = ?', 
                                           (dialog.result['service_id'],))
                if self.main_app.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Service ID already exists! Please use a unique Service ID.")
                    return
                
                # Insert the service
                self.main_app.cursor.execute('''
                    INSERT INTO services (name, description, price, duration, category, service_id, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (dialog.result['name'], 
                      dialog.result['description'], 
                      dialog.result['price'],
                      dialog.result['duration'], 
                      dialog.result['category'], 
                      dialog.result['service_id'],
                      1))  # Active by default
                
                self.main_app.conn.commit()
                messagebox.showinfo("Success", f"Service '{dialog.result['name']}' added successfully!")
                
                # Refresh services display
                self.load_services()
                
            except sqlite3.IntegrityError as e:
                self.main_app.conn.rollback()
                messagebox.showerror("Error", f"Service ID already exists or constraint violation: {str(e)}")
            except sqlite3.Error as e:
                self.main_app.conn.rollback()
                messagebox.showerror("Error", f"Database error: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def edit_service(self):
        """Edit selected service"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to edit.")
            return
        
        try:
            item = self.services_tree.item(selection[0])
            service_id = item['values'][0]  # Hidden database ID
            
            # Get current service data
            self.main_app.cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
            service = self.main_app.cursor.fetchone()
            
            if not service:
                messagebox.showerror("Error", "Service not found!")
                return
            
            # Open edit dialog with current data
            dialog = ServiceDialog(self.main_app.root, "Edit Service", service)
            if dialog.result:
                try:
                    # Update the service
                    self.main_app.cursor.execute('''
                        UPDATE services SET name = ?, description = ?, price = ?, duration = ?, 
                               category = ?, service_id = ?, is_active = ?
                        WHERE id = ?
                    ''', (dialog.result['name'], dialog.result['description'], dialog.result['price'],
                          dialog.result['duration'], dialog.result['category'], dialog.result['service_id'],
                          dialog.result['is_active'], service_id))
                    
                    self.main_app.conn.commit()
                    self.load_services()
                    messagebox.showinfo("Success", "Service updated successfully!")
                    
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Service ID already exists!")
                    self.main_app.conn.rollback()
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to update service: {str(e)}")
                    self.main_app.conn.rollback()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit service: {str(e)}")
    
    def delete_service(self):
        """Delete selected service"""
        selection = self.services_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a service to delete.")
            return
        
        item = self.services_tree.item(selection[0])
        service_name = item['values'][2]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{service_name}'?"):
            try:
                service_id = item['values'][0]  # Hidden ID
                self.main_app.cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
                self.main_app.conn.commit()
                messagebox.showinfo("Deleted", f"'{service_name}' has been deleted.")
                self.load_services()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete service: {str(e)}")
    
    def update_booking_status(self):
        """Update status and payment status of selected booking with improved UI"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a booking to update.")
            return
        
        item = self.history_tree.item(selection[0])
        booking_id = item['values'][1]
        current_status = item['values'][7]
        current_payment = item['values'][8]
        customer_name = item['values'][3]
        service_name = item['values'][4]
        
        # Create update dialog
        self.open_status_update_dialog(booking_id, current_status, current_payment, customer_name, service_name)
    
    def open_status_update_dialog(self, booking_id, current_status, current_payment, customer_name, service_name):
        """Open enhanced status update dialog with improved readability and scrollable content"""
        try:
            # Create dialog window
            dialog = tk.Toplevel()
            dialog.title("Update Booking Status")
            dialog.geometry("520x650")
            dialog.configure(bg='#f8fafc')
            dialog.resizable(True, True)
            dialog.minsize(480, 600)
            dialog.maxsize(700, 800)
            
            # Make dialog modal
            dialog.transient(self.main_app.root if hasattr(self.main_app, 'root') else None)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (520 // 2)
            y = (dialog.winfo_screenheight() // 2) - (650 // 2)
            dialog.geometry(f"520x650+{x}+{y}")
            
            # Main container with fixed padding
            main_container = tk.Frame(dialog, bg='#f8fafc')
            main_container.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Create canvas for scrolling with fixed width
            canvas = tk.Canvas(main_container, bg='#f8fafc', highlightthickness=0, width=500)
            scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='#f8fafc')
            
            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas_width = event.width
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            canvas.bind('<Configure>', configure_canvas)
            
            # Create window in canvas with proper width control
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Content frame with controlled width
            content = tk.Frame(scrollable_frame, bg='#f8fafc', padx=15, pady=15)
            content.pack(fill='x')
            
            # Title
            title_label = tk.Label(content, text="Update Booking Status", 
                                font=('Arial', 18, 'bold'), bg='#f8fafc', fg='#1e293b')
            title_label.pack(pady=(0, 20))
            
            # Booking info card
            info_card = tk.Frame(content, bg='white', relief='solid', bd=1)
            info_card.pack(fill='x', pady=(0, 20))
            
            info_header = tk.Frame(info_card, bg='#3b82f6', height=35)
            info_header.pack(fill='x')
            info_header.pack_propagate(False)
            
            tk.Label(info_header, text="📋 Booking Information", 
                    font=('Arial', 12, 'bold'), bg='#3b82f6', fg='white').pack(pady=8)
            
            info_content = tk.Frame(info_card, bg='white', padx=20, pady=15)
            info_content.pack(fill='x')
            
            # Booking details with better formatting
            booking_info = [
                ("Booking ID:", booking_id),
                ("Customer:", customer_name),
                ("Service:", service_name)
            ]
            
            for i, (label, value) in enumerate(booking_info):
                label_widget = tk.Label(info_content, text=label, font=('Arial', 10, 'bold'), 
                        bg='white', fg='#374151', anchor='w')
                label_widget.grid(row=i, column=0, sticky='w', pady=4, padx=(0, 15))
                
                value_widget = tk.Label(info_content, text=value, font=('Arial', 10), 
                        bg='white', fg='#1f2937', anchor='w', wraplength=280)
                value_widget.grid(row=i, column=1, sticky='w', pady=4)
            
            # Configure grid weights
            info_content.columnconfigure(0, weight=0, minsize=120)
            info_content.columnconfigure(1, weight=1)
            
            # Status updates card
            status_card = tk.Frame(content, bg='white', relief='solid', bd=1)
            status_card.pack(fill='x', pady=(0, 20))
            
            status_header = tk.Frame(status_card, bg='#10b981', height=35)
            status_header.pack(fill='x')
            status_header.pack_propagate(False)
            
            tk.Label(status_header, text="🔄 Status Updates", 
                    font=('Arial', 12, 'bold'), bg='#10b981', fg='white').pack(pady=8)
            
            status_content = tk.Frame(status_card, bg='white', padx=20, pady=20)
            status_content.pack(fill='x')
            
            # Service Status Section
            service_status_frame = tk.Frame(status_content, bg='white')
            service_status_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(service_status_frame, text="Service Status:", 
                    font=('Arial', 12, 'bold'), bg='white', fg='#1e293b').pack(anchor='w')
            
            # Current status with colored indicator
            current_status_frame = tk.Frame(service_status_frame, bg='white')
            current_status_frame.pack(fill='x', pady=(5, 10))
            
            status_color = {'Pending': '#f59e0b', 'In Progress': '#3b82f6', 'Completed': '#10b981', 'Cancelled': '#ef4444'}
            current_color = status_color.get(current_status, '#6b7280')
            
            tk.Label(current_status_frame, text="●", font=('Arial', 14), 
                    fg=current_color, bg='white').pack(side='left')
            tk.Label(current_status_frame, text=f"Current: {current_status}", 
                    font=('Arial', 10), bg='white', fg='#6b7280').pack(side='left', padx=(5, 0))
            
            # Service status dropdown
            status_var = tk.StringVar(value=current_status)
            
            status_dropdown_frame = tk.Frame(service_status_frame, bg='white')
            status_dropdown_frame.pack(fill='x')
            
            tk.Label(status_dropdown_frame, text="New Status:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            
            status_combo = ttk.Combobox(status_dropdown_frame, textvariable=status_var, 
                                    values=['Pending', 'In Progress', 'Completed', 'Cancelled'],
                                    state='readonly', font=('Arial', 11), width=30)
            status_combo.pack(anchor='w')
            
            # Payment Status Section
            payment_status_frame = tk.Frame(status_content, bg='white')
            payment_status_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(payment_status_frame, text="Payment Status:", 
                    font=('Arial', 12, 'bold'), bg='white', fg='#1e293b').pack(anchor='w')
            
            # Current payment with colored indicator
            current_payment_frame = tk.Frame(payment_status_frame, bg='white')
            current_payment_frame.pack(fill='x', pady=(5, 10))
            
            payment_color = {'Unpaid': '#ef4444', 'Paid': '#10b981', 'Partially Paid': '#f59e0b', 'Refunded': '#6b7280'}
            current_pay_color = payment_color.get(current_payment, '#6b7280')
            
            tk.Label(current_payment_frame, text="●", font=('Arial', 14), 
                    fg=current_pay_color, bg='white').pack(side='left')
            tk.Label(current_payment_frame, text=f"Current: {current_payment}", 
                    font=('Arial', 10), bg='white', fg='#6b7280').pack(side='left', padx=(5, 0))
            
            # Payment status dropdown
            payment_var = tk.StringVar(value=current_payment)
            
            payment_dropdown_frame = tk.Frame(payment_status_frame, bg='white')
            payment_dropdown_frame.pack(fill='x')
            
            tk.Label(payment_dropdown_frame, text="New Payment Status:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            
            payment_combo = ttk.Combobox(payment_dropdown_frame, textvariable=payment_var, 
                                        values=['Unpaid', 'Paid', 'Partially Paid', 'Refunded'],
                                        state='readonly', font=('Arial', 11), width=30)
            payment_combo.pack(anchor='w')
            
            # Notes section
            notes_frame = tk.Frame(status_content, bg='white')
            notes_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(notes_frame, text="Update Notes (Optional):", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            
            notes_text_frame = tk.Frame(notes_frame, bg='white')
            notes_text_frame.pack(fill='x')
            
            notes_text = tk.Text(notes_text_frame, height=4, wrap=tk.WORD, 
                                font=('Arial', 10), relief='solid', bd=1, bg='#f9fafb', width=50)
            notes_scrollbar = tk.Scrollbar(notes_text_frame, orient='vertical', command=notes_text.yview)
            notes_text.configure(yscrollcommand=notes_scrollbar.set)
            
            notes_text.pack(side='left', fill='both', expand=True)
            notes_scrollbar.pack(side='right', fill='y')
            
            # Quick actions card
            quick_card = tk.Frame(content, bg='white', relief='solid', bd=1)
            quick_card.pack(fill='x', pady=(0, 20))
            
            quick_header = tk.Frame(quick_card, bg='#8b5cf6', height=35)
            quick_header.pack(fill='x')
            quick_header.pack_propagate(False)
            
            tk.Label(quick_header, text="⚡ Quick Actions", 
                    font=('Arial', 11, 'bold'), bg='#8b5cf6', fg='white').pack(pady=8)
            
            quick_content = tk.Frame(quick_card, bg='white', padx=20, pady=15)
            quick_content.pack(fill='x')
            
            def set_completed_paid():
                status_var.set('Completed')
                payment_var.set('Paid')
                notes_text.delete('1.0', tk.END)
                notes_text.insert('1.0', "Service completed successfully and payment received.")
            
            def set_cancelled_refund():
                status_var.set('Cancelled')
                payment_var.set('Refunded')
                notes_text.delete('1.0', tk.END)
                notes_text.insert('1.0', "Service cancelled and payment refunded.")
            
            def set_in_progress():
                status_var.set('In Progress')
                notes_text.delete('1.0', tk.END)
                notes_text.insert('1.0', "Service work has started.")
            
            def set_paid_only():
                payment_var.set('Paid')
                notes_text.delete('1.0', tk.END)
                notes_text.insert('1.0', "Payment received.")
            
            btn_grid_frame = tk.Frame(quick_content, bg='white')
            btn_grid_frame.pack()
            
            # Row 1 - Main actions
            complete_btn = tk.Button(btn_grid_frame, text="✅ Complete & Paid", command=set_completed_paid,
                                bg='#10b981', fg='white', font=('Arial', 9, 'bold'), 
                                relief='flat', padx=12, pady=6, cursor='hand2', width=18)
            complete_btn.grid(row=0, column=0, padx=3, pady=3)
            
            progress_btn = tk.Button(btn_grid_frame, text="🔄 In Progress", command=set_in_progress,
                                bg='#3b82f6', fg='white', font=('Arial', 9, 'bold'), 
                                relief='flat', padx=12, pady=6, cursor='hand2', width=18)
            progress_btn.grid(row=0, column=1, padx=3, pady=3)
            
            # Row 2 - Payment actions
            paid_btn = tk.Button(btn_grid_frame, text="💰 Mark Paid", command=set_paid_only,
                            bg='#059669', fg='white', font=('Arial', 9, 'bold'), 
                            relief='flat', padx=12, pady=6, cursor='hand2', width=18)
            paid_btn.grid(row=1, column=0, padx=3, pady=3)
            
            cancel_btn = tk.Button(btn_grid_frame, text="❌ Cancel & Refund", command=set_cancelled_refund,
                                bg='#ef4444', fg='white', font=('Arial', 9, 'bold'), 
                                relief='flat', padx=12, pady=6, cursor='hand2', width=18)
            cancel_btn.grid(row=1, column=1, padx=3, pady=3)

            # Fixed action buttons at bottom
            button_container = tk.Frame(dialog, bg='#f8fafc')
            button_container.pack(fill='x', side='bottom', padx=15, pady=15)
            
            def update_status():
                try:
                    new_status = status_var.get()
                    new_payment = payment_var.get()
                    update_notes = notes_text.get('1.0', tk.END).strip()
                    
                    # Check if anything changed
                    if new_status == current_status and new_payment == current_payment and not update_notes:
                        messagebox.showinfo("No Changes", "No changes were made to the booking.")
                        return
                    
                    # Prepare update data
                    completed_date = None
                    if new_status == 'Completed' and current_status != 'Completed':
                        completed_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    elif new_status != 'Completed' and current_status == 'Completed':
                        completed_date = None
                    
                    # Build update notes
                    status_log = []
                    if new_status != current_status:
                        status_log.append(f"Status: {current_status} → {new_status}")
                    if new_payment != current_payment:
                        status_log.append(f"Payment: {current_payment} → {new_payment}")
                    
                    # Get existing notes
                    self.main_app.cursor.execute('''
                        SELECT notes FROM service_bookings WHERE booking_id = ?
                    ''', (booking_id,))
                    existing_notes = self.main_app.cursor.fetchone()[0] or ""
                    
                    # Combine notes
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
                    new_note_entry = f"\n[{timestamp}] " + " | ".join(status_log)
                    if update_notes:
                        new_note_entry += f" - {update_notes}"
                    
                    final_notes = existing_notes + new_note_entry
                    
                    # Update database
                    update_query = '''
                        UPDATE service_bookings 
                        SET status = ?, payment_status = ?, notes = ?
                    '''
                    update_params = [new_status, new_payment, final_notes]
                    
                    if completed_date is not None:
                        update_query += ', completed_date = ?'
                        update_params.append(completed_date)
                    
                    update_query += ' WHERE booking_id = ?'
                    update_params.append(booking_id)
                    
                    self.main_app.cursor.execute(update_query, update_params)
                    self.main_app.conn.commit()
                    
                    # Show success message
                    changes = []
                    if new_status != current_status:
                        changes.append(f"✅ Status: {new_status}")
                    if new_payment != current_payment:
                        changes.append(f"💰 Payment: {new_payment}")
                    
                    success_msg = f"Booking {booking_id} updated successfully!\n\n" + "\n".join(changes)
                    if completed_date:
                        success_msg += f"\n🎉 Completed: {completed_date}"
                    
                    messagebox.showinfo("Update Successful", success_msg)
                    
                    # Close dialog and refresh
                    dialog.destroy()
                    self.load_service_history()
                    self.load_service_sales_data()  # Refresh sales tab too
                    
                except Exception as e:
                    print(f"Error updating booking status: {e}")
                    messagebox.showerror("Error", f"Failed to update booking: {str(e)}")
            
            def cancel_update():
                dialog.destroy()
            
            # Styled action buttons
            cancel_action_btn = tk.Button(button_container, text="Cancel", command=cancel_update,
                                        bg='#6b7280', fg='white', font=('Arial', 11, 'bold'), 
                                        relief='flat', padx=25, pady=10, cursor='hand2')
            cancel_action_btn.pack(side='right', padx=(10, 0))
            
            update_action_btn = tk.Button(button_container, text="Update Booking", command=update_status,
                                        bg='#1e293b', fg='white', font=('Arial', 11, 'bold'), 
                                        relief='flat', padx=25, pady=10, cursor='hand2')
            update_action_btn.pack(side='right')
            
            # Enable mouse wheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            def bind_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            def unbind_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            
            # Bind mouse wheel events
            canvas.bind('<Enter>', bind_mousewheel)
            canvas.bind('<Leave>', unbind_mousewheel)
            
            # Bind keyboard shortcuts
            dialog.bind('<Return>', lambda e: update_status())
            dialog.bind('<Escape>', lambda e: cancel_update())
            
            # Focus on status combo
            status_combo.focus_set()
            
            dialog.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        except Exception as e:
            print(f"Error creating status update dialog: {e}")
            messagebox.showerror("Error", f"Failed to open status update dialog: {str(e)}")
    
    def view_booking_details(self):
        """View detailed information about selected booking - FIXED VERSION"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a booking to view details.")
            return
        
        item = self.history_tree.item(selection[0])
        booking_id = item['values'][1]  # Get booking_id from the tree
        
        try:
            # Fixed SQL query with correct column order
            self.main_app.cursor.execute('''
                SELECT id, booking_id, service_id, service_name, customer_name, customer_contact,
                    bike_details, booking_date, scheduled_date, scheduled_time, status, 
                    notes, payment_status, price, completed_date
                FROM service_bookings 
                WHERE booking_id = ?
            ''', (booking_id,))
            
            booking = self.main_app.cursor.fetchone()
            
            if booking:
                # Format the booking date properly
                booking_date = booking[7]  # booking_date
                if isinstance(booking_date, str):
                    try:
                        # Try to parse and format the date
                        if ' ' in booking_date:
                            date_part = booking_date.split()[0]
                        else:
                            date_part = booking_date
                        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                        formatted_booking_date = date_obj.strftime('%B %d, %Y')
                    except:
                        formatted_booking_date = str(booking_date)
                else:
                    formatted_booking_date = str(booking_date)
                
                # Format completed date if available
                completed_date = booking[14]  
                if completed_date:
                    try:
                        if isinstance(completed_date, str):
                            completed_obj = datetime.strptime(completed_date.split()[0], '%Y-%m-%d')
                            formatted_completed = completed_obj.strftime('%B %d, %Y')
                        else:
                            formatted_completed = str(completed_date)
                    except:
                        formatted_completed = str(completed_date)
                else:
                    formatted_completed = 'Not completed'
                
                # Format scheduled date and time
                scheduled_date = booking[8] if booking[8] else 'Not scheduled'
                scheduled_time = booking[9] if booking[9] else 'Not specified'
                if scheduled_date != 'Not scheduled':
                    try:
                        sched_obj = datetime.strptime(scheduled_date, '%Y-%m-%d')
                        scheduled_date = sched_obj.strftime('%B %d, %Y')
                    except:
                        pass  
                
                # Create detailed information dialog
                detail_dialog = tk.Toplevel()
                detail_dialog.title(f"Booking Details - {booking_id}")
                detail_dialog.geometry("520x650")
                detail_dialog.configure(bg='#f8fafc')
                detail_dialog.resizable(True, True)
                detail_dialog.minsize(480, 600)
                detail_dialog.maxsize(700, 800)
                
                # Make dialog modal
                detail_dialog.transient(self.main_app.root if hasattr(self.main_app, 'root') else None)
                detail_dialog.grab_set()
                
                # Center the dialog
                detail_dialog.update_idletasks()
                x = (detail_dialog.winfo_screenwidth() // 2) - (520 // 2)
                y = (detail_dialog.winfo_screenheight() // 2) - (650 // 2)
                detail_dialog.geometry(f"520x650+{x}+{y}")
                
                # Main container with fixed padding
                main_container = tk.Frame(detail_dialog, bg='#f8fafc')
                main_container.pack(fill='both', expand=True, padx=5, pady=5)
                
                # Create canvas for scrolling with fixed width
                canvas = tk.Canvas(main_container, bg='#f8fafc', highlightthickness=0, width=500)
                scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg='#f8fafc')
                
                def configure_canvas(event):
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    canvas_width = event.width
                    canvas.itemconfig(canvas_window, width=canvas_width)
                
                canvas.bind('<Configure>', configure_canvas)
                
                # Create window in canvas with proper width control
                canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                # Pack canvas and scrollbar
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Content frame with controlled width
                content = tk.Frame(scrollable_frame, bg='#f8fafc', padx=15, pady=15)
                content.pack(fill='x')
                
                # Title
                title_label = tk.Label(content, text=f"Booking Details", 
                                    font=('Arial', 18, 'bold'), bg='#f8fafc', fg='#1e293b')
                title_label.pack(pady=(0, 20))
                
                # Booking ID card
                id_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                id_card.pack(fill='x', pady=(0, 15))
                
                id_header = tk.Frame(id_card, bg='#3b82f6', height=35)
                id_header.pack(fill='x')
                id_header.pack_propagate(False)
                
                tk.Label(id_header, text=f"📋 {booking[1]}", font=('Arial', 12, 'bold'), 
                        bg='#3b82f6', fg='white').pack(pady=8)
                
                # Customer Information
                customer_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                customer_card.pack(fill='x', pady=(0, 15))
                
                customer_header = tk.Frame(customer_card, bg='#10b981', height=35)
                customer_header.pack(fill='x')
                customer_header.pack_propagate(False)
                
                tk.Label(customer_header, text="👤 Customer Information", 
                        font=('Arial', 12, 'bold'), bg='#10b981', fg='white').pack(pady=8)
                
                customer_content = tk.Frame(customer_card, bg='white', padx=20, pady=15)
                customer_content.pack(fill='x')
                
                # Customer details
                details_grid = [
                    ("Customer Name:", booking[4]),  # customer_name
                    ("Contact Number:", booking[5] or 'Not provided'),  # customer_contact
                ]
                
                for i, (label, value) in enumerate(details_grid):
                    tk.Label(customer_content, text=label, font=('Arial', 10, 'bold'), 
                            bg='white', fg='#374151').grid(row=i, column=0, sticky='w', pady=5, padx=(0, 10))
                    tk.Label(customer_content, text=str(value), font=('Arial', 10), 
                            bg='white', fg='#1f2937', wraplength=300).grid(row=i, column=1, sticky='w', pady=5)
                
                # Service Information
                service_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                service_card.pack(fill='x', pady=(0, 15))
                
                service_header = tk.Frame(service_card, bg='#8b5cf6', height=35)
                service_header.pack(fill='x')
                service_header.pack_propagate(False)
                
                tk.Label(service_header, text="🔧 Service Information", 
                        font=('Arial', 12, 'bold'), bg='#8b5cf6', fg='white').pack(pady=8)
                
                service_content = tk.Frame(service_card, bg='white', padx=20, pady=15)
                service_content.pack(fill='x')
                
                service_details = [
                    ("Service ID:", booking[2]),  # service_id
                    ("Service Name:", booking[3]),  # service_name
                    ("Price:", f"₱{booking[13]:.2f}"),  # price
                ]
                
                for i, (label, value) in enumerate(service_details):
                    label_widget = tk.Label(service_content, text=label, font=('Arial', 10, 'bold'), 
                            bg='white', fg='#374151', anchor='w')
                    label_widget.grid(row=i, column=0, sticky='w', pady=4, padx=(0, 15))
                    
                    value_widget = tk.Label(service_content, text=str(value), font=('Arial', 10), 
                            bg='white', fg='#1f2937', anchor='w')
                    value_widget.grid(row=i, column=1, sticky='w', pady=4)
                
                # Configure grid weights
                service_content.columnconfigure(0, weight=0, minsize=130)
                service_content.columnconfigure(1, weight=1)
                
                # Scheduling Information
                schedule_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                schedule_card.pack(fill='x', pady=(0, 15))
                
                schedule_header = tk.Frame(schedule_card, bg='#f59e0b', height=35)
                schedule_header.pack(fill='x')
                schedule_header.pack_propagate(False)
                
                tk.Label(schedule_header, text="📅 Scheduling Information", 
                        font=('Arial', 12, 'bold'), bg='#f59e0b', fg='white').pack(pady=8)
                
                schedule_content = tk.Frame(schedule_card, bg='white', padx=20, pady=15)
                schedule_content.pack(fill='x')
                
                schedule_info = [
                    ("Booking Date:", formatted_booking_date),
                    ("Scheduled Date:", scheduled_date),
                    ("Scheduled Time:", scheduled_time),
                    ("Completed Date:", formatted_completed),
                ]
                
                for i, (label, value) in enumerate(schedule_info):
                    label_widget = tk.Label(schedule_content, text=label, font=('Arial', 10, 'bold'), 
                            bg='white', fg='#374151', anchor='w')
                    label_widget.grid(row=i, column=0, sticky='w', pady=4, padx=(0, 15))
                    
                    value_widget = tk.Label(schedule_content, text=str(value), font=('Arial', 10), 
                            bg='white', fg='#1f2937', anchor='w')
                    value_widget.grid(row=i, column=1, sticky='w', pady=4)
                
                # Configure grid weights
                schedule_content.columnconfigure(0, weight=0, minsize=130)
                schedule_content.columnconfigure(1, weight=1)
                
                # Status Information
                status_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                status_card.pack(fill='x', pady=(0, 15))
                
                status_header = tk.Frame(status_card, bg='#ef4444', height=35)
                status_header.pack(fill='x')
                status_header.pack_propagate(False)
                
                tk.Label(status_header, text="📊 Status Information", 
                        font=('Arial', 12, 'bold'), bg='#ef4444', fg='white').pack(pady=8)
                
                status_content = tk.Frame(status_card, bg='white', padx=20, pady=15)
                status_content.pack(fill='x')
                
                # Status with colored indicators
                status_frame = tk.Frame(status_content, bg='white')
                status_frame.pack(fill='x', pady=5)
                
                tk.Label(status_frame, text="Service Status:", font=('Arial', 10, 'bold'), 
                        bg='white', fg='#374151').pack(side='left')
                
                # Status color coding
                status_colors = {
                    'Pending': '#f59e0b',
                    'In Progress': '#3b82f6', 
                    'Completed': '#10b981',
                    'Cancelled': '#ef4444'
                }
                status_color = status_colors.get(booking[10], '#6b7280')  
                
                tk.Label(status_frame, text="●", font=('Arial', 14), 
                        fg=status_color, bg='white').pack(side='left', padx=(10, 5))
                tk.Label(status_frame, text=booking[10], font=('Arial', 10, 'bold'), 
                        fg=status_color, bg='white').pack(side='left')
                
                # Payment status
                payment_frame = tk.Frame(status_content, bg='white')
                payment_frame.pack(fill='x', pady=5)
                
                tk.Label(payment_frame, text="Payment Status:", font=('Arial', 10, 'bold'), 
                        bg='white', fg='#374151').pack(side='left')
                
                payment_colors = {
                    'Unpaid': '#ef4444',
                    'Paid': '#10b981', 
                    'Partially Paid': '#f59e0b',
                    'Refunded': '#6b7280'
                }
                payment_color = payment_colors.get(booking[12], '#6b7280')  
                
                tk.Label(payment_frame, text="●", font=('Arial', 14), 
                        fg=payment_color, bg='white').pack(side='left', padx=(10, 5))
                tk.Label(payment_frame, text=booking[12], font=('Arial', 10, 'bold'), 
                        fg=payment_color, bg='white').pack(side='left')
                
                # Notes section (if available)
                if booking[11]:  # notes
                    notes_card = tk.Frame(content, bg='white', relief='solid', bd=1)
                    notes_card.pack(fill='x', pady=(0, 15))
                    
                    notes_header = tk.Frame(notes_card, bg='#6b7280', height=35)
                    notes_header.pack(fill='x')
                    notes_header.pack_propagate(False)
                    
                    tk.Label(notes_header, text="📝 Notes & Updates", 
                            font=('Arial', 12, 'bold'), bg='#6b7280', fg='white').pack(pady=8)
                    
                    notes_content = tk.Frame(notes_card, bg='white', padx=20, pady=15)
                    notes_content.pack(fill='x')
                    
                    # Notes text with proper sizing
                    notes_text_frame = tk.Frame(notes_content, bg='white')
                    notes_text_frame.pack(fill='x', pady=(0, 5))
                    
                    notes_text = tk.Text(notes_text_frame, height=5, wrap=tk.WORD, 
                                    font=('Arial', 9), relief='solid', bd=1, bg='#f9fafb', 
                                    state='normal', width=50)
                    notes_text_scroll = tk.Scrollbar(notes_text_frame, orient='vertical', command=notes_text.yview)
                    notes_text.configure(yscrollcommand=notes_text_scroll.set)
                    
                    notes_text.insert('1.0', booking[11])
                    notes_text.configure(state='disabled')  # Make read-only
                    
                    notes_text.pack(side='left', fill='both', expand=True)
                    notes_text_scroll.pack(side='right', fill='y')
                
                # Close button
                button_frame = tk.Frame(content, bg='#f8fafc')
                button_frame.pack(fill='x', pady=20)
                
                close_btn = tk.Button(button_frame, text="Close", 
                                    command=detail_dialog.destroy,
                                    bg='#6b7280', fg='white', font=('Arial', 11, 'bold'), 
                                    relief='flat', padx=30, pady=10, cursor='hand2')
                close_btn.pack()
                
                # Enable mouse wheel scrolling
                def _on_mousewheel(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
                def bind_mousewheel(event):
                    canvas.bind_all("<MouseWheel>", _on_mousewheel)
                
                def unbind_mousewheel(event):
                    canvas.unbind_all("<MouseWheel>")
                
                canvas.bind('<Enter>', bind_mousewheel)
                canvas.bind('<Leave>', unbind_mousewheel)
                
                # Update scroll region
                detail_dialog.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Bind escape key to close
                detail_dialog.bind('<Escape>', lambda e: detail_dialog.destroy())
                
            else:
                messagebox.showerror("Error", "Booking not found!")
                
        except Exception as e:
            print(f"Error in view_booking_details: {e}")
            messagebox.showerror("Error", f"Failed to load booking details: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def refresh_services(self):
        """Refresh services list"""
        self.load_services()
    
    def delete_service_history(self):
        """Delete selected service history record"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return
        
        try:
            item = self.history_tree.item(selection[0])
            booking_id = item['values'][1]  
            customer_name = item['values'][3]  
            service_name = item['values'][4]  
            
            # Show confirmation dialog with details
            if messagebox.askyesno("Confirm Delete", 
                                f"Are you sure you want to delete this service record?\n\n" + 
                                f"Booking ID: {booking_id}\n" +
                                f"Customer: {customer_name}\n" +
                                f"Service: {service_name}"):
                
                # Delete the record
                self.main_app.cursor.execute('''
                    DELETE FROM service_bookings 
                    WHERE booking_id = ?
                ''', (booking_id,))
                
                self.main_app.conn.commit()
                messagebox.showinfo("Success", "Service record has been deleted successfully!")
                
                # Refresh the history view
                self.load_service_history()
                self.load_service_sales_data()  # Refresh sales tab too
                
        except Exception as e:
            print(f"Error deleting service record: {e}")
            messagebox.showerror("Error", f"Failed to delete service record: {str(e)}")
            self.main_app.conn.rollback()

    def refresh_service_history(self):
        """Refresh service history"""
        self.load_service_history()
    
    def get_service_statistics(self):
        """Get service statistics for dashboard integration"""
        try:
            stats = {}
            
            # Total services offered
            self.main_app.cursor.execute('SELECT COUNT(*) FROM services WHERE is_active = 1')
            stats['total_services'] = self.main_app.cursor.fetchone()[0]
            
            # Total bookings
            self.main_app.cursor.execute('SELECT COUNT(*) FROM service_bookings')
            stats['total_bookings'] = self.main_app.cursor.fetchone()[0]
            
            # Pending bookings
            self.main_app.cursor.execute("SELECT COUNT(*) FROM service_bookings WHERE status = 'Pending'")
            stats['pending_bookings'] = self.main_app.cursor.fetchone()[0]
            
            # Completed bookings this month
            self.main_app.cursor.execute('''
                SELECT COUNT(*) FROM service_bookings 
                WHERE status = 'Completed' 
                AND strftime('%Y-%m', booking_date) = strftime('%Y-%m', 'now')
            ''')
            stats['completed_this_month'] = self.main_app.cursor.fetchone()[0]
            
            # Revenue from services this month
            self.main_app.cursor.execute('''
                SELECT SUM(price) FROM service_bookings 
                WHERE status = 'Completed' 
                AND strftime('%Y-%m', booking_date) = strftime('%Y-%m', 'now')
            ''')
            result = self.main_app.cursor.fetchone()[0]
            stats['revenue_this_month'] = result if result else 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting service statistics: {e}")
            return {
                'total_services': 0,
                'total_bookings': 0,
                'pending_bookings': 0,
                'completed_this_month': 0,
                'revenue_this_month': 0
            }
    
    def get_popular_services(self, limit=5):
        """Get most popular services by booking count"""
        try:
            self.main_app.cursor.execute('''
                SELECT service_name, COUNT(*) as booking_count
                FROM service_bookings 
                GROUP BY service_name
                ORDER BY booking_count DESC
                LIMIT ?
            ''', (limit,))
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting popular services: {e}")
            return []
    
    def get_upcoming_appointments(self, days=7):
        """Get upcoming service appointments"""
        try:
            from datetime import datetime, timedelta
            end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            self.main_app.cursor.execute('''
                SELECT booking_id, customer_name, service_name, scheduled_date, scheduled_time
                FROM service_bookings 
                WHERE status IN ('Pending', 'In Progress')
                AND scheduled_date BETWEEN date('now') AND ?
                ORDER BY scheduled_date, scheduled_time
            ''', (end_date,))
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error getting upcoming appointments: {e}")
            return []
    
    def mark_booking_paid(self, booking_id):
        """Mark a booking as paid"""
        try:
            self.main_app.cursor.execute('''
                UPDATE service_bookings 
                SET payment_status = 'Paid'
                WHERE booking_id = ?
            ''', (booking_id,))
            self.main_app.conn.commit()
            return True
        except Exception as e:
            print(f"Error marking booking as paid: {e}")
            return False
    
    def cancel_booking(self, booking_id, reason=""):
        """Cancel a service booking"""
        try:
            self.main_app.cursor.execute('''
                UPDATE service_bookings 
                SET status = 'Cancelled', notes = COALESCE(notes, '') || ' | Cancelled: ' || ?
                WHERE booking_id = ?
            ''', (reason, booking_id))
            self.main_app.conn.commit()
            return True
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            return False
    
    def search_bookings(self, search_term):
        """Search bookings by customer name, booking ID, or service name"""
        try:
            search_pattern = f"%{search_term}%"
            self.main_app.cursor.execute('''
                SELECT id, booking_id, booking_date, customer_name, service_name, 
                       customer_contact, scheduled_date, status, payment_status, price
                FROM service_bookings 
                WHERE customer_name LIKE ? 
                   OR booking_id LIKE ? 
                   OR service_name LIKE ?
                ORDER BY booking_date DESC
            ''', (search_pattern, search_pattern, search_pattern))
            return self.main_app.cursor.fetchall()
        except Exception as e:
            print(f"Error searching bookings: {e}")
            return []
    
    def export_service_data(self, start_date=None, end_date=None):
        """Export service data for reporting (placeholder for future enhancement)"""
        try:
            query = '''
                SELECT booking_id, booking_date, customer_name, service_name, 
                       scheduled_date, status, payment_status, price
                FROM service_bookings 
            '''
            params = []
            
            if start_date and end_date:
                query += ' WHERE booking_date BETWEEN ? AND ?'
                params = [start_date, end_date]
            
            query += ' ORDER BY booking_date DESC'
            
            self.main_app.cursor.execute(query, params)
            return self.main_app.cursor.fetchall()
            
        except Exception as e:
            print(f"Error exporting service data: {e}")
            return []
    
    def refresh(self):
        """Refresh the services interface"""
        if self.frame:
            self.load_services()
            self.load_service_history()
            self.load_service_sales_data()  
            return self.frame
        return None