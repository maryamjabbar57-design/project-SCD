import tkinter as tk
from tkinter import messagebox
from app.gui.styles import COLORS, FONTS

class AuthScreen:
    def __init__(self, parent, db_manager, on_login_success):
        self.parent = parent
        self.db = db_manager
        self.on_login_success = on_login_success
        self.frame = tk.Frame(parent, bg=COLORS["background"])
        self.frame.pack(fill="both", expand=True)
        
        self.show_login()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Quiz Master Pro", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=40)
        
        container = tk.Frame(self.frame, bg=COLORS["white"], padx=40, pady=40)
        container.pack(pady=10)

        tk.Label(container, text="Username", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        self.user_entry = tk.Entry(container, font=FONTS["body"], width=30)
        self.user_entry.pack(pady=(5, 15))

        tk.Label(container, text="Password", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        self.pass_entry = tk.Entry(container, font=FONTS["body"], width=30, show="*")
        self.pass_entry.pack(pady=(5, 25))

        tk.Button(container, text="Login", font=FONTS["button"], bg=COLORS["primary"], 
                  fg="white", width=25, command=self.handle_login).pack(pady=10)
        
        tk.Button(self.frame, text="Don't have an account? Register", font=FONTS["body"], 
                  bg=COLORS["background"], bd=0, fg=COLORS["secondary"], 
                  command=self.show_register).pack()

    def show_register(self):
        self.clear_frame()
        
        tk.Label(self.frame, text="Create Account", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=40)
        
        container = tk.Frame(self.frame, bg=COLORS["white"], padx=40, pady=40)
        container.pack(pady=10)

        tk.Label(container, text="Choose Username", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        self.reg_user = tk.Entry(container, font=FONTS["body"], width=30)
        self.reg_user.pack(pady=(5, 15))

        tk.Label(container, text="Choose Password", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        self.reg_pass = tk.Entry(container, font=FONTS["body"], width=30, show="*")
        self.reg_pass.pack(pady=(5, 25))

        tk.Button(container, text="Register", font=FONTS["button"], bg=COLORS["success"], 
                  fg="white", width=25, command=self.handle_register).pack(pady=10)
        
        tk.Button(self.frame, text="Already have an account? Login", font=FONTS["body"], 
                  bg=COLORS["background"], bd=0, fg=COLORS["secondary"], 
                  command=self.show_login).pack()

    def handle_login(self):
        u = self.user_entry.get()
        p = self.pass_entry.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            user_data = self.db.fetch_one("SELECT id, username, role FROM users WHERE username=? AND password=?", (u, p))
            if user_data:
                self.on_login_success(user_data)
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred while connecting to the database:\n{e}")

    def handle_register(self):
        u = self.reg_user.get()
        p = self.reg_pass.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            self.db.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
            messagebox.showinfo("Success", "Account created! Please login.")
            self.show_login()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "Username already exists. Please choose a different one.")
            else:
                messagebox.showerror("Database Error", f"An error occurred while creating your account:\n{e}")
