import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class StockHistoryModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the stock history interface - Shows only sales transactions"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Stock History", style='PageTitle.TLabel').pack(side='left')
        
        # Controls and filters
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        # Top row - Search box
        search_frame = ttk.Frame(controls_frame, style='Content.TFrame')
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, style='Modern.TEntry')
        search_entry.pack(side='left', padx=(0, 10))
        
        # Clear search button
        ttk.Button(search_frame, text="Clear", command=self.clear_search, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        
        # Search hint label
        ttk.Label(search_frame, text="(Search by product, customer, or transaction ID)", 
                 style='Hint.TLabel').pack(side='left', padx=(10, 0))
        
        # Bottom row - Left side - Filters
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
        self.movement_type_var = tk.StringVar(value='All Sales')
        movement_filter = ttk.Combobox(filters_frame, textvariable=self.movement_type_var,
                                     values=['All Sales', 'Regular Sales', 'Returns'],
                                     state='readonly', style='Modern.TCombobox', width=15)
        movement_filter.pack(side='left', padx=(0, 15))
        movement_filter.bind('<<ComboboxSelected>>', self.filter_stock_history)
        
        # Right side - Action buttons
        buttons_frame = ttk.Frame(controls_frame, style='Content.TFrame')
        buttons_frame.pack(side='right')
        
        # Delete button
        ttk.Button(buttons_frame, text="Delete Selected", command=self.delete_stock_history,
                  style='Danger.TButton').pack(side='right', padx=(0, 10))
        
        # Stock history table
        table_frame = ttk.Frame(self.frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview for stock history 
        columns = ('ID', 'Date', 'Time', 'Transaction ID', 'Product Name', 'Product ID', 
                  'Category', 'Customer Name', 'Customer Address', 'Movement Type', 'Quantity', 'Unit Price', 'Total Amount', 'Current Stock')
        self.stock_history_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                              style='Modern.Treeview', height=20)
        
        # Configure columns
        column_widths = {
            'ID': 60,  
            'Date': 80,
            'Time': 80, 
            'Transaction ID': 120,
            'Product Name': 150,
            'Product ID': 80,
            'Category': 100,
            'Customer Name': 120,
            'Customer Address': 200,  
            'Movement Type': 120,
            'Quantity': 70,
            'Unit Price': 90,
            'Total Amount': 100,
            'Current Stock': 90
        }
        
        for col in columns:
            self.stock_history_tree.heading(col, text=col)
            self.stock_history_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
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
        
        # Bind double-click event to edit customer info
        self.stock_history_tree.bind('<Double-Button-1>', self.on_row_double_click)
        
        # Summary section
        summary_frame = ttk.Frame(self.frame, style='Card.TFrame')
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
        
        # Load initial data
        self.refresh_stock_history()
        
        return self.frame

    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().strip()
        if search_term:
            self.search_stock_history(search_term)
        else:
            self.refresh_stock_history()

    def search_stock_history(self, search_term):
        """Search stock history by product name, customer name, or transaction ID"""
        if not hasattr(self, 'stock_history_tree') or not self.stock_history_tree.winfo_exists():
            return
            
        # Clear existing items
        for item in self.stock_history_tree.get_children():
            self.stock_history_tree.delete(item)
            
        try:
            # Build query with search
            date_filter = self.date_filter_var.get() if hasattr(self, 'date_filter_var') else 'All Time'
            category_filter = self.stock_category_var.get() if hasattr(self, 'stock_category_var') else 'All Categories'
            movement_filter = self.movement_type_var.get() if hasattr(self, 'movement_type_var') else 'All Sales'
            
            sales_query = '''
                SELECT 
                    s.id,
                    DATE(s.sale_date) as sale_date,
                    TIME(s.sale_date) as sale_time,
                    s.transaction_id,
                    s.product_name,
                    s.product_id,
                    s.product_category,
                    s.customer_name,
                    COALESCE(s.customer_address, 'N/A') as customer_address,
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
            
            # Add search filter
            search_pattern = f"%{search_term}%"
            sales_query += """ AND (
                s.product_name LIKE ? OR 
                s.customer_name LIKE ? OR 
                s.transaction_id LIKE ?
            )"""
            params.extend([search_pattern, search_pattern, search_pattern])
            
            # Add date filter
            if date_filter == 'Today':
                sales_query += " AND DATE(s.sale_date) = DATE('now')"
            elif date_filter == 'Last 7 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-7 days')"
            elif date_filter == 'Last 30 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-30 days')"
            elif date_filter == 'Last 90 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-90 days')"
            
            # Add category filter
            if category_filter != 'All Categories':
                sales_query += " AND s.product_category = ?"
                params.append(category_filter)
            
            # Add movement type filter
            if movement_filter == 'Returns':
                sales_query += " AND s.quantity < 0" 
            elif movement_filter == 'Regular Sales':
                sales_query += " AND s.quantity > 0"  
            
            # Order by date descending
            sales_query += " ORDER BY s.sale_date DESC, s.id DESC"
            
            # Execute query
            self.main_app.cursor.execute(sales_query, params)
            history_data = self.main_app.cursor.fetchall()
            
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
                customer_name = record[7] if record[7] else 'N/A'
                customer_address = record[8] if record[8] else 'N/A'
                movement_type = record[9] if record[9] else 'N/A'
                quantity = int(record[10]) if record[10] else 0
                unit_price = float(record[11]) if record[11] else 0.0
                total_amount = float(record[12]) if record[12] else 0.0
                current_stock = int(record[13]) if record[13] else 0
                
                self.stock_history_tree.insert('', 'end', values=(
                    record_id,  
                    date_str,
                    time_str,
                    transaction_id,
                    product_name,
                    product_id,
                    category,
                    customer_name,
                    customer_address,
                    movement_type,
                    f"{quantity:,}", 
                    f"₱{unit_price:.2f}",
                    f"₱{total_amount:.2f}",
                    f"{current_stock:,}"
                ))
                
                # Update summary statistics
                total_transactions += 1
                total_items_sold += abs(quantity)  
                total_revenue += total_amount
            
            # Update summary display
            if hasattr(self, 'total_transactions_var'):
                self.total_transactions_var.set(f"{total_transactions:,}")
                self.total_items_sold_var.set(f"{total_items_sold:,}")
                self.total_revenue_var.set(f"₱{total_revenue:,.2f}")
                
            print(f"Found {len(history_data)} records matching '{search_term}'")
            
        except Exception as e:
            print(f"Error searching stock history: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to search stock history: {str(e)}")

    def clear_search(self):
        """Clear the search box and show all records"""
        self.search_var.set("")
        self.refresh_stock_history()

    def on_row_double_click(self, event):
        """Handle double-click on a row to edit customer info"""
        # Get the item that was clicked
        item_id = self.stock_history_tree.identify_row(event.y)
        
        if not item_id:
            return
        
        # Select the row
        self.stock_history_tree.selection_set(item_id)
        
        # Open edit dialog
        self.edit_customer_info()

    def edit_customer_info(self):
        """Edit customer name and address for selected sale record"""
        if not hasattr(self, 'stock_history_tree'):
            messagebox.showwarning("Warning", "Please navigate to stock history first.")
            return
            
        selection = self.stock_history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sale record to edit.")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one record at a time to edit.")
            return
            
        # Get selected item details
        item = self.stock_history_tree.item(selection[0])
        values = item['values']
        
        sales_id = values[0]
        transaction_id = values[3]
        product_name = values[4]
        current_customer_name = values[7]
        current_customer_address = values[8]
        
        # Open edit dialog
        dialog = EditCustomerDialog(
            self.main_app.root, 
            transaction_id,
            product_name,
            current_customer_name if current_customer_name != 'N/A' else '',
            current_customer_address if current_customer_address != 'N/A' else ''
        )
        
        if dialog.result:
            try:
                new_customer_name = dialog.result['customer_name'].strip()
                new_customer_address = dialog.result['customer_address'].strip()
                
                # Update the sales record
                self.main_app.cursor.execute('''
                    UPDATE sales 
                    SET customer_name = ?, customer_address = ?
                    WHERE id = ?
                ''', (new_customer_name if new_customer_name else None,
                      new_customer_address if new_customer_address else None,
                      sales_id))
                
                self.main_app.conn.commit()
                
                # Refresh the display
                self.refresh_stock_history()
                
                messagebox.showinfo("Success", "Customer information updated successfully!")
                
            except sqlite3.Error as e:
                self.main_app.conn.rollback()
                messagebox.showerror("Database Error", f"Failed to update customer information: {str(e)}")
            except Exception as e:
                self.main_app.conn.rollback()
                messagebox.showerror("Error", f"Unexpected error occurred: {str(e)}")

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
                'sales_id': values[0],  
                'date': values[1],
                'transaction_id': values[3],
                'product_name': values[4],
                'customer_name': values[7],
                'movement_type': values[9]
            })
        
        # Confirmation dialog
        if len(selected_items) == 1:
            item = selected_items[0]
            message = (f"Are you sure you want to delete this sale record?\n\n"
                      f"Date: {item['date']}\n"
                      f"Transaction ID: {item['transaction_id']}\n"
                      f"Product: {item['product_name']}\n"
                      f"Customer: {item['customer_name']}\n"
                      f"Type: {item['movement_type']}\n\n"
                      f"⚠️ Warning: This action cannot be undone!")
        else:
            message = (f"Are you sure you want to delete {len(selected_items)} sale records?\n\n"
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
                    self.main_app.cursor.execute('''
                        SELECT product_id, quantity, product_name 
                        FROM sales 
                        WHERE id = ?
                    ''', (sales_id,))
                    sale_details = self.main_app.cursor.fetchone()
                    
                    if sale_details:
                        product_id, quantity, product_name = sale_details
                        
                        restore_stock = messagebox.askyesno(
                            "Restore Stock", 
                            f"Do you want to restore {quantity} units of '{product_name}' back to inventory?\n\n"
                            f"This will add {quantity} units to the current stock level."
                        )
                        
                        # Delete the sales record
                        self.main_app.cursor.execute('DELETE FROM sales WHERE id = ?', (sales_id,))
                        
                        if restore_stock:
                            # Add stock back to the product
                            self.main_app.cursor.execute('''
                                UPDATE products 
                                SET stock = stock + ? 
                                WHERE product_id = ?
                            ''', (quantity, product_id))
                            
                            self.main_app.cursor.execute('''
                                INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                           reference_id, reason, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (product_id, product_name, 'IN', quantity, 
                                  f"RESTORE_{sales_id}", 'SALE_DELETION', 
                                  f'Stock restored due to deletion of sale record {transaction_id}'))
                    
                    deleted_count += 1
                    
                except sqlite3.Error as e:
                    failed_deletions.append(f"Transaction {transaction_id}: {str(e)}")
                    continue
            
            # Commit the changes
            self.main_app.conn.commit()
            
            # Show results
            if deleted_count > 0:
                if failed_deletions:
                    message = (f"Successfully deleted {deleted_count} record(s).\n\n"
                              f"Failed to delete {len(failed_deletions)} record(s):\n" + 
                              "\n".join(failed_deletions))
                    messagebox.showwarning("Partial Success", message)
                else:
                    messagebox.showinfo("Success", f"Successfully deleted {deleted_count} sale record(s)!")
            else:
                if failed_deletions:
                    message = "Failed to delete records:\n" + "\n".join(failed_deletions)
                    messagebox.showerror("Error", message)
                else:
                    messagebox.showinfo("Info", "No records were deleted.")
            
            # Refresh the display
            self.refresh_stock_history()
            
            # Refresh inventory if visible
            if hasattr(self.main_app, 'inventory_module'):
                inventory = self.main_app.inventory_module
                if hasattr(inventory, 'frame') and inventory.frame and inventory.frame.winfo_exists():
                    if inventory.frame.winfo_viewable():
                        inventory.refresh_products()
                
        except sqlite3.Error as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete stock history: {str(e)}")
        except Exception as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Unexpected error occurred: {str(e)}")

    def refresh_stock_history(self):
        """Refresh the stock history display - Shows only sales transactions"""
        if not hasattr(self, 'stock_history_tree') or not self.stock_history_tree.winfo_exists():
            return
            
        # Clear existing items
        for item in self.stock_history_tree.get_children():
            self.stock_history_tree.delete(item)
            
        try:
            # Build query based on filters
            date_filter = self.date_filter_var.get() if hasattr(self, 'date_filter_var') else 'All Time'
            category_filter = self.stock_category_var.get() if hasattr(self, 'stock_category_var') else 'All Categories'
            movement_filter = self.movement_type_var.get() if hasattr(self, 'movement_type_var') else 'All Sales'
            
            sales_query = '''
                SELECT 
                    s.id,
                    DATE(s.sale_date) as sale_date,
                    TIME(s.sale_date) as sale_time,
                    s.transaction_id,
                    s.product_name,
                    s.product_id,
                    s.product_category,
                    s.customer_name,
                    COALESCE(s.customer_address, 'N/A') as customer_address,
                    'Sale (Out)' as movement_type,
                    s.quantity,
                    s.price,
                    s.total,
                    p.stock as current_stock
                FROM sales s
                LEFT JOIN products p ON s.product_id = p.product_id
                WHERE 1=1
            '''
            
            # Add date filter
            params = []
            if date_filter == 'Today':
                sales_query += " AND DATE(s.sale_date) = DATE('now')"
            elif date_filter == 'Last 7 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-7 days')"
            elif date_filter == 'Last 30 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-30 days')"
            elif date_filter == 'Last 90 Days':
                sales_query += " AND DATE(s.sale_date) >= DATE('now', '-90 days')"
            
            # Add category filter
            if category_filter != 'All Categories':
                sales_query += " AND s.product_category = ?"
                params.append(category_filter)
            
            if movement_filter == 'Returns':
                sales_query += " AND s.quantity < 0" 
            elif movement_filter == 'Regular Sales':
                sales_query += " AND s.quantity > 0"  
            
            # Order by date descending
            sales_query += " ORDER BY s.sale_date DESC, s.id DESC"
            
            # Execute query
            self.main_app.cursor.execute(sales_query, params)
            history_data = self.main_app.cursor.fetchall()
            
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
                customer_name = record[7] if record[7] else 'N/A'
                customer_address = record[8] if record[8] else 'N/A'
                movement_type = record[9] if record[9] else 'N/A'
                quantity = int(record[10]) if record[10] else 0
                unit_price = float(record[11]) if record[11] else 0.0
                total_amount = float(record[12]) if record[12] else 0.0
                current_stock = int(record[13]) if record[13] else 0
                
                self.stock_history_tree.insert('', 'end', values=(
                    record_id,  
                    date_str,
                    time_str,
                    transaction_id,
                    product_name,
                    product_id,
                    category,
                    customer_name,
                    customer_address,
                    movement_type,
                    f"{quantity:,}", 
                    f"₱{unit_price:.2f}",
                    f"₱{total_amount:.2f}",
                    f"{current_stock:,}"
                ))
                
                # Update summary statistics
                total_transactions += 1
                total_items_sold += abs(quantity)  
                total_revenue += total_amount
            
            # Update summary display
            if hasattr(self, 'total_transactions_var'):
                self.total_transactions_var.set(f"{total_transactions:,}")
                self.total_items_sold_var.set(f"{total_items_sold:,}")
                self.total_revenue_var.set(f"₱{total_revenue:,.2f}")
                
            print(f"Loaded {len(history_data)} sales records (stock additions excluded)")
            
        except Exception as e:
            print(f"Error refreshing stock history: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load stock history: {str(e)}")

    def filter_stock_history(self, event=None):
        """Filter stock history based on selected criteria"""
        self.refresh_stock_history()

    def refresh(self):
        """Refresh the stock history interface"""
        if self.frame:
            self.refresh_stock_history()
            return self.frame
        return None


