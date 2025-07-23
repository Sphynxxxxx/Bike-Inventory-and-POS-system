import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

class PointOfSaleModule:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.cart_items = []
        self.current_customer = ""
        
    def create_interface(self):
        """Create the Point of Sale interface"""
        self.frame = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.frame, style='Content.TFrame')
        header_frame.pack(fill='x', padx=30, pady=20)
        
        ttk.Label(header_frame, text="Point of Sale", style='PageTitle.TLabel').pack(side='left')
        
        # Customer info section
        customer_frame = ttk.Frame(self.frame, style='Card.TFrame')
        customer_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        customer_content = ttk.Frame(customer_frame, style='Card.TFrame')
        customer_content.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(customer_content, text="Customer Name:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.customer_var = tk.StringVar()
        self.customer_entry = ttk.Entry(customer_content, textvariable=self.customer_var, 
                                       style='Modern.TEntry', width=30)
        self.customer_entry.pack(side='left', padx=(0, 10))
        self.customer_entry.bind('<Return>', self.focus_product_search)
        
        # Main content area
        main_content = ttk.Frame(self.frame, style='Content.TFrame')
        main_content.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        
        # Left side - Product search and selection
        left_panel = ttk.Frame(main_content, style='Card.TFrame')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Product search
        search_header = ttk.Frame(left_panel, style='Card.TFrame')
        search_header.pack(fill='x', padx=20, pady=(15, 10))
        ttk.Label(search_header, text="Product Search", style='SectionTitle.TLabel').pack(side='left')
        
        search_frame = ttk.Frame(left_panel, style='Card.TFrame')
        search_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                     style='Modern.TEntry', width=25)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_products)
        self.search_entry.bind('<Return>', self.add_first_product)
        
        ttk.Button(search_frame, text="Add", command=self.add_selected_product,
                  style='Primary.TButton').pack(side='left')
        
        # Product list
        product_list_frame = ttk.Frame(left_panel, style='Card.TFrame')
        product_list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Products treeview
        product_columns = ('ID', 'Name', 'Price', 'Stock')
        self.product_tree = ttk.Treeview(product_list_frame, columns=product_columns, 
                                        show='headings', style='Modern.Treeview', height=15)
        
        for col in product_columns:
            self.product_tree.heading(col, text=col)
            if col == 'ID':
                self.product_tree.column(col, width=80)
            elif col == 'Name':
                self.product_tree.column(col, width=200)
            else:
                self.product_tree.column(col, width=100)
        
        # Scrollbar for products
        product_scrollbar = ttk.Scrollbar(product_list_frame, orient='vertical', 
                                         command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=product_scrollbar.set)
        
        self.product_tree.pack(side='left', fill='both', expand=True)
        product_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to add product
        self.product_tree.bind('<Double-1>', self.on_product_double_click)
        
        # Right side - Cart and checkout
        right_panel = ttk.Frame(main_content, style='Card.TFrame')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Cart header
        cart_header = ttk.Frame(right_panel, style='Card.TFrame')
        cart_header.pack(fill='x', padx=20, pady=(15, 10))
        ttk.Label(cart_header, text="Shopping Cart", style='SectionTitle.TLabel').pack(side='left')
        ttk.Button(cart_header, text="Clear Cart", command=self.clear_cart,
                  style='Danger.TButton').pack(side='right')
        
        # Cart items
        cart_frame = ttk.Frame(right_panel, style='Card.TFrame')
        cart_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Cart treeview
        cart_columns = ('Product', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, 
                                     show='headings', style='Modern.Treeview', height=12)
        
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            if col == 'Product':
                self.cart_tree.column(col, width=150)
            else:
                self.cart_tree.column(col, width=80)
        
        # Scrollbar for cart
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient='vertical', 
                                      command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side='left', fill='both', expand=True)
        cart_scrollbar.pack(side='right', fill='y')
        
        # Bind keys for cart management
        self.cart_tree.bind('<Delete>', self.remove_cart_item)
        self.cart_tree.bind('<Double-1>', self.edit_cart_item_quantity)
        
        # Total and checkout section
        checkout_frame = ttk.Frame(right_panel, style='Card.TFrame')
        checkout_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Total display
        total_frame = ttk.Frame(checkout_frame, style='Card.TFrame')
        total_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(total_frame, text="Total:", style='SectionTitle.TLabel').pack(side='left')
        self.total_var = tk.StringVar(value="₱0.00")
        ttk.Label(total_frame, textvariable=self.total_var, 
                 style='CardValue.TLabel').pack(side='right')
        
        # Payment method
        payment_frame = ttk.Frame(checkout_frame, style='Card.TFrame')
        payment_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(payment_frame, text="Payment:", style='FieldLabel.TLabel').pack(side='left', padx=(0, 10))
        self.payment_var = tk.StringVar(value='Cash')
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_var,
                                    values=['Cash', 'Card', 'GCash', 'Maya'], 
                                    state='readonly', style='Modern.TCombobox', width=15)
        payment_combo.pack(side='left')
        
        # Checkout button
        ttk.Button(checkout_frame, text="💳 CHECKOUT", command=self.process_checkout,
                  style='Success.TButton').pack(fill='x', pady=(10, 0))
        
        # Load products
        self.load_products()
        
        # Focus customer entry
        self.customer_entry.focus()
        
        return self.frame
    
    def focus_product_search(self, event=None):
        """Focus on product search after customer entry"""
        self.search_entry.focus()
    
    def load_products(self):
        """Load all products into the product list"""
        try:
            # Clear existing items
            for item in self.product_tree.get_children():
                self.product_tree.delete(item)
            
            # Get all products
            products = self.main_app.get_all_products()
            
            for product in products:
                self.product_tree.insert('', 'end', values=(
                    product[0],  # product_id
                    product[1],  # name
                    f"₱{product[2]:.2f}",  # price
                    product[3]   # stock
                ))
                
        except Exception as e:
            print(f"Error loading products: {e}")
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
    
    def filter_products(self, event=None):
        """Filter products based on search term"""
        search_term = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get all products and filter
        products = self.main_app.get_all_products()
        
        for product in products:
            if (search_term in product[1].lower() or  # name
                search_term in product[0].lower()):   # product_id
                self.product_tree.insert('', 'end', values=(
                    product[0],  # product_id
                    product[1],  # name
                    f"₱{product[2]:.2f}",  # price
                    product[3]   # stock
                ))
    
    def add_first_product(self, event=None):
        """Add the first product in the filtered list"""
        children = self.product_tree.get_children()
        if children:
            self.product_tree.selection_set(children[0])
            self.add_selected_product()
    
    def on_product_double_click(self, event):
        """Handle double-click on product"""
        self.add_selected_product()
    
    def add_selected_product(self):
        """Add selected product to cart"""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to add.")
            return
        
        if not self.customer_var.get().strip():
            messagebox.showwarning("Warning", "Please enter customer name first.")
            self.customer_entry.focus()
            return
        
        item = self.product_tree.item(selection[0])
        product_data = item['values']
        
        product_id = product_data[0]
        product_name = product_data[1]
        price_str = product_data[2].replace('₱', '').replace(',', '')
        price = float(price_str)
        stock = int(product_data[3])
        
        if stock <= 0:
            messagebox.showwarning("Warning", f"'{product_name}' is out of stock!")
            return
        
        # Check if product already in cart
        for i, cart_item in enumerate(self.cart_items):
            if cart_item['product_id'] == product_id:
                # Increase quantity if stock allows
                current_qty = cart_item['quantity']
                if current_qty < stock:
                    self.cart_items[i]['quantity'] += 1
                    self.refresh_cart()
                    return
                else:
                    messagebox.showwarning("Warning", f"Cannot add more. Only {stock} units available.")
                    return
        
        # Add new item to cart
        cart_item = {
            'product_id': product_id,
            'product_name': product_name,
            'customer_name': self.customer_var.get().strip(),
            'unit_price': price,
            'quantity': 1,
            'category': 'General'  # You can enhance this to get actual category
        }
        
        self.cart_items.append(cart_item)
        self.refresh_cart()
        
        # Clear search and focus back to search
        self.search_var.set("")
        self.filter_products()
        self.search_entry.focus()
    
    def refresh_cart(self):
        """Refresh cart display and calculate total"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total = 0
        
        # Add items to cart tree
        for cart_item in self.cart_items:
            item_total = cart_item['quantity'] * cart_item['unit_price']
            total += item_total
            
            self.cart_tree.insert('', 'end', values=(
                cart_item['product_name'][:20] + "..." if len(cart_item['product_name']) > 20 else cart_item['product_name'],
                cart_item['quantity'],
                f"₱{cart_item['unit_price']:.2f}",
                f"₱{item_total:.2f}"
            ))
        
        # Update total display
        self.total_var.set(f"₱{total:,.2f}")
    
    def remove_cart_item(self, event=None):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        # Get the index of selected item
        selected_index = self.cart_tree.index(selection[0])
        
        # Remove from cart_items list
        if 0 <= selected_index < len(self.cart_items):
            removed_item = self.cart_items.pop(selected_index)
            self.refresh_cart()
            print(f"Removed {removed_item['product_name']} from cart")
    
    def edit_cart_item_quantity(self, event=None):
        """Edit quantity of cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        selected_index = self.cart_tree.index(selection[0])
        if not (0 <= selected_index < len(self.cart_items)):
            return
        
        cart_item = self.cart_items[selected_index]
        
        # Get available stock
        current_stock = self.main_app.get_current_stock(cart_item['product_id'])
        
        # Ask for new quantity
        new_qty = simpledialog.askinteger(
            "Edit Quantity",
            f"Enter new quantity for {cart_item['product_name']}:\n(Available stock: {current_stock})",
            initialvalue=cart_item['quantity'],
            minvalue=1,
            maxvalue=current_stock
        )
        
        if new_qty and new_qty != cart_item['quantity']:
            self.cart_items[selected_index]['quantity'] = new_qty
            self.refresh_cart()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items and messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart_items.clear()
            self.refresh_cart()
    
    def process_checkout(self):
        """Process the checkout"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        
        if not self.customer_var.get().strip():
            messagebox.showwarning("Warning", "Please enter customer name.")
            self.customer_entry.focus()
            return
        
        # Update customer name in all cart items
        customer_name = self.customer_var.get().strip()
        for item in self.cart_items:
            item['customer_name'] = customer_name
        
        # Validate transaction
        is_valid, message = self.main_app.validate_transaction(self.cart_items)
        if not is_valid:
            messagebox.showerror("Validation Error", message)
            return
        
        # Show checkout confirmation
        total = sum(item['quantity'] * item['unit_price'] for item in self.cart_items)
        
        if messagebox.askyesno("Confirm Checkout", 
                              f"Customer: {customer_name}\n"
                              f"Items: {len(self.cart_items)}\n"
                              f"Total: ₱{total:,.2f}\n"
                              f"Payment: {self.payment_var.get()}\n\n"
                              f"Process this sale?"):
            
            # Process the sale
            success, result = self.main_app.record_sale(self.cart_items, self.payment_var.get())
            
            if success:
                messagebox.showinfo("Success", 
                                   f"Sale completed successfully!\n"
                                   f"Transaction ID: {result}\n"
                                   f"Total: ₱{total:,.2f}")
                
                # Clear cart and reset customer
                self.cart_items.clear()
                self.customer_var.set("")
                self.refresh_cart()
                self.load_products()  # Refresh to show updated stock
                self.customer_entry.focus()
                
                # Print receipt option
                if messagebox.askyesno("Print Receipt", "Would you like to print a receipt?"):
                    self.print_receipt(result, customer_name, total)
                    
            else:
                messagebox.showerror("Error", f"Failed to process sale:\n{result}")
    
    def print_receipt(self, transaction_id, customer_name, total):
        """Show receipt in a popup window"""
        receipt_window = tk.Toplevel(self.frame)
        receipt_window.title("Receipt")
        receipt_window.geometry("400x600")
        receipt_window.configure(bg='white')
        receipt_window.transient(self.frame)
        receipt_window.grab_set()
        
        # Center the window
        receipt_window.update_idletasks()
        x = (receipt_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (receipt_window.winfo_screenheight() // 2) - (600 // 2)
        receipt_window.geometry(f"400x600+{x}+{y}")
        
        # Receipt content
        receipt_frame = ttk.Frame(receipt_window)
        receipt_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        ttk.Label(receipt_frame, text="BIKE SHOP", font=('Arial', 16, 'bold')).pack()
        ttk.Label(receipt_frame, text="Sales Receipt", font=('Arial', 12)).pack(pady=(0, 10))
        
        # Transaction info
        info_frame = ttk.Frame(receipt_frame)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Transaction ID: {transaction_id}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Customer: {customer_name}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Payment: {self.payment_var.get()}").pack(anchor='w')
        
        # Separator
        ttk.Separator(receipt_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Items
        items_frame = ttk.Frame(receipt_frame)
        items_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        for item in self.cart_items:
            item_frame = ttk.Frame(items_frame)
            item_frame.pack(fill='x', pady=2)
            
            ttk.Label(item_frame, text=item['product_name']).pack(anchor='w')
            ttk.Label(item_frame, text=f"  {item['quantity']} x ₱{item['unit_price']:.2f} = ₱{item['quantity'] * item['unit_price']:.2f}").pack(anchor='w')
        
        # Separator
        ttk.Separator(receipt_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Total
        ttk.Label(receipt_frame, text=f"TOTAL: ₱{total:,.2f}", 
                 font=('Arial', 14, 'bold')).pack(anchor='w')
        
        # Thank you message
        ttk.Label(receipt_frame, text="Thank you for your purchase!", 
                 font=('Arial', 10)).pack(pady=(20, 0))
        
        # Close button
        ttk.Button(receipt_frame, text="Close", 
                  command=receipt_window.destroy).pack(pady=(20, 0))
        
        # Focus on close button
        receipt_window.focus_set()
    
    def refresh(self):
        """Refresh the POS interface"""
        if self.frame:
            self.load_products()
            return self.frame
        return None