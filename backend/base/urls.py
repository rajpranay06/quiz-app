from django.urls import path
from .service import loginService, logoutService, registerService, homePage, createQuiz, quizService, lobbyPage

urlpatterns = [
    path("login/", loginService.loginPage, name="login"),
    path("logout/", logoutService.logoutUser, name="logout"),
    path("register/", registerService.registerPage, name="register"),

    path("create-quiz/", createQuiz.create_quiz, name="create_quiz"),
    path('add_questions/<int:quiz_id>/', createQuiz.add_questions, name='add_questions'),
    
    path('join_quiz/', quizService.join_quiz, name='join_quiz'),
    path('play_quiz/<int:quiz_id>/', quizService.play_quiz, name='play_quiz'),  
    path('submit_quiz/<int:quiz_id>/', quizService.submit_quiz, name='submit_quiz'),
    path('update_quiz/<int:quiz_id>/', quizService.update_quiz, name='update_quiz'),
    path('lobby/update_quiz_list', quizService.update_quiz_list, name='update_quiz_list'),
    
    path('delete_question/<int:question_id>/', quizService.delete_question, name='delete_question'),
    path('delete_quiz/<int:quiz_id>/', quizService.delete_quiz, name='delete_quiz'),

    path('lobby/', lobbyPage.lobby, name="lobby"),
    path('', homePage.home, name='home'),
]
