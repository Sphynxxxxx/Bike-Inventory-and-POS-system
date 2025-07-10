import tkinter as tk
from tkinter import ttk

class ProductDialog:
    def __init__(self, parent, title, product_data=None):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets(product_data)
        self.dialog.wait_window()

    def create_widgets(self, product_data):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Product Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar(value=product_data[1] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Price:").grid(row=1, column=0, sticky='w', pady=5)
        self.price_var = tk.StringVar(value=str(product_data[2]) if product_data else "")
        ttk.Entry(main_frame, textvariable=self.price_var, width=30).grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Stock:").grid(row=2, column=0, sticky='w', pady=5)
        self.stock_var = tk.StringVar(value=str(product_data[3]) if product_data else "")
        ttk.Entry(main_frame, textvariable=self.stock_var, width=30).grid(row=2, column=1, pady=5)

        ttk.Label(main_frame, text="Category:").grid(row=3, column=0, sticky='w', pady=5)
        self.category_var = tk.StringVar(value=product_data[4] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.category_var, width=30).grid(row=3, column=1, pady=5)

        ttk.Label(main_frame, text="Product ID:").grid(row=4, column=0, sticky='w', pady=5)
        self.barcode_var = tk.StringVar(value=product_data[5] if product_data else "")
        ttk.Entry(main_frame, textvariable=self.barcode_var, width=30).grid(row=4, column=1, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Save", command=self.save).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)

    def save(self):
        try:
            name = self.name_var.get().strip()
            price = float(self.price_var.get())
            stock = int(self.stock_var.get())
            category = self.category_var.get().strip()
            barcode = self.barcode_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Product name is required!")
                return
            if price < 0:
                messagebox.showerror("Error", "Price cannot be negative!")
                return
            if stock < 0:
                messagebox.showerror("Error", "Stock cannot be negative!")
                return
            self.result = {
                'name': name,
                'price': price,
                'stock': stock,
                'category': category,
                'barcode': barcode if barcode else None
            }
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for price and stock!")

    def cancel(self):
        self.dialog.destroy()

def create_styles():
    style = ttk.Style()
    style.theme_use('clam')  # Base theme that allows customization
    
    # Configure the main colors
    style.configure('.', background='#ffffff', foreground='#000000')
    
    # Frame styles
    style.configure('TFrame', background='#ffffff', borderwidth=0)
    style.configure('Header.TFrame', background='#222222')
    
    # Label styles
    style.configure('TLabel', background='#ffffff', foreground='#000000', 
                   font=('Helvetica', 9))
    style.configure('Header.TLabel', background='#222222', foreground='#ffffff', 
                   font=('Helvetica', 11, 'bold'))
    style.configure('Title.TLabel', background='#ffffff', foreground='#000000', 
                   font=('Helvetica', 14, 'bold'))
    style.configure('Total.TLabel', background='#ffffff', foreground='#000000', 
                   font=('Helvetica', 12, 'bold'))
    
    # Button styles
    style.configure('TButton', background='#333333', foreground='#ffffff',
                   borderwidth=1, relief='flat', font=('Helvetica', 9))
    style.map('TButton', 
              background=[('active', '#444444'), ('pressed', '#222222')],
              foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])
    
    style.configure('Accent.TButton', background='#555555', foreground='#ffffff',
                   font=('Helvetica', 10, 'bold'))
    style.map('Accent.TButton', 
             background=[('active', '#666666'), ('pressed', '#444444')])
    
    style.configure('Danger.TButton', background='#333333', foreground='#ff4444',
                   font=('Helvetica', 9))
    style.map('Danger.TButton', 
             background=[('active', '#444444'), ('pressed', '#222222')],
             foreground=[('active', '#ff6666'), ('pressed', '#ff2222')])
    
    # Entry styles
    style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', 
                    insertcolor='#000000', bordercolor='#cccccc', relief='solid',
                    padding=5)
    
    # Combobox styles
    style.configure('TCombobox', fieldbackground='#ffffff', foreground='#000000',
                   selectbackground='#333333', selectforeground='#ffffff',
                   arrowsize=12)
    style.map('TCombobox', 
              fieldbackground=[('readonly', '#ffffff')],
              selectbackground=[('readonly', '#333333')])
    
    # Treeview styles
    style.configure('Treeview', background='#ffffff', foreground='#000000',
                   fieldbackground='#ffffff', rowheight=28, 
                   font=('Helvetica', 9), borderwidth=0)
    style.configure('Treeview.Heading', background='#222222', foreground='#ffffff', 
                   relief='flat', font=('Helvetica', 9, 'bold'))
    style.map('Treeview.Heading', background=[('active', '#333333')])
    
    style.configure('Treeview.Row', background='#ffffff', foreground='#000000')
    style.map('Treeview.Row', 
             background=[('selected', '#333333')],
             foreground=[('selected', '#ffffff')])
    
    # Scrollbar styles
    style.configure('Vertical.TScrollbar', background='#dddddd', 
                    arrowcolor='#333333', troughcolor='#f0f0f0')
    style.map('Vertical.TScrollbar', 
              background=[('active', '#cccccc')])
    
    # Notebook styles
    style.configure('TNotebook', background='#ffffff', borderwidth=0)
    style.configure('TNotebook.Tab', background='#dddddd', foreground='#000000',
                   padding=[10, 5], font=('Helvetica', 9))
    style.map('TNotebook.Tab', 
             background=[('selected', '#ffffff'), ('active', '#eeeeee')],
             foreground=[('selected', '#000000'), ('active', '#000000')])