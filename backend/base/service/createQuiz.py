from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..forms import QuizForm, QuestionForm
from ..models import Quiz
from django.contrib.auth.decorators import login_required

# API - http://127.0.0.1:8000/home/  (GET request)
# @api_view(['POST'])
@login_required
def create_quiz(request):
    if request.method == "POST":
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.creator = request.user
            quiz.save()
            return redirect('add_questions', quiz_id=quiz.id)  # Redirect to add questions

    else:
        quiz_form = QuizForm()

    return render(request, 'base/create_quiz.html', {"quiz_form": quiz_form})

@login_required
def add_questions(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == "POST":
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            return redirect('add_questions', quiz_id=quiz.id)  # Reload to add another question

    else:
        question_form = QuestionForm()

    return render(request, 'base/add_questions.html', {"quiz": quiz, "question_form": question_form})
