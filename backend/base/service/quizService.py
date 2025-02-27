from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Quiz, QuizAttempt, Question
from ..forms import JoinQuizForm, QuizForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


 
@api_view(['GET' , 'POST'])
@login_required
def join_quiz(request):
    # Fetch all quizzes
    quizzes = Quiz.objects.all()

    if request.method == "POST":
        # Get the selected quiz ID from the form
        quiz_id = request.POST.get('quiz_id')
        
        if quiz_id:
            # Check if the quiz exists
            quiz = Quiz.objects.filter(id=quiz_id).first()
            
            if quiz:
                return redirect('play_quiz', quiz_id=quiz.id)  # Redirect to the quiz page
            else:
                messages.error(request, "Quiz not found. Please select a valid quiz.")
        else:
            messages.error(request, "Please select a quiz to join.")

    # Render the join quiz page with the list of quizzes
    return render(request, 'base/join_quiz.html', {"quizzes": quizzes})

@login_required
def play_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    # Check if the user has already attempted the quiz
    attempt, created = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz,
        defaults={'attempts': 0, 'score': 0}  # Initialize with default values
    )

    # Prevent the user from retaking the quiz
    if attempt.attempts >= 1:
        messages.error(request, "You have already taken this quiz!")
        return redirect('lobby')

    # Handle quiz submission
    if request.method == "POST":
        score = 0
        total_questions = questions.count()

        # Calculate the score
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1

        # Update the attempt record properly
        attempt.attempts = 1  # Update the number of attempts
        attempt.score = score  # Update the score
        attempt.save()  # Save the updated attempt object

        # Render result page
        return render(request, 'base/quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total_questions
        })

    # Render the quiz page with questions
    return render(request, 'base/play_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

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


@login_required
def update_quiz_list(request):
    quizzes = Quiz.objects.filter(creator=request.user)
    return render(request, 'base/update_quiz_list.html', {'quizzes': quizzes})


@login_required
def update_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Ensure only the creator can update the quiz
    if request.user != quiz.creator:
        return HttpResponseForbidden("You are not allowed to edit this quiz.")

    # Handle form submission
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST, instance=quiz)

        if quiz_form.is_valid():
            quiz_form.save()

            # Update existing questions
            for question in quiz.questions.all():
                question_id = f'question_{question.id}'
                option1 = request.POST.get(f'{question_id}_option1')
                option2 = request.POST.get(f'{question_id}_option2')
                option3 = request.POST.get(f'{question_id}_option3')
                option4 = request.POST.get(f'{question_id}_option4')
                correct_option = request.POST.get(f'{question_id}_correct_option')

                if option1 and option2 and option3 and option4 and correct_option:
                    question.option1 = option1
                    question.option2 = option2
                    question.option3 = option3
                    question.option4 = option4
                    question.correct_option = int(correct_option)
                    question.save()

            # Add new questions
            new_questions_count = int(request.POST.get('new_questions_count', 0))
            for i in range(1, new_questions_count + 1):
                text = request.POST.get(f'new_question_{i}_text')
                option1 = request.POST.get(f'new_question_{i}_option1')
                option2 = request.POST.get(f'new_question_{i}_option2')
                option3 = request.POST.get(f'new_question_{i}_option3')
                option4 = request.POST.get(f'new_question_{i}_option4')
                correct_option = request.POST.get(f'new_question_{i}_correct_option')

                if text and option1 and option2 and option3 and option4 and correct_option:
                    Question.objects.create(
                        quiz=quiz,
                        text=text,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        correct_option=int(correct_option)
                    )

            return redirect('lobby')

    else:
        quiz_form = QuizForm(instance=quiz)

    return render(request, 'base/update_quiz.html', {
        'quiz_form': quiz_form,
        'quiz': quiz
    })


@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    
    # Check if the quiz creator is deleting the question
    if request.user != question.quiz.creator:
        messages.error(request, "You can only delete questions from quizzes you created.")
        return redirect('update_quiz', quiz_id=question.quiz.id)

    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('update_quiz', quiz_id=question.quiz.id)

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if the user is the creator
    if request.user != quiz.creator:
        messages.error(request, "You can only delete quizzes you created.")
        return redirect('lobby')

    quiz.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('lobby')