class EditCustomerDialog:
    """Dialog for editing customer information"""
    
    def __init__(self, parent, transaction_id, product_name, current_name, current_address):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Customer Information")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Edit Customer Information", 
                 font=('Arial', 14, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Transaction info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(info_frame, text=f"Transaction ID: {transaction_id}", 
                 font=('Arial', 10)).pack(anchor='w', pady=(0, 3))
        ttk.Label(info_frame, text=f"Product: {product_name}", 
                 font=('Arial', 10)).pack(anchor='w')
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        # Customer Name
        ttk.Label(main_frame, text="Customer Name:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar(value=current_name)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50, font=('Arial', 10))
        name_entry.pack(anchor='w', pady=(0, 20), ipady=5)
        name_entry.focus()
        
        # Customer Address
        ttk.Label(main_frame, text="Customer Address:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Text widget for multi-line address
        address_frame = ttk.Frame(main_frame)
        address_frame.pack(anchor='w', fill='x', pady=(0, 20))
        
        self.address_text = tk.Text(address_frame, height=4, width=50, font=('Arial', 10), wrap='word')
        self.address_text.pack(side='left', fill='both', expand=True)
        self.address_text.insert('1.0', current_address)
        
        address_scrollbar = ttk.Scrollbar(address_frame, command=self.address_text.yview)
        address_scrollbar.pack(side='right', fill='y')
        self.address_text.config(yscrollcommand=address_scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_clicked).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_clicked).pack(side='right')
        
        # Bind Enter key (but not in text widget)
        name_entry.bind('<Return>', lambda e: self.save_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        self.dialog.wait_window()
    
    def save_clicked(self):
        customer_name = self.name_var.get().strip()
        customer_address = self.address_text.get('1.0', 'end-1c').strip()
        
        # Allow empty values (will be stored as NULL in database)
        self.result = {
            'customer_name': customer_name,
            'customer_address': customer_address
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()