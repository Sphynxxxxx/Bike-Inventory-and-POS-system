import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class StockHistoryModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the stock history interface - UPDATED to show customer names"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Stock History", style='PageTitle.TLabel').pack(side='left')
        
        # Controls and filters
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
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
        table_frame = ttk.Frame(self.frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview for stock history - UPDATED to include Customer Name
        columns = ('ID', 'Date', 'Time', 'Transaction ID', 'Product Name', 'Product ID', 
                  'Category', 'Customer Name', 'Movement Type', 'Quantity', 'Unit Price', 'Total Amount', 'Current Stock')
        self.stock_history_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                              style='Modern.Treeview')
        
        # Configure columns
        column_widths = {
            'ID': 60,  
            'Date': 80,
            'Time': 80, 
            'Transaction ID': 120,
            'Product Name': 120,
            'Product ID': 80,
            'Category': 80,
            'Customer Name': 100,
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
                'customer_name': values[7],
                'movement_type': values[8]
            })
        
        # Confirmation dialog
        if len(selected_items) == 1:
            item = selected_items[0]
            message = (f"Are you sure you want to delete this stock history record?\n\n"
                      f"Date: {item['date']}\n"
                      f"Transaction ID: {item['transaction_id']}\n"
                      f"Product: {item['product_name']}\n"
                      f"Customer: {item['customer_name']}\n"
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
                        self.main_app.cursor.execute('''
                            SELECT product_id, quantity, product_name 
                            FROM sales 
                            WHERE id = ?
                        ''', (sales_id,))
                        sale_details = self.main_app.cursor.fetchone()
                        
                        if sale_details:
                            product_id, quantity, product_name = sale_details
                            
                            # Ask if user wants to restore stock to inventory
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
                                
                                # Record the stock restoration in stock_movements table
                                self.main_app.cursor.execute('''
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
            self.main_app.conn.commit()
            
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
            if hasattr(self.main_app, 'inventory_frame') and self.main_app.inventory_frame and self.main_app.inventory_frame.winfo_viewable():
                self.main_app.refresh_products()
                
        except sqlite3.Error as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete stock history: {str(e)}")
        except Exception as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Unexpected error occurred: {str(e)}")

    def refresh_stock_history(self):
        """Refresh the stock history display - UPDATED to show customer names"""
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
            
            # Base query for sales (stock out) - UPDATED to include customer_name
            base_query = '''
                SELECT 
                    s.id,
                    DATE(s.sale_date) as sale_date,
                    TIME(s.sale_date) as sale_time,
                    s.transaction_id,
                    s.product_name,
                    s.product_id,
                    s.product_category,
                    s.customer_name,
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
                        'System' as customer_name,
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
            self.main_app.cursor.execute(base_query, params)
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
                movement_type = record[8] if record[8] else 'N/A'
                quantity = int(record[9]) if record[9] else 0
                unit_price = float(record[10]) if record[10] else 0.0
                total_amount = float(record[11]) if record[11] else 0.0
                current_stock = int(record[12]) if record[12] else 0
                
                # Insert into treeview (ID is first but hidden)
                self.stock_history_tree.insert('', 'end', values=(
                    record_id,  # Hidden ID for deletion
                    date_str,
                    time_str,
                    transaction_id,
                    product_name,
                    product_id,
                    category,
                    customer_name,  # Customer name column
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

    def refresh(self):
        """Refresh the stock history interface"""
        if self.frame:
            self.refresh_stock_history()
            return self.frame
        return None