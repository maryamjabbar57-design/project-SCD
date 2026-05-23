import tkinter as tk
from tkinter import messagebox
from app.gui.styles import COLORS, FONTS
import threading
import time

class QuizScreen:
    def __init__(self, parent, user, category, difficulty, questions, on_complete):
        self.parent = parent
        self.user = user
        self.category = category
        self.difficulty = difficulty
        self.questions = questions
        self.on_complete = on_complete
        
        self.current_q_index = 0
        self.score = 0
        self.correct_count = 0
        self.timer_running = False
        self.remaining_time = 15 # 15 seconds per question
        
        self.frame = tk.Frame(parent, bg=COLORS["background"])
        self.frame.pack(fill="both", expand=True)
        
        self.setup_ui()
        self.load_question()

    def setup_ui(self):
        # Header with Timer
        header = tk.Frame(self.frame, bg=COLORS["primary"], height=60)
        header.pack(fill="x")
        
        tk.Label(header, text=f"Category: {self.category}", bg=COLORS["primary"], 
                 fg="white", font=FONTS["body"]).pack(side="left", padx=20)
        
        self.timer_label = tk.Label(header, text="Time: 15s", bg=COLORS["primary"], 
                                   fg="white", font=FONTS["timer"])
        self.timer_label.pack(side="right", padx=20)

        # Question Area
        self.q_container = tk.Frame(self.frame, bg=COLORS["white"], padx=40, pady=40)
        self.q_container.pack(pady=40, padx=40, fill="both")

        self.q_label = tk.Label(self.q_container, text="", font=FONTS["h2"], 
                                bg=COLORS["white"], wraplength=500, justify="left")
        self.q_label.pack(pady=(0, 30))

        self.options_var = tk.StringVar(value="")
        self.option_buttons = []
        for i in range(4):
            btn = tk.Radiobutton(self.q_container, text="", variable=self.options_var, 
                                 value="", font=FONTS["body"], bg=COLORS["white"],
                                 activebackground=COLORS["white"], indicatoron=0,
                                 width=50, anchor="w", padx=20, pady=10,
                                 selectcolor=COLORS["accent"])
            btn.pack(pady=5)
            self.option_buttons.append(btn)

        self.next_btn = tk.Button(self.frame, text="Next Question", font=FONTS["button"],
                                 bg=COLORS["primary"], fg="white", width=20,
                                 command=self.submit_answer)
        self.next_btn.pack(pady=20)

    def load_question(self):
        if self.current_q_index < len(self.questions):
            q = self.questions[self.current_q_index]
            self.q_label.config(text=f"Q{self.current_q_index+1}: {q[3]}")
            
            options = [q[4], q[5], q[6], q[7]]
            values = ['A', 'B', 'C', 'D']
            
            for i in range(4):
                self.option_buttons[i].config(text=options[i], value=values[i])
            
            self.options_var.set("")
            self.start_timer()
        else:
            self.finish_quiz()

    def start_timer(self):
        self.remaining_time = 15
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.frame.winfo_exists(): return
        if self.timer_running and self.remaining_time >= 0:
            self.timer_label.config(text=f"Time: {self.remaining_time}s")
            if self.remaining_time == 0:
                self.timer_running = False
                messagebox.showinfo("Time's Up!", "Moving to next question...")
                self.submit_answer(auto=True)
            else:
                self.remaining_time -= 1
                self.parent.after(1000, self.update_timer)

    def submit_answer(self, auto=False):
        self.timer_running = False
        selected = self.options_var.get()
        correct = self.questions[self.current_q_index][8]
        
        if not auto and not selected:
            messagebox.showwarning("Warning", "Please select an answer")
            self.timer_running = True
            self.update_timer()
            return

        if selected == correct:
            self.correct_count += 1
            points = 10 if self.difficulty == 'Easy' else (20 if self.difficulty == 'Medium' else 30)
            self.score += points

        self.current_q_index += 1
        self.load_question()

    def finish_quiz(self):
        self.timer_running = False
        self.frame.destroy()
        self.on_complete(self.score, self.correct_count, len(self.questions), self.category, self.difficulty)
