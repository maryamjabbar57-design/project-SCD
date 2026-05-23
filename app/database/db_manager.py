import sqlite3
import os
import sys

class DatabaseError(Exception):
    """Custom exception for database-related errors in the application."""
    pass

class DatabaseManager:
    def __init__(self, db_name="quiz_game.db"):
        """
        Initializes the DatabaseManager.
        Supports ':memory:' for isolated testing.
        """
        self.db_name = db_name
        if db_name == ":memory:":
            self.db_path = db_name
            # For in-memory DB, keep a single persistent connection so that
            # tables and schema persist across queries in unit tests.
            self.conn = sqlite3.connect(db_name)
        else:
            self.db_path = os.path.join(os.path.dirname(__file__), db_name)
            self.conn = None
        self.init_db()

    def get_connection(self):
        if self.db_name == ":memory:":
            return self.conn
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}") from e

    def close_connection(self, conn):
        # Do not close connection if it's the persistent in-memory connection
        if self.db_name != ":memory:" and conn:
            conn.close()

    def init_db(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )
            ''')
            
            # Questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_option TEXT NOT NULL
                )
            ''')
            
            # Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    score INTEGER,
                    total_questions INTEGER,
                    category TEXT,
                    difficulty TEXT,
                    date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Add a default admin if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               ('admin', 'admin123', 'admin'))
            
            # Add some sample questions if empty
            cursor.execute("SELECT COUNT(*) FROM questions")
            if cursor.fetchone()[0] == 0:
                sample_questions = [
                    ('Science', 'Easy', 'What is the chemical symbol for water?', 'H2O', 'CO2', 'O2', 'NaCl', 'A'),
                    ('Science', 'Medium', 'What planet is known as the Red Planet?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'B'),
                    ('Technology', 'Easy', 'What does CPU stand for?', 'Central Process Unit', 'Central Processing Unit', 'Computer Personal Unit', 'Central Processor Unit', 'B'),
                    ('English', 'Easy', 'What is a synonym for "Happy"?', 'Sad', 'Joyful', 'Angry', 'Tired', 'B'),
                    ('General Knowledge', 'Medium', 'Who painted the Mona Lisa?', 'Van Gogh', 'Picasso', 'Da Vinci', 'Michelangelo', 'C')
                ]
                cursor.executemany('''
                    INSERT INTO questions (category, difficulty, question_text, option_a, option_b, option_c, option_d, correct_option)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_questions)
                
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database initialization failed: {e}") from e
        finally:
            if conn:
                self.close_connection(conn)

    def execute_query(self, query, params=()):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {query} with params {params}. Error: {e}") from e
        finally:
            if conn:
                self.close_connection(conn)

    def fetch_all(self, query, params=()):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Fetch all failed: {query} with params {params}. Error: {e}") from e
        finally:
            if conn:
                self.close_connection(conn)

    def fetch_one(self, query, params=()):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise DatabaseError(f"Fetch one failed: {query} with params {params}. Error: {e}") from e
        finally:
            if conn:
                self.close_connection(conn)
