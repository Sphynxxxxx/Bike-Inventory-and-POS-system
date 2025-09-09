import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from ui_components import ProductDialog

class InventoryModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        
    def create_interface(self):
        """Create the inventory management interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Header.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Inventory", style='PageTitle.TLabel').pack(side='left')
        
        # Controls
        controls_frame = ttk.Frame(self.frame, style='Content.TFrame')
        controls_frame.pack(fill='x', padx=30, pady=10)
        
        ttk.Button(controls_frame, text="Add Product", command=self.add_product, 
                  style='Primary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Edit Product", command=self.edit_product, 
                  style='Secondary.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Delete Product", command=self.delete_product, 
                  style='Danger.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_products, 
                  style='Secondary.TButton').pack(side='left')
        
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
                print(f"Dialog result: {dialog.result}")  
                
                # Validate required fields
                if not dialog.result.get('name'):
                    messagebox.showerror("Error", "Product name is required!")
                    return
                    
                if not dialog.result.get('product_id'):
                    messagebox.showerror("Error", "Product ID is required!")
                    return
                
                # Check if product_id already exists
                self.main_app.cursor.execute('SELECT COUNT(*) FROM products WHERE product_id = ?', 
                                  (dialog.result['product_id'],))
                if self.main_app.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Error", "Product ID already exists! Please use a unique Product ID.")
                    return
                
                # Format the product_id to ensure consistency
                formatted_product_id = str(dialog.result['product_id']).strip()
                
                # Insert the product with formatted product_id
                self.main_app.cursor.execute('''
                    INSERT INTO products (name, price, stock, category, product_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (dialog.result['name'], 
                      float(dialog.result['price']), 
                      int(dialog.result['stock']),
                      dialog.result['category'], 
                      formatted_product_id))
                
                # Record initial stock addition
                if dialog.result['stock'] > 0:
                    self.main_app.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                   reference_id, reason, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (dialog.result['product_id'], dialog.result['name'], 'IN', 
                          dialog.result['stock'], 'INITIAL', 'INITIAL_STOCK', 
                          'Initial stock when product was added to inventory'))
                
                self.main_app.conn.commit()
                messagebox.showinfo("Success", f"Product '{dialog.result['name']}' added successfully!")
                
                # Refresh inventory display
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
            
        old_stock = product[3]  # Get current stock before editing
        
        dialog = ProductDialog(self.main_app.root, "Edit Product", product)
        if dialog.result:
            try:
                new_stock = int(dialog.result['stock'])
                stock_difference = new_stock - old_stock
                
                # Format the product_id to ensure consistency
                formatted_product_id = str(dialog.result['product_id']).strip()
                
                self.main_app.cursor.execute('''
                    UPDATE products SET name = ?, price = ?, stock = ?, category = ?, product_id = ?
                    WHERE id = ?
                ''', (dialog.result['name'], float(dialog.result['price']), new_stock,
                      dialog.result['category'], formatted_product_id, product_id))
                
                # Record stock movement if stock changed
                if stock_difference != 0:
                    movement_type = 'IN' if stock_difference > 0 else 'OUT'
                    reason = 'STOCK_ADJUSTMENT'
                    notes = f"Stock adjusted from {old_stock} to {new_stock} (difference: {stock_difference:+d})"
                    
                    self.main_app.cursor.execute('''
                        INSERT INTO stock_movements (product_id, product_name, movement_type, quantity, 
                                                   reference_id, reason, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (dialog.result['product_id'], dialog.result['name'], movement_type, 
                          abs(stock_difference), f"EDIT_{product_id}", reason, notes))
                
                self.main_app.conn.commit()
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
                    
                print(f"Loaded {len(products)} products into inventory")  # Debug print
                
            except Exception as e:
                print(f"Error refreshing products: {e}")
                messagebox.showerror("Error", f"Failed to load products: {str(e)}")
        else:
            print("Inventory tree not available yet")  # Debug print

    def refresh(self):
        """Refresh the inventory interface"""
        if self.frame:
            self.refresh_products()
            return self.frame
        return None