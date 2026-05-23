import random
import time

class Quiz:
    def __init__(self, questions):
        self.questions = questions
        random.shuffle(self.questions)
        self.current_index = 0
        self.score_manager = ScoreManager()

    def get_next_question(self):
        if self.current_index < len(self.questions):
            question = self.questions[self.current_index]
            self.current_index += 1
            return question
        return None

    def has_more_questions(self):
        return self.current_index < len(self.questions)

class ScoreManager:
    def __init__(self):
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_points = 0

    def record_answer(self, is_correct, difficulty):
        # Points based on difficulty
        points_map = {'Easy': 10, 'Medium': 20, 'Hard': 30}
        points = points_map.get(difficulty, 10)
        
        if is_correct:
            self.correct_answers += 1
            self.total_points += points
        else:
            self.wrong_answers += 1
            # Penalty for wrong answer in Medium/Hard
            if difficulty != 'Easy':
                self.total_points -= 5

    def calculate_percentage(self, total_questions):
        if total_questions == 0: return 0
        return (self.correct_answers / total_questions) * 100

    def generate_grade(self, percentage):
        if percentage >= 90: return "A+"
        elif percentage >= 80: return "A"
        elif percentage >= 70: return "B"
        elif percentage >= 60: return "C"
        elif percentage >= 50: return "D"
        else: return "Fail"

class Timer:
    def __init__(self, duration, callback_on_end):
        self.duration = duration
        self.remaining_time = duration
        self.callback = callback_on_end
        self.running = False

    def start(self, update_ui_callback):
        self.running = True
        while self.remaining_time > 0 and self.running:
            update_ui_callback(self.remaining_time)
            time.sleep(1)
            self.remaining_time -= 1
        
        if self.remaining_time <= 0 and self.running:
            self.callback()

    def stop(self):
        self.running = False

class ResultManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def save_result(self, user_id, score, total, category, difficulty):
        query = "INSERT INTO results (user_id, score, total_questions, category, difficulty) VALUES (?, ?, ?, ?, ?)"
        self.db.execute_query(query, (user_id, score, total, category, difficulty))

    def get_user_history(self, user_id):
        query = "SELECT score, total_questions, category, difficulty, date_taken FROM results WHERE user_id = ? ORDER BY date_taken DESC"
        return self.db.fetch_all(query, (user_id,))

class Admin:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_question(self, category, difficulty, text, options, correct):
        query = "INSERT INTO questions (category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        self.db.execute_query(query, (category, difficulty, text, options[0], options[1], options[2], options[3], correct))

    def update_question(self, q_id, text, options, correct):
        query = "UPDATE questions SET question_text=?, option_a=?, option_b=?, option_c=?, option_d=?, correct_option=? WHERE id=?"
        self.db.execute_query(query, (text, options[0], options[1], options[2], options[3], correct, q_id))

    def delete_question(self, q_id):
        self.db.execute_query("DELETE FROM questions WHERE id=?", (q_id,))
