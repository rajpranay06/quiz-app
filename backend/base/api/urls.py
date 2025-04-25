from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name='api-routes'),
    
    # Quiz routes
    path('quizzes/', views.getQuizzes, name='quizzes'),
    path('quizzes/<int:pk>/', views.getQuiz, name='quiz-detail'),
    path('quizzes/create/', views.createQuiz, name='create-quiz'),
    path('quizzes/<int:pk>/update/', views.updateQuiz, name='update-quiz'),
    path('quizzes/<int:pk>/delete/', views.deleteQuiz, name='delete-quiz'),
    path('quizzes/<int:pk>/questions/', views.getQuizQuestions, name='quiz-questions'),
    path('quizzes/<int:pk>/add-question/', views.addQuestion, name='add-question'),
    path('quizzes/<int:pk>/submit/', views.submitQuiz, name='submit-quiz'),
    path('quizzes/<int:pk>/statistics/', views.getQuizStatistics, name='quiz-statistics'),
    
    # Question routes
    path('questions/', views.getQuestions, name='questions'),
    path('questions/<int:pk>/', views.getQuestion, name='question-detail'),
    path('questions/<int:pk>/update/', views.updateQuestion, name='update-question'),
    path('questions/<int:pk>/delete/', views.deleteQuestion, name='delete-question'),
    path('questions/<int:pk>/add-option/', views.addOption, name='add-option'),
    
    # User stats routes
    path('user-stats/', views.getUserStats, name='user-stats'),
    path('user-stats/summary/', views.getUserStatsSummary, name='user-stats-summary'),
    
    # Join quiz
    path('join-quiz/', views.joinQuiz, name='join-quiz'),
] 