import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.styles import COLORS, FONTS

class Dashboard:
    def __init__(self, parent, user, db_manager, on_start_quiz, on_logout):
        self.parent = parent
        self.user = user  # (id, username, role)
        self.db = db_manager
        self.on_start_quiz = on_start_quiz
        self.on_logout = on_logout
        
        self.frame = tk.Frame(parent, bg=COLORS["background"])
        self.frame.pack(fill="both", expand=True)
        
        self.setup_ui()

    def setup_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.frame, bg=COLORS["secondary"], width=200)
        sidebar.pack(side="left", fill="y")
        
        tk.Label(sidebar, text=f"Hi, {self.user[1]}", font=FONTS["h2"], 
                 bg=COLORS["secondary"], fg="white").pack(pady=30)
        
        tk.Button(sidebar, text="New Quiz", font=FONTS["body"], bg=COLORS["secondary"], 
                  fg="white", bd=0, command=self.show_new_quiz).pack(fill="x", pady=5)
        
        tk.Button(sidebar, text="History", font=FONTS["body"], bg=COLORS["secondary"], 
                  fg="white", bd=0, command=self.show_history).pack(fill="x", pady=5)
        
        if self.user[2] == 'admin':
            tk.Button(sidebar, text="Admin Panel", font=FONTS["body"], bg=COLORS["secondary"], 
                      fg="white", bd=0, command=self.show_admin_panel).pack(fill="x", pady=5)

        tk.Button(sidebar, text="Logout", font=FONTS["body"], bg=COLORS["error"], 
                  fg="white", bd=0, command=self.on_logout).pack(side="bottom", fill="x", pady=20)

        # Main Content Area
        self.content = tk.Frame(self.frame, bg=COLORS["background"], padx=40, pady=40)
        self.content.pack(side="right", fill="both", expand=True)
        
        self.show_new_quiz()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_new_quiz(self):
        self.clear_content()
        tk.Label(self.content, text="Start a New Quiz", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 30))
        
        form = tk.Frame(self.content, bg=COLORS["white"], padx=30, pady=30)
        form.pack()

        tk.Label(form, text="Select Category", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        categories = ["Science", "Technology", "English", "General Knowledge"]
        self.cat_var = tk.StringVar(value=categories[0])
        ttk.Combobox(form, textvariable=self.cat_var, values=categories, state="readonly", width=30).pack(pady=(5, 15))

        tk.Label(form, text="Select Difficulty", font=FONTS["body"], bg=COLORS["white"]).pack(anchor="w")
        levels = ["Easy", "Medium", "Hard"]
        self.diff_var = tk.StringVar(value=levels[0])
        ttk.Combobox(form, textvariable=self.diff_var, values=levels, state="readonly", width=30).pack(pady=(5, 25))

        tk.Button(form, text="Start Quiz", font=FONTS["button"], bg=COLORS["primary"], 
                  fg="white", width=20, command=self.handle_start).pack()

    def handle_start(self):
        cat = self.cat_var.get()
        diff = self.diff_var.get()
        
        questions = self.db.fetch_all("SELECT * FROM questions WHERE category=? AND difficulty=?", (cat, diff))
        if not questions:
            messagebox.showwarning("Empty", f"No questions found for {cat} ({diff})")
            return
        
        self.frame.destroy()
        self.on_start_quiz(cat, diff, questions)

    def show_history(self):
        self.clear_content()
        tk.Label(self.content, text="Your Performance History", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 30))
        
        history = self.db.fetch_all("SELECT score, total_questions, category, difficulty, date_taken FROM results WHERE user_id=? ORDER BY date_taken DESC", (self.user[0],))
        
        if not history:
            tk.Label(self.content, text="No history found. Take a quiz first!", bg=COLORS["background"]).pack()
            return

        tree = ttk.Treeview(self.content, columns=("Score", "Total", "Category", "Diff", "Date"), show="headings")
        tree.heading("Score", text="Score")
        tree.heading("Total", text="Total Qs")
        tree.heading("Category", text="Category")
        tree.heading("Diff", text="Difficulty")
        tree.heading("Date", text="Date")
        
        for col in ("Score", "Total", "Category", "Diff", "Date"):
            tree.column(col, width=100, anchor="center")
        
        for row in history:
            tree.insert("", "end", values=row)
        
        tree.pack(fill="both", expand=True)

    def show_admin_panel(self):
        self.clear_content()
        tk.Label(self.content, text="Admin Management", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=(0, 20))
        
        btn_frame = tk.Frame(self.content, bg=COLORS["background"])
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="Add New Question", font=FONTS["body"], bg=COLORS["success"], fg="white", 
                  padx=15, command=self.show_add_question_dialog).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Delete Selected", font=FONTS["body"], bg=COLORS["error"], fg="white",
                  padx=15, command=self.delete_selected_question).pack(side="left", padx=10)

        questions = self.db.fetch_all("SELECT id, category, difficulty, question_text FROM questions")
        
        self.admin_tree = ttk.Treeview(self.content, columns=("ID", "Cat", "Diff", "Text"), show="headings")
        self.admin_tree.heading("ID", text="ID")
        self.admin_tree.heading("Cat", text="Category")
        self.admin_tree.heading("Diff", text="Diff")
        self.admin_tree.heading("Text", text="Question")
        
        self.admin_tree.column("ID", width=50, anchor="center")
        self.admin_tree.column("Cat", width=100, anchor="center")
        self.admin_tree.column("Diff", width=80, anchor="center")
        self.admin_tree.column("Text", width=400, anchor="w")
        
        for q in questions:
            self.admin_tree.insert("", "end", values=q)
        
        self.admin_tree.pack(fill="both", expand=True, pady=10)

    def delete_selected_question(self):
        selected_item = self.admin_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a question to delete")
            return
        
        item = self.admin_tree.item(selected_item)
        q_id = item['values'][0]
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Question ID {q_id}?")
        if confirm:
            try:
                self.db.execute_query("DELETE FROM questions WHERE id=?", (q_id,))
                messagebox.showinfo("Success", "Question deleted successfully")
                self.show_admin_panel()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete question:\n{e}")

    def show_add_question_dialog(self):
        popup = tk.Toplevel(self.parent)
        popup.title("Add Question")
        popup.geometry("520x620")
        popup.configure(bg=COLORS["white"])
        popup.transient(self.parent)
        popup.grab_set()

        tk.Label(popup, text="Add New Question", font=FONTS["h2"], bg=COLORS["white"], fg=COLORS["primary"]).pack(pady=15)
        
        form_frame = tk.Frame(popup, bg=COLORS["white"], padx=20)
        form_frame.pack(fill="both", expand=True)
        
        # Category
        tk.Label(form_frame, text="Category:", font=FONTS["body"], bg=COLORS["white"]).grid(row=0, column=0, sticky="w", pady=5)
        categories = ["Science", "Technology", "English", "General Knowledge"]
        cat_var = tk.StringVar(value=categories[0])
        cat_combo = ttk.Combobox(form_frame, textvariable=cat_var, values=categories, state="readonly", width=30)
        cat_combo.grid(row=0, column=1, pady=5, sticky="w")
        
        # Difficulty
        tk.Label(form_frame, text="Difficulty:", font=FONTS["body"], bg=COLORS["white"]).grid(row=1, column=0, sticky="w", pady=5)
        levels = ["Easy", "Medium", "Hard"]
        diff_var = tk.StringVar(value=levels[0])
        diff_combo = ttk.Combobox(form_frame, textvariable=diff_var, values=levels, state="readonly", width=30)
        diff_combo.grid(row=1, column=1, pady=5, sticky="w")
        
        # Question Text
        tk.Label(form_frame, text="Question Text:", font=FONTS["body"], bg=COLORS["white"]).grid(row=2, column=0, sticky="nw", pady=5)
        q_text = tk.Text(form_frame, width=35, height=4, font=("Helvetica", 10))
        q_text.grid(row=2, column=1, pady=5, sticky="w")
        
        # Options A, B, C, D
        tk.Label(form_frame, text="Option A:", font=FONTS["body"], bg=COLORS["white"]).grid(row=3, column=0, sticky="w", pady=5)
        opt_a = tk.Entry(form_frame, width=40, font=("Helvetica", 10))
        opt_a.grid(row=3, column=1, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Option B:", font=FONTS["body"], bg=COLORS["white"]).grid(row=4, column=0, sticky="w", pady=5)
        opt_b = tk.Entry(form_frame, width=40, font=("Helvetica", 10))
        opt_b.grid(row=4, column=1, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Option C:", font=FONTS["body"], bg=COLORS["white"]).grid(row=5, column=0, sticky="w", pady=5)
        opt_c = tk.Entry(form_frame, width=40, font=("Helvetica", 10))
        opt_c.grid(row=5, column=1, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Option D:", font=FONTS["body"], bg=COLORS["white"]).grid(row=6, column=0, sticky="w", pady=5)
        opt_d = tk.Entry(form_frame, width=40, font=("Helvetica", 10))
        opt_d.grid(row=6, column=1, pady=5, sticky="w")
        
        # Correct Option
        tk.Label(form_frame, text="Correct Option:", font=FONTS["body"], bg=COLORS["white"]).grid(row=7, column=0, sticky="w", pady=5)
        correct_var = tk.StringVar(value="A")
        correct_combo = ttk.Combobox(form_frame, textvariable=correct_var, values=["A", "B", "C", "D"], state="readonly", width=10)
        correct_combo.grid(row=7, column=1, pady=5, sticky="w")
        
        # Action Buttons
        def save_question():
            cat = cat_var.get()
            diff = diff_var.get()
            text = q_text.get("1.0", "end-1c").strip()
            oa = opt_a.get().strip()
            ob = opt_b.get().strip()
            oc = opt_c.get().strip()
            od = opt_d.get().strip()
            corr = correct_var.get()
            
            if not text or not oa or not ob or not oc or not od:
                messagebox.showerror("Validation Error", "All fields are required.", parent=popup)
                return
                
            try:
                self.db.execute_query(
                    "INSERT INTO questions (category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (cat, diff, text, oa, ob, oc, od, corr)
                )
                messagebox.showinfo("Success", "Question added successfully!", parent=popup)
                popup.destroy()
                self.show_admin_panel()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save question:\n{e}", parent=popup)
                
        btn_container = tk.Frame(popup, bg=COLORS["white"])
        btn_container.pack(fill="x", pady=20)
        
        tk.Button(btn_container, text="Save Question", font=FONTS["button"], bg=COLORS["success"], fg="white", width=15, command=save_question).pack(side="left", padx=40)
        tk.Button(btn_container, text="Cancel", font=FONTS["button"], bg=COLORS["error"], fg="white", width=15, command=popup.destroy).pack(side="right", padx=40)
