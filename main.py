import tkinter as tk
from app.database.db_manager import DatabaseManager
from app.gui.auth_screens import AuthScreen
from app.gui.dashboard import Dashboard
from app.gui.quiz_screen import QuizScreen
from app.gui.styles import COLORS, FONTS

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Quiz Game")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["background"])
        
        self.db = DatabaseManager()
        self.current_user = None
        
        self.show_auth()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_auth(self):
        self.clear_root()
        AuthScreen(self.root, self.db, self.on_login_success)

    def on_login_success(self, user_data):
        self.current_user = user_data
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_root()
        Dashboard(self.root, self.current_user, self.db, self.start_quiz, self.show_auth)

    def start_quiz(self, category, difficulty, questions):
        self.clear_root()
        QuizScreen(self.root, self.current_user, category, difficulty, questions, self.show_results)

    def show_results(self, score, correct, total, category, difficulty):
        self.clear_root()
        
        # Save result to DB
        self.db.execute_query("INSERT INTO results (user_id, score, total_questions, category, difficulty) VALUES (?, ?, ?, ?, ?)", 
                             (self.current_user[0], score, total, category, difficulty))
        
        percentage = (correct / total) * 100
        grade = "Pass" if percentage >= 50 else "Fail"
        
        frame = tk.Frame(self.root, bg=COLORS["background"])
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Quiz Completed!", font=FONTS["h1"], 
                 bg=COLORS["background"], fg=COLORS["primary"]).pack(pady=50)
        
        res_container = tk.Frame(frame, bg=COLORS["white"], padx=40, pady=40)
        res_container.pack()
        
        tk.Label(res_container, text=f"Correct Answers: {correct}/{total}", 
                 font=FONTS["h2"], bg=COLORS["white"]).pack(pady=5)
        tk.Label(res_container, text=f"Total Score: {score}", 
                 font=FONTS["h2"], bg=COLORS["white"]).pack(pady=5)
        tk.Label(res_container, text=f"Percentage: {percentage:.1f}%", 
                 font=FONTS["h2"], bg=COLORS["white"]).pack(pady=5)
        
        color = COLORS["success"] if grade == "Pass" else COLORS["error"]
        tk.Label(res_container, text=f"Result: {grade}", font=FONTS["h1"], 
                 bg=COLORS["white"], fg=color).pack(pady=20)
        
        tk.Button(frame, text="Back to Dashboard", font=FONTS["button"], 
                  bg=COLORS["primary"], fg="white", width=25, 
                  command=self.show_dashboard).pack(pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
