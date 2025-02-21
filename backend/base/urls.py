from django.urls import path
from .service import loginService, logoutService, registerService, homePage, createQuiz, quizService, lobbyPage

urlpatterns = [
    path("login/", loginService.loginPage, name="login"),
    path("logout/", logoutService.logoutUser, name="logout"),
    path("register/", registerService.registerPage, name="register"),
    
    path("create-quiz/", createQuiz.create_quiz, name="create_quiz"),
    path('add_questions/<int:quiz_id>/', createQuiz.add_questions, name='add_questions'),
    path("quiz/", quizService.quizGame, name="quiz"),
    
    path('join_quiz/', quizService.join_quiz, name='join_quiz'),
    path('play_quiz/<int:quiz_id>/', quizService.play_quiz, name='play_quiz'),  # Make sure this exists!
    path('submit_quiz/<int:quiz_id>/', quizService.submit_quiz, name='submit_quiz'),

    path('lobby/', lobbyPage.lobby, name="lobby"),
    path('', homePage.home, name='home'),
]
