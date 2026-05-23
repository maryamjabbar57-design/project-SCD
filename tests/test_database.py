import unittest
import sqlite3
from app.database.db_manager import DatabaseManager, DatabaseError

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Initialize in-memory database for clean test isolation
        self.db = DatabaseManager(":memory:")

    def tearDown(self):
        # In-memory database is dropped automatically when connection closes
        pass

    def test_database_initialization(self):
        # Verify tables exist
        tables = self.db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t[0] for t in tables]
        self.assertIn("users", table_names)
        self.assertIn("questions", table_names)
        self.assertIn("results", table_names)

        # Verify admin user was created
        admin = self.db.fetch_one("SELECT username, role FROM users WHERE username='admin'")
        self.assertIsNotNone(admin)
        self.assertEqual(admin[0], "admin")
        self.assertEqual(admin[1], "admin")

        # Verify default questions were populated
        questions_count = self.db.fetch_one("SELECT COUNT(*) FROM questions")[0]
        self.assertEqual(questions_count, 5)

    def test_user_creation_and_auth(self):
        # Register a new user
        self.db.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("testuser", "pass123", "user"))
        
        # Verify credentials
        user = self.db.fetch_one("SELECT username, role FROM users WHERE username=? AND password=?", ("testuser", "pass123"))
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "testuser")
        self.assertEqual(user[1], "user")

        # Duplicate username constraint test
        with self.assertRaises(DatabaseError):
            self.db.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("testuser", "otherpass", "user"))

    def test_question_operations(self):
        # Insert a question
        self.db.execute_query(
            "INSERT INTO questions (category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("Science", "Hard", "What is quantum entanglement?", "A", "B", "C", "D", "A")
        )
        
        # Retrieve question
        questions = self.db.fetch_all("SELECT * FROM questions WHERE category=? AND difficulty=?", ("Science", "Hard"))
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0][3], "What is quantum entanglement?")

        # Delete question
        q_id = questions[0][0]
        self.db.execute_query("DELETE FROM questions WHERE id=?", (q_id,))
        
        # Verify deletion
        questions_after = self.db.fetch_all("SELECT * FROM questions WHERE category=? AND difficulty=?", ("Science", "Hard"))
        self.assertEqual(len(questions_after), 0)

    def test_results_and_history(self):
        # Register a user
        self.db.execute_query("INSERT INTO users (username, password) VALUES (?, ?)", ("player1", "play123"))
        user_id = self.db.fetch_one("SELECT id FROM users WHERE username=?", ("player1",))[0]

        # Save results
        self.db.execute_query(
            "INSERT INTO results (user_id, score, total_questions, category, difficulty) VALUES (?, ?, ?, ?, ?)",
            (user_id, 40, 5, "Science", "Medium")
        )

        # Retrieve history
        history = self.db.fetch_all("SELECT score, total_questions, category, difficulty FROM results WHERE user_id=?", (user_id,))
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], 40)
        self.assertEqual(history[0][2], "Science")

    def test_database_error_handling(self):
        # Verify query errors are caught and re-raised as DatabaseError
        with self.assertRaises(DatabaseError):
            # Invalid SQL syntax
            self.db.execute_query("SELECT * FROM non_existent_table")

        with self.assertRaises(DatabaseError):
            # Invalid SQL column names
            self.db.fetch_one("SELECT dummy_column FROM users")

if __name__ == "__main__":
    unittest.main()
