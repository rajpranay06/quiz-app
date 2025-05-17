from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from ..forms import QuizForm, QuestionForm, OptionFormSet
from ..models import Quiz, Question, Option
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
    # Ensure only the quiz creator can add questions
    if request.user != quiz.creator:
        messages.error(request, "You are not allowed to add questions to this quiz.")
        return redirect('lobby')
    
    if request.method == "POST":
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            # Process formset data manually since we didn't create the question yet when rendering
            option_count = int(request.POST.get('option_count', 0))
            has_correct = False
            
            for i in range(option_count):
                option_text = request.POST.get(f'option_text_{i}')
                is_correct = request.POST.get(f'is_correct_{i}') == 'on'
                
                if option_text:  # Only create options that have text
                    Option.objects.create(
                        question=question,
                        text=option_text if option_text.strip() else f"Option {i + 1}",
                        is_correct=is_correct
                    )
                    
                    if is_correct:
                        has_correct = True
            
            # Ensure at least one option is marked as correct
            if not has_correct and option_count > 0:
                messages.warning(request, "No correct answer was selected. The first option has been set as correct.")
                first_option = question.options.first()
                if first_option:
                    first_option.is_correct = True
                    first_option.save()
            
            if 'complete_quiz' in request.POST:
                return redirect('lobby')
            else:
                return redirect('add_questions', quiz_id=quiz.id)  # Reload to add another question

    else:
        question_form = QuestionForm()

    return render(request, 'base/add_questions.html', {
        "quiz": quiz, 
        "question_form": question_form,
    })
    
    