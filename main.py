import tkinter as tk
from tkinter import messagebox
import subprocess
import os
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
        subprocess.Popen(["python", "ui/main.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open dashboard: {e}")

# Create main window
root = tk.Tk()
root.title("BikeShop Admin Login")
root.geometry("800x500")
root.resizable(False, False)
root.configure(bg="#F0F0F0")

# Center the window on the screen
window_width = 800
window_height = 500

# Get the screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate x and y coordinates for placing the window in the center
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Set the window geometry with centered position
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Styling
font_style = ("Helvetica", 14)
label_font = ("Helvetica", 16, "bold")
button_font = ("Helvetica", 14, "bold")

# Main Frame
main_frame = tk.Frame(root, bg="#F0F0F0")
main_frame.pack(expand=True, fill="both")

# Left Side (Welcome Section)
left_frame = tk.Frame(main_frame, bg="#222222", width=400, height=400)
left_frame.pack(side="left", fill="both", expand=False)

try:
    # Load the image
    logo_image = Image.open("assets/logo/logo.png")  
    logo_image = logo_image.resize((100, 100))  # Resize the image if needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Create the logo label
    logo_label = tk.Label(left_frame, image=logo_photo, bg="#222222")
    logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
    logo_label.place(relx=0.5, rely=0.3, anchor="center")
except Exception as e:
    print(f"Error loading logo: {e}")

welcome_label = tk.Label(left_frame, text="Welcome Back!", font=label_font, fg="white", bg="#222222")
welcome_label.place(relx=0.5, rely=0.5, anchor="center")

description_label = tk.Label(left_frame, text="Access your bike shop analytics\ndashboard and manage your\ninventory with ease.", font=font_style, fg="white", bg="#222222", justify="center")
description_label.place(relx=0.5, rely=0.6, anchor="center")

# Stats Section
stats_frame = tk.Frame(left_frame, bg="#222222")
stats_frame.place(relx=0.5, rely=0.8, anchor="center")

tk.Label(stats_frame, text="150+", font=("Helvetica", 18, "bold"), fg="white", bg="#222222").grid(row=0, column=0, padx=10)
tk.Label(stats_frame, text="Products", font=font_style, fg="white", bg="#222222").grid(row=1, column=0)

tk.Label(stats_frame, text="₹2.5M", font=("Helvetica", 18, "bold"), fg="white", bg="#222222").grid(row=0, column=1, padx=10)
tk.Label(stats_frame, text="Revenue", font=font_style, fg="white", bg="#222222").grid(row=1, column=1)

tk.Label(stats_frame, text="500+", font=("Helvetica", 18, "bold"), fg="white", bg="#222222").grid(row=0, column=2, padx=10)
tk.Label(stats_frame, text="Sales", font=font_style, fg="white", bg="#222222").grid(row=1, column=2)

# Right Side (Login Section)
right_frame = tk.Frame(main_frame, bg="white", width=400, height=400)
right_frame.pack(side="right", fill="both", expand=False)

# Title and Description
title_label = tk.Label(right_frame, text="Sign In", font=label_font, bg="white")
title_label.place(relx=0.5, rely=0.2, anchor="center")

description_label = tk.Label(right_frame, text="Enter your credentials to access the dashboard", font=font_style, bg="white")
description_label.place(relx=0.5, rely=0.3, anchor="center")

# Email Entry
email_entry = tk.Entry(right_frame, font=font_style, width=30)
email_entry.place(relx=0.5, rely=0.4, anchor="center")
email_entry.insert(0, "Email Address")
email_entry.bind("<FocusIn>", lambda args: email_entry.delete('0', 'end') if email_entry.get() == "Email Address" else None)
email_entry.bind("<FocusOut>", lambda args: email_entry.insert(0, "Email Address") if email_entry.get() == "" else None)

# Password Entry
password_entry = tk.Entry(right_frame, font=font_style, width=30, show="*")
password_entry.place(relx=0.5, rely=0.5, anchor="center")
password_entry.insert(0, "Password")
password_entry.bind("<FocusIn>", lambda args: password_entry.delete('0', 'end') if password_entry.get() == "Password" else None)
password_entry.bind("<FocusOut>", lambda args: password_entry.insert(0, "Password") if password_entry.get() == "" else None)

# Remember Me Checkbox
remember_var = tk.BooleanVar(value=True)
remember_checkbox = tk.Checkbutton(right_frame, text="Remember me", variable=remember_var, font=font_style, bg="white", activebackground="white", selectcolor="white")
remember_checkbox.place(relx=0.3, rely=0.6, anchor="center")



# Login Button
login_button = tk.Button(right_frame, text="Sign In", command=login, font=button_font, bg="#222222", fg="white", activebackground="#333333", activeforeground="white", width=20)
login_button.place(relx=0.5, rely=0.7, anchor="center")

# Start GUI loop
root.mainloop()