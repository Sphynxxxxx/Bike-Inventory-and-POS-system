import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from ui_components import ProductDialog

class InventoryModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.search_var = None
        
    def create_interface(self):
        """Create the inventory management interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Inventory", style='PageTitle.TLabel').pack(side='left')
        
        # Search frame
        search_frame = ttk.Frame(self.frame, style='Content.TFrame')
        search_frame.pack(fill='x', padx=30, pady=10)
        
        # Search box
        ttk.Label(search_frame, text="Search:", style='Content.TLabel').pack(side='left', padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        # Clear search button
        ttk.Button(search_frame, text="Clear", command=self.clear_search, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        
        # Search hint label
        ttk.Label(search_frame, text="(Search by name or product ID)", 
                 style='Hint.TLabel').pack(side='left', padx=(10, 0))
        
        # Controls
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Button(controls_frame, text="Add Product", command=self.add_product, 
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Add Stock", command=self.add_stock, 
                  style='Success.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit Product", command=self.edit_product, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete Product", command=self.delete_product, 
                  style='Danger.TButton').pack(side='left')
        
        # Inventory table
        table_frame = ttk.Frame(self.frame, style='Content.TFrame')
        table_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Create treeview
        columns = ('ID', 'Name', 'Price', 'Stock', 'Category', 'Product ID')
        self.inventory_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style='Modern.Treeview')
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            if col == 'ID':
                self.inventory_tree.column(col, width=50)
            elif col == 'Name':
                self.inventory_tree.column(col, width=200)
            else:
                self.inventory_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load initial data
        self.refresh_products()
        
        print("Inventory interface created successfully")  # Debug print
        
        return self.frame

    def add_stock(self):
        """Add stock to an existing product"""
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add stock to.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]  # Internal database ID
        product_name = item['values'][1]
        current_stock = item['values'][3]
        product_code = item['values'][5]  
        
        # Create a simple dialog for stock addition
        stock_dialog = AddStockDialog(self.main_app.root, product_name, current_stock)
        if stock_dialog.result:
            try:
                quantity_to_add = stock_dialog.result['quantity']
                
                if quantity_to_add <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0!")
                    return
                
                # Get current stock from database to ensure accuracy
                self.main_app.cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
                current_db_stock = self.main_app.cursor.fetchone()[0]
                
                new_stock = current_db_stock + quantity_to_add
                
                # Update product stock
                self.main_app.cursor.execute('''
                    UPDATE products SET stock = ? WHERE id = ?
                ''', (new_stock, product_id))
                
                # Record stock movement
                self.main_app.cursor.execute('''
                    INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                            reference_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_code, product_name, 'IN', quantity_to_add, 
                      f"STOCK_ADD_{product_id}", f"Stock addition: {quantity_to_add} units added"))
                
                self.main_app.conn.commit()
                
                # Refresh display (respects current search)
                if self.search_var and self.search_var.get().strip():
                    self.search_products(self.search_var.get().strip())
                else:
                    self.refresh_products()
                    
                messagebox.showinfo("Success", 
                    f"Added {quantity_to_add} units to '{product_name}'\n"
                    f"Previous stock: {current_db_stock}\n"
                    f"New stock: {new_stock}")
                
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
                self.main_app.conn.rollback()
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get().strip()
        if search_term:
            self.search_products(search_term)
        else:
            self.refresh_products()

    def search_products(self, search_term):
        """Search products by name or product ID"""
        if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
            try:
                # Clear existing items
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                
                search_pattern = f"%{search_term}%"
                self.main_app.cursor.execute('''
                    SELECT id, name, price, stock, category, product_id 
                    FROM products 
                    WHERE name LIKE ? OR product_id LIKE ? 
                    ORDER BY name
                ''', (search_pattern, search_pattern))
                
                products = self.main_app.cursor.fetchall()
                
                # Insert filtered products into treeview
                for product in products:
                    self.inventory_tree.insert('', 'end', values=(
                        product[0],  # id
                        product[1],  # name
                        f"₱{product[2]:.2f}",  # price
                        product[3],  # stock
                        product[4],  # category
                        product[5]   # product_id
                    ))
                
                print(f"Found {len(products)} products matching '{search_term}'") 
                
            except Exception as e:
                print(f"Error searching products: {e}")
                messagebox.showerror("Error", f"Failed to search products: {str(e)}")

    def clear_search(self):
        """Clear the search box and show all products"""
        self.search_var.set("")
        self.refresh_products()

    def validate_product_data(self, product_data):
        """Validate product data before adding or updating"""
        try:
            # Validate name
            if not product_data.get('name') or not product_data['name'].strip():
                raise ValueError("Product name is required!")
                
            # Validate product_id
            if not product_data.get('product_id') or not str(product_data['product_id']).strip():
                raise ValueError("Product ID is required!")
                
            # Validate price
            try:
                price = float(product_data['price'])
                if price < 0:
                    raise ValueError("Price cannot be negative!")
            except (TypeError, ValueError):
                raise ValueError("Invalid price value!")
                
            # Validate stock
            try:
                stock = int(product_data['stock'])
                if stock < 0:
                    raise ValueError("Stock cannot be negative!")
            except (TypeError, ValueError):
                raise ValueError("Invalid stock value!")
                
            return True
                
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return False

    def add_product(self):
        try:
            dialog = ProductDialog(self.main_app.root, "Add Product")
            if dialog.result:
                # Validate the product data first
                if not self.validate_product_data(dialog.result):
                    return
                    
                print(f"Dialog result: {dialog.result}")  
                
                # Validate required fields
                if not dialog.result.get('name'):
                    messagebox.showerror("Error", "Product name is required!")
                    return
                    
            
                product_id_input = dialog.result.get('product_id', '').strip()
                if not product_id_input:
                    messagebox.showerror("Error", "Product ID is required!")
                    return
                
                
                self.main_app.cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', 
                                (product_id_input,))
                if self.main_app.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Product ID already exists! Please use a unique Product ID.")
                    return
                
            
                self.main_app.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, product_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], 
                    float(dialog.result['price']), 
                    int(dialog.result['stock']),
                    dialog.result['category'], 
                    product_id_input))  # Use the validated product_id
                
                # Record initial stock addition
                if int(dialog.result['stock']) > 0:
                    self.main_app.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                reference_id, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (product_id_input, dialog.result['name'], 'IN', 
                        int(dialog.result['stock']), 'INITIAL', 
                        'Initial stock when product was added to inventory'))
                
                self.main_app.conn.commit()
                messagebox.showinfo("Success", f"Product '{dialog.result['name']}' added successfully!")
                
                # Refresh inventory display (respects current search)
                if self.search_var and self.search_var.get().strip():
                    self.search_products(self.search_var.get().strip())
                else:
                    self.refresh_products()
                
        except sqlite3.IntegrityError as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Product ID already exists or constraint violation: {str(e)}")
        except sqlite3.Error as e:
            self.main_app.conn.rollback()
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            print(f"Exception in add_product: {e}") 

    def edit_product(self):
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0] 
        
        self.main_app.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = self.main_app.cursor.fetchone()
        
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
            
        old_stock = product[3]  
        
        dialog = ProductDialog(self.main_app.root, "Edit Product", product)
        if dialog.result:
            try:
                new_stock = int(dialog.result['stock'])
                stock_difference = new_stock - old_stock
                
                # Get the original product_id from the database
                original_product_id = product[5]  
                
                # Format the product_id to ensure consistency
                formatted_product_id = str(dialog.result['product_id']).strip()
                
                # Check if product_id is being changed and if the new one already exists
                if formatted_product_id != original_product_id:
                    self.main_app.cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', 
                                    (formatted_product_id,))
                    if self.main_app.cursor.fetchone()[0] > 0:
                        messagebox.showerror("Error", "Product ID already exists! Please use a unique Product ID.")
                        return
                
                self.main_app.cursor.execute('''
                    UPDATE products SET name = ?, price = ?, stock = ?, category = ?, product_id = ?
                    WHERE id = ?
                ''', (dialog.result['name'], float(dialog.result['price']), new_stock,
                    dialog.result['category'], formatted_product_id, product_id))
                
                # Record stock movement if stock changed
                if stock_difference != 0:
                    movement_type = 'IN' if stock_difference > 0 else 'OUT'
                    notes = f"Stock adjusted from {old_stock} to {new_stock} (difference: {stock_difference:+d})"
                    
                    self.main_app.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                reference_id, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (formatted_product_id, dialog.result['name'], movement_type, 
                        abs(stock_difference), f"EDIT_{product_id}", notes))
                
                self.main_app.conn.commit()
                
                # Refresh display (respects current search)
                if self.search_var and self.search_var.get().strip():
                    self.search_products(self.search_var.get().strip())
                else:
                    self.refresh_products()
                    
                messagebox.showinfo("Success", "Product updated successfully!")
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Product ID already exists!")
                self.main_app.conn.rollback()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to update product: {str(e)}")
                self.main_app.conn.rollback()

    def delete_product(self):
        if not hasattr(self, 'inventory_tree'):
            messagebox.showwarning("Warning", "Please navigate to inventory first.")
            return
            
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete.")
            return
            
        item = self.inventory_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            try:
                # First get the product_id for the sales deletion
                self.main_app.cursor.execute('SELECT product_id FROM products WHERE id = ?', (product_id,))
                product_code = self.main_app.cursor.fetchone()
                
                if product_code:
                    # Delete related sales records first
                    self.main_app.cursor.execute('DELETE FROM sales WHERE product_id = ?', (product_code[0],))
                    # Delete related stock movements
                    self.main_app.cursor.execute('DELETE FROM stock_movements WHERE product_id = ?', (product_code[0],))
                    
                # Delete the product
                self.main_app.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.main_app.conn.commit()
                
                # Refresh display (respects current search)
                if self.search_var and self.search_var.get().strip():
                    self.search_products(self.search_var.get().strip())
                else:
                    self.refresh_products()
                    
                messagebox.showinfo("Success", "Product deleted successfully!")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to delete product: {str(e)}")
                self.main_app.conn.rollback()

    def refresh_products(self):
        """Refresh the inventory display"""
        if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
            try:
                # Clear existing items
                for item in self.inventory_tree.get_children():
                    self.inventory_tree.delete(item)
                
                # Get all products from database
                self.main_app.cursor.execute('SELECT id, name, price, stock, category, product_id FROM products ORDER BY name')
                products = self.main_app.cursor.fetchall()
                
                # Insert products into treeview
                for product in products:
                    self.inventory_tree.insert('', 'end', values=(
                        product[0],  # id
                        product[1],  # name
                        f"₱{product[2]:.2f}",  # price
                        product[3],  # stock
                        product[4],  # category
                        product[5]   # product_id
                    ))
                    
                print(f"Loaded {len(products)} products into inventory")
                
            except Exception as e:
                print(f"Error refreshing products: {e}")
                messagebox.showerror("Error", f"Failed to load products: {str(e)}")
        else:
            print("Inventory tree not available yet")  

    def refresh(self):
        """Refresh the inventory interface"""
        if self.frame:
            if self.search_var and self.search_var.get().strip():
                self.search_products(self.search_var.get().strip())
            else:
                self.refresh_products()
            return self.frame
        return None


class AddStockDialog:
    """Simple dialog for adding stock to existing products"""
    
    def __init__(self, parent, product_name, current_stock):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Stock")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (220 // 2)
        self.dialog.geometry(f"350x220+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Product info
        ttk.Label(main_frame, text=f"Product: {product_name}", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Label(main_frame, text=f"Current Stock: {current_stock}", 
                 font=('Arial', 10)).pack(anchor='w', pady=(0, 20))
        
        # Quantity to add
        ttk.Label(main_frame, text="Quantity to Add:").pack(anchor='w', pady=(0, 5))
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(main_frame, textvariable=self.quantity_var, width=20)
        quantity_entry.pack(anchor='w', pady=(0, 20))
        quantity_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Add Stock", command=self.ok_clicked).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='right')
        
        # Bind Enter key to OK
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        self.dialog.wait_window()
    
    def ok_clicked(self):
        try:
            quantity = int(self.quantity_var.get().strip())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0!")
                return
            
            self.result = {
                'quantity': quantity
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
    
    def cancel_clicked(self):
        self.dialog.destroy()