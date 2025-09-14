import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
from PIL import Image, ImageTk

# Static credentials
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    entered_email = email_entry.get()
    entered_password = password_entry.get()

    if entered_email == USERNAME and entered_password == PASSWORD:
        root.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid email or password.")

def open_dashboard():
    # Run the dashboard script
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_path = os.path.join(current_dir, "ui", "main.py")
        python_exe = sys.executable
        subprocess.Popen([python_exe, dashboard_path])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open dashboard: {e}")

def create_gradient_frame(parent, width, height, color1, color2):
    """Create a gradient effect using multiple frames"""
    gradient_frame = tk.Frame(parent, width=width, height=height)
    gradient_frame.pack_propagate(False)
    
    steps = 50
    for i in range(steps):
        # Interpolate between color1 and color2
        ratio = i / (steps - 1)
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        
        stripe = tk.Frame(gradient_frame, bg=color, height=height//steps)
        stripe.pack(fill='x')
    
    return gradient_frame

# Create main window
root = tk.Tk()
root.title("BikeShop Admin Login")
root.geometry("800x500")
root.resizable(False, False)
root.configure(bg="#f0fdff") 

# Center the window on the screen
window_width = 800
window_height = 500

# Get the screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the window geometry with centered position
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Color scheme from bike shop logo
colors = {
    'gradient_start': '#00d4ff',    # Bright cyan
    'gradient_end': '#1e40af',      # Deep blue
    'dark_navy': '#0f172a',         # Almost black
    'white': '#ffffff',
    'light_cyan': '#f0fdff',
    'cyan_accent': '#00bcd4',
    'text_light': '#e2e8f0'
}

# Styling
font_style = ("Helvetica", 14)
label_font = ("Helvetica", 16, "bold")
button_font = ("Helvetica", 14, "bold")

# Main Frame
main_frame = tk.Frame(root, bg=colors['light_cyan'])
main_frame.pack(expand=True, fill="both")

# Left Side (Welcome Section) with gradient-like background
left_frame = tk.Frame(main_frame, bg=colors['dark_navy'], width=400, height=500)
left_frame.pack(side="left", fill="both", expand=False)
left_frame.pack_propagate(False)

# Create a canvas for gradient effect
canvas = tk.Canvas(left_frame, width=400, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Create gradient effect on canvas
for i in range(500):
    ratio = i / 499
    r1, g1, b1 = int(colors['gradient_start'][1:3], 16), int(colors['gradient_start'][3:5], 16), int(colors['gradient_start'][5:7], 16)
    r2, g2, b2 = int(colors['gradient_end'][1:3], 16), int(colors['gradient_end'][3:5], 16), int(colors['gradient_end'][5:7], 16)
    
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    
    color = f"#{r:02x}{g:02x}{b:02x}"
    canvas.create_line(0, i, 400, i, fill=color, width=1)

try:
    # Load the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "assets", "logo", "logo.png")
    logo_image = Image.open(logo_path)  
    logo_image = logo_image.resize((120, 120))  
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Create the logo label on canvas
    canvas.create_image(200, 150, image=logo_photo)
    canvas.image = logo_photo  
except Exception as e:
    print(f"Error loading logo: {e}")
    canvas.create_text(200, 150, text="🚲", font=("Arial", 48), fill="white")

# Welcome text on canvas
canvas.create_text(200, 250, text="Welcome Back!", font=label_font, fill="white", anchor="center")

canvas.create_text(200, 300, text="Access your bike shop analytics\ndashboard and manage your\ninventory with ease.", 
                  font=font_style, fill=colors['text_light'], anchor="center", justify="center")

# Stats Section on canvas
stats_y = 400
canvas.create_text(120, stats_y, text="150+", font=("Helvetica", 18, "bold"), fill="white", anchor="center")
canvas.create_text(120, stats_y + 20, text="Products", font=font_style, fill=colors['text_light'], anchor="center")

canvas.create_text(200, stats_y, text="₱2.5M", font=("Helvetica", 18, "bold"), fill="white", anchor="center")
canvas.create_text(200, stats_y + 20, text="Revenue", font=font_style, fill=colors['text_light'], anchor="center")

canvas.create_text(280, stats_y, text="500+", font=("Helvetica", 18, "bold"), fill="white", anchor="center")
canvas.create_text(280, stats_y + 20, text="Sales", font=font_style, fill=colors['text_light'], anchor="center")

# Right Side (Login Section)
right_frame = tk.Frame(main_frame, bg=colors['white'], width=400, height=500)
right_frame.pack(side="right", fill="both", expand=False)
right_frame.pack_propagate(False)

# Title and Description
title_label = tk.Label(right_frame, text="Sign In", font=("Helvetica", 24, "bold"), 
                      bg=colors['white'], fg=colors['dark_navy'])
title_label.place(relx=0.5, rely=0.15, anchor="center")

# Add a cyan accent line under title
accent_line = tk.Frame(right_frame, bg=colors['cyan_accent'], height=3, width=100)
accent_line.place(relx=0.5, rely=0.2, anchor="center")

description_label = tk.Label(right_frame, text="Enter your credentials to access the dashboard", 
                           font=font_style, bg=colors['white'], fg=colors['gradient_end'])
description_label.place(relx=0.5, rely=0.28, anchor="center")

# Email Entry with modern styling
email_frame = tk.Frame(right_frame, bg=colors['white'])
email_frame.place(relx=0.5, rely=0.4, anchor="center")

email_label = tk.Label(email_frame, text="Email Address", font=("Helvetica", 10, "bold"), 
                      bg=colors['white'], fg=colors['gradient_end'])
email_label.pack(anchor='w')

email_entry = tk.Entry(email_frame, font=font_style, width=25, 
                      relief='solid', borderwidth=2, 
                      highlightcolor=colors['cyan_accent'],
                      highlightthickness=1)
email_entry.pack(pady=(2, 0))
email_entry.insert(0, "admin")

# Password Entry with modern styling
password_frame = tk.Frame(right_frame, bg=colors['white'])
password_frame.place(relx=0.5, rely=0.52, anchor="center")

password_label = tk.Label(password_frame, text="Password", font=("Helvetica", 10, "bold"), 
                         bg=colors['white'], fg=colors['gradient_end'])
password_label.pack(anchor='w')

password_entry = tk.Entry(password_frame, font=font_style, width=25, show="*",
                         relief='solid', borderwidth=2,
                         highlightcolor=colors['cyan_accent'],
                         highlightthickness=1)
password_entry.pack(pady=(2, 0))
password_entry.insert(0, "admin123")

# Remember Me Checkbox with cyan styling
remember_var = tk.BooleanVar(value=True)
remember_checkbox = tk.Checkbutton(right_frame, text="Remember me", variable=remember_var, 
                                  font=("Helvetica", 11), bg=colors['white'], 
                                  activebackground=colors['white'], 
                                  selectcolor=colors['cyan_accent'],
                                  fg=colors['gradient_end'])
remember_checkbox.place(relx=0.5, rely=0.62, anchor="center")

# Login Button with gradient-like styling
class GradientButton(tk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
    
    def on_enter(self, event):
        self.configure(bg=colors['gradient_start'])
    
    def on_leave(self, event):
        self.configure(bg=colors['cyan_accent'])

login_button = GradientButton(right_frame, text="Sign In", command=login, 
                             font=("Helvetica", 14, "bold"), 
                             bg=colors['cyan_accent'], fg="white", 
                             activebackground=colors['gradient_start'], 
                             activeforeground="white", 
                             width=20, height=2,
                             relief='flat',
                             cursor='hand2')
login_button.place(relx=0.5, rely=0.75, anchor="center")

# Add forgot password link
forgot_label = tk.Label(right_frame, text="Forgot password?", 
                       font=("Helvetica", 10, "underline"), 
                       bg=colors['white'], fg=colors['cyan_accent'],
                       cursor='hand2')
forgot_label.place(relx=0.5, rely=0.85, anchor="center")

# Bind Enter key to login
def on_enter_key(event):
    login()

root.bind('<Return>', on_enter_key)
email_entry.bind('<Return>', on_enter_key)
password_entry.bind('<Return>', on_enter_key)

# Focus on email entry
email_entry.focus_set()

# Start GUI loop
root.mainloop()