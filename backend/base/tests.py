from django.test import TestCase
from django.contrib.auth.models import User
from .models import Quiz, Question, QuizAttempt

class QuizModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.quiz = Quiz.objects.create(title="Sample Quiz", description="A test quiz", creator=self.user)

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, "Sample Quiz")
        self.assertEqual(self.quiz.description, "A test quiz")
        self.assertEqual(self.quiz.creator.username, "testuser")


class QuestionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.quiz = Quiz.objects.create(title="Sample Quiz", description="A test quiz", creator=self.user)
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            option1="1",
            option2="2",
            option3="3",
            option4="4",
            correct_option=4
        )

    def test_question_creation(self):
        self.assertEqual(self.question.text, "What is 2+2?")
        self.assertEqual(self.question.quiz.title, "Sample Quiz")
        self.assertEqual(self.question.correct_option, 4)


class QuizAttemptModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.quiz = Quiz.objects.create(title="Sample Quiz", description="A test quiz", creator=self.user)
        self.quiz_attempt = QuizAttempt.objects.create(user=self.user, quiz=self.quiz, score=80, attempts=1)

    def test_quiz_attempt_creation(self):
        self.assertEqual(self.quiz_attempt.user.username, "testuser")
        self.assertEqual(self.quiz_attempt.quiz.title, "Sample Quiz")
        self.assertEqual(self.quiz_attempt.score, 80)
        self.assertEqual(self.quiz_attempt.attempts, 1)

    def test_unique_quiz_attempt(self):
        with self.assertRaises(Exception):
            QuizAttempt.objects.create(user=self.user, quiz=self.quiz, score=90, attempts=2)


