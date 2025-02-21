from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Quiz
from ..forms import JoinQuizForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# API - http://127.0.0.1:8000/home/  (GET request)
 
def quizGame(request):
    return render(request, 'base/home.html', {})



@api_view(['GET' , 'POST'])
@login_required
def join_quiz(request):
    if request.method == "POST":
        form = JoinQuizForm(request.POST)
        if form.is_valid():
            quiz_id = form.cleaned_data['quiz_id']
            
            # Check if the quiz exists
            quiz = Quiz.objects.filter(id=quiz_id).first()
            
            if quiz:
                return redirect('play_quiz', quiz_id=quiz.id)  # Redirect to the quiz page
            else:
                messages.error(request, "Quiz ID not found. Please enter a valid ID.")

    else:
        form = JoinQuizForm()

    return render(request, 'base/join_quiz.html', {"form": form})

@login_required
def play_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()  # Fetch all related questions

    return render(request, 'base/play_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    score = 0
    total_questions = questions.count()

    if request.method == "POST":
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1

        return render(request, 'base/quiz_result.html', {'quiz': quiz, 'score': score, 'total': total_questions})

    return render(request, 'base/play_quiz.html', {'quiz': quiz, 'questions': questions})