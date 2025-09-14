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
            
        except Exception as e:
            print(f"Error creating notebook: {e}")
            # Fall back to simple frame if notebook fails
            self.create_services_tab(self.frame)
        
        return self.frame
    
    def create_services_tab(self, parent):
        """Create the services management tab"""
        # Services controls
        controls_frame = ttk.Frame(parent, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(controls_frame, text="Add", command=self.add_service,
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit", command=self.edit_service,
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete", command=self.delete_service,
                  style='Danger.TButton').pack(side='left', padx=(0, 10))
        
        
        # Filter frame
        filter_frame = ttk.Frame(parent, style='Content.TFrame')
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter by Category:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.category_filter_var = tk.StringVar(value='All Categories')
        category_filter = ttk.Combobox(filter_frame, textvariable=self.category_filter_var,
                                     values=['All Categories', 'Cleaning', 'Assembly', 'Suspension', 
                                           'Drivetrain', 'Wheels', 'Brakes'],
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
        
        # Configure columns
        column_widths = {
            'ID': 50,
            'Service ID': 80,
            'Name': 200,
            'Category': 100,
            'Price': 100,
            'Duration': 120,
            'Status': 80
        }
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=column_widths.get(col, 100))
        
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
        
        ttk.Button(action_frame, text="📅Select Service", 
                  command=self.book_selected_service,
                  style='Success.TButton').pack(side='left', padx=(0, 10))
        
        # Load services
        self.load_services()
    
    def create_service_history_tab(self, parent):
        """Create the service history tab"""
        # History controls
        history_controls = ttk.Frame(parent, style='Content.TFrame')
        history_controls.pack(fill='x', padx=20, pady=10)
        
        # Filter controls
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
        #ttk.Button(history_controls, text="Refresh", command=self.refresh_service_history,
        #          style='Secondary.TButton').pack(side='right')
        
        # Service history table
        history_table_frame = ttk.Frame(parent, style='Content.TFrame')
        history_table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for service history
        history_columns = ('ID', 'Service ID', 'Date', 'Customer', 'Service', 'Contact', 
                          'Scheduled', 'Status', 'Payment', 'Price')
        self.history_tree = ttk.Treeview(history_table_frame, columns=history_columns, 
                                        show='headings', style='Modern.Treeview')
        
        # Configure history columns
        history_widths = {
            'ID': 50,
            'Service ID': 100,
            'Date': 100,
            'Customer': 120,
            'Service': 150,
            'Contact': 100,
            'Scheduled': 120,
            'Status': 80,
            'Payment': 80,
            'Price': 100
        }
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=history_widths.get(col, 100))
        
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
                           customer_contact, scheduled_date, status, payment_status, price
                    FROM service_bookings 
                    ORDER BY booking_date DESC
                ''')
            else:
                self.main_app.cursor.execute('''
                    SELECT id, booking_id, booking_date, customer_name, service_name, 
                           customer_contact, scheduled_date, status, payment_status, price
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
                
                scheduled = booking[6] if booking[6] else 'TBD'
                
                self.history_tree.insert('', 'end', values=(
                    booking[0],  # id (hidden)
                    booking[1],  # booking_id
                    formatted_date,  # booking_date
                    booking[3],  # customer_name
                    booking[4],  # service_name
                    booking[5] or 'N/A',  # customer_contact
                    scheduled,   # scheduled_date
                    booking[7],  # status
                    booking[8],  # payment_status
                    f"₱{booking[9]:.2f}"  # price
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
            messagebox.showwarning("Warning", "Please select a service to book.")
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
            
            print(f"Booking service: ID={service_db_id}, Name={service_name}, Price={price}")
            
            # Open booking dialog with corrected parameters
            self.open_booking_dialog(service_db_id, service_name, price)
            
        except Exception as e:
            print(f"Error in book_selected_service: {e}")
            messagebox.showerror("Error", f"Failed to initiate booking: {str(e)}")
    
    def open_booking_dialog(self, service_id, service_name, price):
        """Open service booking dialog with scrollable interface - FIXED VERSION"""
        try:
            # Create dialog window
            dialog = tk.Toplevel()
            dialog.title("Book Service")
            dialog.geometry("480x650")
            dialog.configure(bg='white')
            dialog.resizable(False, False)
            dialog.minsize(480, 650)
            dialog.maxsize(480, 650)
            
            # Make dialog modal
            dialog.transient(self.main_app.root if hasattr(self.main_app, 'root') else None)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (480 // 2)
            y = (dialog.winfo_screenheight() // 2) - (650 // 2)
            dialog.geometry(f"480x650+{x}+{y}")
            
            # Create main container
            main_container = tk.Frame(dialog, bg='white')
            main_container.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Create canvas and scrollbar for scrollable content
            canvas = tk.Canvas(main_container, bg='white', highlightthickness=0, width=460)
            scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            # Configure canvas width
            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                # Ensure the scrollable_frame fills the canvas width
                canvas_width = event.width
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            canvas.bind('<Configure>', configure_canvas)
            
            # Create window in canvas
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Content frame with controlled width
            content_frame = tk.Frame(scrollable_frame, bg='white', padx=15, pady=15)
            content_frame.pack(fill='x')
            
            # Title
            title_label = tk.Label(content_frame, text=f"Services: {service_name}", 
                                font=('Arial', 16, 'bold'), bg='white', fg='#1e293b')
            title_label.pack(pady=(0, 25))
            
            # Service details card
            details_card = tk.Frame(content_frame, bg='#f8fafc', relief='solid', bd=1)
            details_card.pack(fill='x', pady=(0, 20))
            
            details_header = tk.Frame(details_card, bg='#3b82f6', height=35)
            details_header.pack(fill='x')
            details_header.pack_propagate(False)
            
            tk.Label(details_header, text="📋 Service Details", 
                    font=('Arial', 12, 'bold'), bg='#3b82f6', fg='white').pack(pady=8)
            
            details_content = tk.Frame(details_card, bg='#f8fafc', padx=20, pady=15)
            details_content.pack(fill='x')
            
            tk.Label(details_content, text=f"Service: {service_name}", 
                    font=('Arial', 11, 'bold'), bg='#f8fafc', fg='#1e293b').pack(anchor='w', pady=2)
            tk.Label(details_content, text=f"Price: ₱{price:.2f}", 
                    font=('Arial', 11, 'bold'), bg='#f8fafc', fg='#059669').pack(anchor='w', pady=2)
            
            # Customer information card
            customer_card = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
            customer_card.pack(fill='x', pady=(0, 20))
            
            customer_header = tk.Frame(customer_card, bg='#10b981', height=35)
            customer_header.pack(fill='x')
            customer_header.pack_propagate(False)
            
            tk.Label(customer_header, text="👤 Customer Information", 
                    font=('Arial', 12, 'bold'), bg='#10b981', fg='white').pack(pady=8)
            
            customer_content = tk.Frame(customer_card, bg='white', padx=20, pady=20)
            customer_content.pack(fill='x')
            
            # Customer Name (Required)
            tk.Label(customer_content, text="Customer Name*:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            customer_var = tk.StringVar()
            customer_entry = tk.Entry(customer_content, textvariable=customer_var, 
                                    font=('Arial', 10), relief='solid', bd=1)
            customer_entry.pack(fill='x', pady=(0, 12))
            customer_entry.focus_set()  # Set focus to first field
            
            # Contact Number
            tk.Label(customer_content, text="Contact Number:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            contact_var = tk.StringVar()
            contact_entry = tk.Entry(customer_content, textvariable=contact_var, 
                                    font=('Arial', 10), relief='solid', bd=1)
            contact_entry.pack(fill='x', pady=(0, 12))
            
            # Bike Details
            tk.Label(customer_content, text="Bike Details:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            bike_var = tk.StringVar()
            bike_entry = tk.Entry(customer_content, textvariable=bike_var, 
                                font=('Arial', 10), relief='solid', bd=1)
            bike_entry.pack(fill='x', pady=(0, 8))
            
            # Scheduling card
            schedule_card = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
            schedule_card.pack(fill='x', pady=(0, 20))
            
            schedule_header = tk.Frame(schedule_card, bg='#8b5cf6', height=35)
            schedule_header.pack(fill='x')
            schedule_header.pack_propagate(False)
            
            tk.Label(schedule_header, text="📅 Scheduling", 
                    font=('Arial', 12, 'bold'), bg='#8b5cf6', fg='white').pack(pady=8)
            
            schedule_content = tk.Frame(schedule_card, bg='white', padx=20, pady=20)
            schedule_content.pack(fill='x')
            
            # Preferred Date
            tk.Label(schedule_content, text="Preferred Date (YYYY-MM-DD):", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            date_entry = tk.Entry(schedule_content, textvariable=date_var, 
                                font=('Arial', 10), relief='solid', bd=1)
            date_entry.pack(fill='x', pady=(0, 12))
            
            # Preferred Time
            tk.Label(schedule_content, text="Preferred Time:", 
                    font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            time_var = tk.StringVar(value='09:00 AM')
            time_combo = ttk.Combobox(schedule_content, textvariable=time_var, 
                                    font=('Arial', 10),
                                    values=['09:00 AM', '10:00 AM', '11:00 AM', '01:00 PM', 
                                            '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'],
                                    state='readonly')
            time_combo.pack(fill='x', pady=(0, 12))
            
            # Notes
            #tk.Label(schedule_content, text="Additional Notes:", 
                    #font=('Arial', 10, 'bold'), bg='white', fg='#374151').pack(anchor='w', pady=(0, 5))
            
            notes_frame = tk.Frame(schedule_content, bg='white')
            notes_frame.pack(fill='x', pady=(0, 8))
            
            notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD, 
                                font=('Arial', 9), relief='solid', bd=1, bg='#f9fafb')
            notes_scrollbar = tk.Scrollbar(notes_frame, orient='vertical', command=notes_text.yview)
            notes_text.configure(yscrollcommand=notes_scrollbar.set)
            
            notes_text.pack(side='left', fill='both', expand=True)
            notes_scrollbar.pack(side='right', fill='y')
            
            # Action buttons - Fixed at bottom
            button_container = tk.Frame(dialog, bg='white')
            button_container.pack(fill='x', side='bottom', padx=15, pady=15)
            
            def confirm_booking():
                try:
                    # Validate required fields
                    if not customer_var.get().strip():
                        messagebox.showerror("Error", "Customer name is required!")
                        customer_entry.focus_set()
                        return
                    
                    # Generate unique booking ID
                    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Get notes text
                    notes = notes_text.get('1.0', tk.END).strip()
                    
                    # Insert booking into database
                    self.main_app.cursor.execute('''
                        INSERT INTO service_bookings 
                        (booking_id, service_id, service_name, customer_name, customer_contact,
                        bike_details, scheduled_date, scheduled_time, notes, price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (booking_id, service_id, service_name, customer_var.get().strip(),
                        contact_var.get().strip(), bike_var.get().strip(), 
                        date_var.get(), time_var.get(), notes, price))
                    
                    self.main_app.conn.commit()
                    
                    # Show success message
                    messagebox.showinfo("Success", 
                                    f"Service booked successfully!\n\n"
                                    f"Booking ID: {booking_id}\n"
                                    f"Customer: {customer_var.get()}\n"
                                    f"Service: {service_name}\n"
                                    f"Scheduled: {date_var.get()} at {time_var.get()}\n"
                                    f"Price: ₱{price:.2f}")
                    
                    # Close dialog and refresh history
                    dialog.destroy()
                    self.load_service_history()
                    
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
            
            confirm_btn = tk.Button(button_container, text="Confirm", command=confirm_booking,
                                bg='#3b82f6', fg='white', font=('Arial', 10, 'bold'), 
                                relief='flat', padx=20, pady=8, cursor='hand2')
            confirm_btn.pack(side='right')
            
            # Bind Enter key to confirm and Escape to cancel
            dialog.bind('<Return>', lambda e: confirm_booking())
            dialog.bind('<Escape>', lambda e: cancel_booking())
            
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
            
            # Update scroll region after everything is packed
            dialog.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
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
                    ("Bike Details:", booking[6] or 'Not specified'),  # bike_details
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
            return self.frame
        return None