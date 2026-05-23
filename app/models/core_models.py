class User:
    def __init__(self, user_id, username, role='user'):
        self.user_id = user_id
        self.username = username
        self.role = role

    def __str__(self):
        return f"User({self.username}, {self.role})"

class Question:
    def __init__(self, q_id, category, difficulty, text, options, correct_option):
        self.q_id = q_id
        self.category = category
        self.difficulty = difficulty
        self.text = text
        self.options = options  # Expecting a list or dict of options
        self.correct_option = correct_option

    def is_correct(self, selected_option):
        return selected_option.upper() == self.correct_option.upper()
