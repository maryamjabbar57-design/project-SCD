import unittest
from app.models.logic_managers import ScoreManager, Quiz
from app.models.core_models import Question

class TestQuizLogic(unittest.TestCase):

    def test_score_calculation(self):
        sm = ScoreManager()
        # Easy: 10 points
        sm.record_answer(True, 'Easy')
        self.assertEqual(sm.total_points, 10)
        self.assertEqual(sm.correct_answers, 1)

        # Medium: 20 points, -5 for wrong
        sm.record_answer(True, 'Medium')
        self.assertEqual(sm.total_points, 30)
        
        sm.record_answer(False, 'Medium')
        self.assertEqual(sm.total_points, 25)
        self.assertEqual(sm.wrong_answers, 1)

    def test_grade_generation(self):
        sm = ScoreManager()
        self.assertEqual(sm.generate_grade(95), "A+")
        self.assertEqual(sm.generate_grade(85), "A")
        self.assertEqual(sm.generate_grade(75), "B")
        self.assertEqual(sm.generate_grade(65), "C")
        self.assertEqual(sm.generate_grade(45), "Fail")

    def test_quiz_flow(self):
        q1 = Question(1, "Sci", "Easy", "Q1", ["A", "B", "C", "D"], "A")
        q2 = Question(2, "Sci", "Easy", "Q2", ["A", "B", "C", "D"], "B")
        quiz = Quiz([q1, q2])
        
        self.assertTrue(quiz.has_more_questions())
        nxt = quiz.get_next_question()
        self.assertIn(nxt, [q1, q2])
        
        quiz.get_next_question()
        self.assertFalse(quiz.has_more_questions())

if __name__ == '__main__':
    unittest.main()
