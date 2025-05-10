import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Quiz, Question, Option, QuizAttempt, UserAnswer

# Simple test to verify pytest is working
def test_simple_assert():
    """A simple test that should always pass."""
    assert True

# Simple direct test of models
@pytest.mark.django_db
def test_create_quiz_direct():
    """Test creating a quiz directly."""
    user = User.objects.create_user('testuser', 'test@example.com', 'password')
    quiz = Quiz.objects.create(title='Direct Test Quiz', description='Test', creator=user)
    assert quiz.title == 'Direct Test Quiz'
    assert Quiz.objects.filter(title='Direct Test Quiz').exists()

@pytest.fixture
def api_client():
    """Create an API client for testing API views."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def quiz(user):
    """Create a test quiz."""
    return Quiz.objects.create(
        title='Test Quiz',
        description='This is a test quiz',
        creator=user
    )


@pytest.fixture
def question(quiz):
    """Create a test question for the quiz."""
    return Question.objects.create(
        quiz=quiz,
        text='What is the capital of France?'
    )


@pytest.fixture
def options(question):
    """Create options for the test question."""
    options = [
        Option.objects.create(question=question, text='Paris', is_correct=True),
        Option.objects.create(question=question, text='London', is_correct=False),
        Option.objects.create(question=question, text='Berlin', is_correct=False),
        Option.objects.create(question=question, text='Madrid', is_correct=False)
    ]
    return options


@pytest.fixture
def another_user():
    """Create another test user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpassword'
    )


# Test for Routes list
@pytest.mark.django_db
def test_get_routes(api_client):
    url = reverse('api-routes')
    response = api_client.get(url)
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) > 0


# Quiz API Tests
@pytest.mark.django_db
def test_get_quizzes(authenticated_client, quiz):
    url = reverse('quizzes')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['title'] == 'Test Quiz'


@pytest.mark.django_db
def test_get_quiz_detail(authenticated_client, quiz, question, options):
    url = reverse('quiz-detail', args=[quiz.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.data['title'] == 'Test Quiz'
    assert len(response.data['questions']) == 1
    assert response.data['questions'][0]['text'] == 'What is the capital of France?'
    assert len(response.data['questions'][0]['options']) == 4


@pytest.mark.django_db
def test_create_quiz(authenticated_client):
    url = reverse('create-quiz')
    data = {
        'title': 'New Quiz',
        'description': 'This is a new quiz'
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['title'] == 'New Quiz'
    assert Quiz.objects.filter(title='New Quiz').exists()


@pytest.mark.django_db
def test_update_quiz(authenticated_client, quiz):
    url = reverse('update-quiz', args=[quiz.id])
    data = {
        'title': 'Updated Quiz',
        'description': 'This quiz has been updated'
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == 200
    assert response.data['title'] == 'Updated Quiz'
    quiz.refresh_from_db()
    assert quiz.title == 'Updated Quiz'


@pytest.mark.django_db
def test_delete_quiz(authenticated_client, quiz):
    url = reverse('delete-quiz', args=[quiz.id])
    response = authenticated_client.delete(url)
    assert response.status_code == 204
    assert not Quiz.objects.filter(id=quiz.id).exists()


@pytest.mark.django_db
def test_unauthorized_update_quiz(authenticated_client, another_user):
    # Create a quiz owned by another user
    quiz = Quiz.objects.create(
        title='Another User Quiz',
        description='This quiz belongs to another user',
        creator=another_user
    )
    
    url = reverse('update-quiz', args=[quiz.id])
    data = {
        'title': 'Trying to Update',
        'description': 'Should not work'
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == 403
    quiz.refresh_from_db()
    assert quiz.title == 'Another User Quiz'  # Title should not change


@pytest.mark.django_db
def test_get_quiz_questions(authenticated_client, quiz, question, options):
    url = reverse('quiz-questions', args=[quiz.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['text'] == 'What is the capital of France?'
    assert len(response.data[0]['options']) == 4


@pytest.mark.django_db
def test_add_question_to_quiz(authenticated_client, quiz):
    url = reverse('add-question', args=[quiz.id])
    data = {
        'text': 'What is the largest planet in our solar system?',
        'options': [
            {'text': 'Jupiter', 'is_correct': True},
            {'text': 'Saturn', 'is_correct': False},
            {'text': 'Earth', 'is_correct': False},
            {'text': 'Mars', 'is_correct': False}
        ]
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['text'] == 'What is the largest planet in our solar system?'
    assert Question.objects.filter(quiz=quiz, text='What is the largest planet in our solar system?').exists()


@pytest.mark.django_db
def test_submit_quiz(authenticated_client, quiz, question, options):
    url = reverse('submit-quiz', args=[quiz.id])
    data = {
        'quiz_id': quiz.id,
        'answers': [
            {str(question.id): [options[0].id]}  # Correct answer
        ]
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 200
    assert response.data['score'] == 100
    assert response.data['correct_answers'] == 1
    assert QuizAttempt.objects.filter(quiz=quiz).exists()


@pytest.mark.django_db
def test_get_quiz_statistics(authenticated_client, quiz, question, options, user):
    # Create a quiz attempt
    quiz_attempt = QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        score=75,
        attempts=1
    )
    
    url = reverse('quiz-statistics', args=[quiz.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.data['total_attempts'] == 1
    assert response.data['average_score'] > 0


# Question API Tests
@pytest.mark.django_db
def test_get_questions(authenticated_client, question):
    url = reverse('questions')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['text'] == 'What is the capital of France?'


@pytest.mark.django_db
def test_get_questions_by_quiz(authenticated_client, quiz, question):
    url = f"{reverse('questions')}?quiz_id={quiz.id}"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['text'] == 'What is the capital of France?'


@pytest.mark.django_db
def test_get_question_detail(authenticated_client, question, options):
    url = reverse('question-detail', args=[question.id])
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.data['text'] == 'What is the capital of France?'
    assert len(response.data['options']) == 4


@pytest.mark.django_db
def test_update_question(authenticated_client, question):
    url = reverse('update-question', args=[question.id])
    data = {
        'text': 'What is the capital of Italy?'
    }
    response = authenticated_client.put(url, data, format='json')
    assert response.status_code == 200
    assert response.data['text'] == 'What is the capital of Italy?'
    question.refresh_from_db()
    assert question.text == 'What is the capital of Italy?'


@pytest.mark.django_db
def test_delete_question(authenticated_client, question):
    url = reverse('delete-question', args=[question.id])
    response = authenticated_client.delete(url)
    assert response.status_code == 204
    assert not Question.objects.filter(id=question.id).exists()


@pytest.mark.django_db
def test_add_option_to_question(authenticated_client, question):
    url = reverse('add-option', args=[question.id])
    data = {
        'text': 'Rome',
        'is_correct': False
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['text'] == 'Rome'
    assert Option.objects.filter(question=question, text='Rome').exists()


# User Stats API Tests
@pytest.mark.django_db
def test_get_user_stats(authenticated_client, quiz, user):
    # Create a quiz attempt for the user
    QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        score=85,
        attempts=1
    )
    
    url = reverse('user-stats')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['score'] == 85


@pytest.mark.django_db
def test_get_user_stats_summary(authenticated_client, quiz, user):
    # Create a quiz attempt for the user
    QuizAttempt.objects.create(
        user=user,
        quiz=quiz,
        score=85,
        attempts=1
    )
    
    url = reverse('user-stats-summary')
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response.data['total_quizzes_taken'] == 1
    assert response.data['average_score'] == 85


# Join Quiz API Test
@pytest.mark.django_db
def test_join_quiz(authenticated_client, quiz):
    url = reverse('join-quiz')
    data = {
        'code': str(quiz.id)
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 200
    assert response.data['quiz_id'] == quiz.id
    assert response.data['title'] == 'Test Quiz'


@pytest.mark.django_db
def test_join_quiz_invalid_code(authenticated_client):
    url = reverse('join-quiz')
    data = {
        'code': '9999'  # Assuming this ID doesn't exist
    }
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == 404
    assert 'detail' in response.data


