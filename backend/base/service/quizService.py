from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Quiz, QuizAttempt, Question, Option, UserAnswer
from ..forms import JoinQuizForm, QuizForm, QuestionForm, OptionForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction


 
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
    questions = quiz.questions.all().prefetch_related('options')

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

        with transaction.atomic():
            # Calculate the score
            for question in questions:
                # Get all submitted answers for this question (handles multiple choice)
                selected_options = request.POST.getlist(f'question_{question.id}')
                correct_options = question.options.filter(is_correct=True).count()
                selected_correct = question.options.filter(id__in=selected_options, is_correct=True).count()
                
                # Create user answer record
                user_answer = UserAnswer.objects.create(
                    quiz_attempt=attempt,
                    question=question
                )
                
                # Add selected options to the user answer
                for option_id in selected_options:
                    option = Option.objects.get(id=option_id)
                    user_answer.selected_options.add(option)
                
                # Full point if all correct options are selected and no incorrect ones
                if selected_correct == correct_options and len(selected_options) == correct_options:
                    score += 1
                # Partial credit for partially correct answers
                elif selected_correct > 0:
                    score += selected_correct / correct_options * 0.5

            # Update the attempt record
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
    questions = quiz.questions.all().prefetch_related('options')
    score = 0
    total_questions = questions.count()

    if request.method == "POST":
        # Create or get quiz attempt
        attempt, created = QuizAttempt.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'attempts': 1, 'score': 0}
        )
        
        if not created:
            attempt.attempts += 1
            
        with transaction.atomic():
            for question in questions:
                # Get all submitted answers for this question (handles multiple choice)
                selected_options = request.POST.getlist(f'question_{question.id}')
                correct_options = question.options.filter(is_correct=True).count()
                selected_correct = question.options.filter(id__in=selected_options, is_correct=True).count()
                
                # Create user answer record
                user_answer = UserAnswer.objects.create(
                    quiz_attempt=attempt,
                    question=question
                )
                
                # Add selected options to the user answer
                for option_id in selected_options:
                    option = Option.objects.get(id=option_id)
                    user_answer.selected_options.add(option)
                
                # Full point if all correct options are selected and no incorrect ones
                if selected_correct == correct_options and len(selected_options) == correct_options:
                    score += 1
                # Partial credit for partially correct answers
                elif selected_correct > 0:
                    score += selected_correct / correct_options * 0.5
            
            attempt.score = score
            attempt.save()

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
                question_text = request.POST.get(f'{question_id}_text')
                
                if question_text:
                    question.text = question_text
                    question.save()
                    
                    # Handle existing options
                    existing_options = list(question.options.all())
                    option_ids = request.POST.getlist(f'{question_id}_option_ids')
                    
                    # First, delete options that are not in the submitted form
                    for option in existing_options:
                        if str(option.id) not in option_ids:
                            option.delete()
                    
                    # Then update or create options
                    for i, option_id in enumerate(option_ids):
                        option_text = request.POST.get(f'{question_id}_option_text_{i}')
                        is_correct = request.POST.get(f'{question_id}_is_correct_{i}') == 'on'
                        
                        if option_id and option_text:  # Update existing option
                            option = Option.objects.get(id=option_id)
                            option.text = option_text
                            option.is_correct = is_correct
                            option.save()
                        elif option_text:  # Create new option
                            Option.objects.create(
                                question=question,
                                text=option_text,
                                is_correct=is_correct
                            )

            # Add new questions
            new_questions_count = int(request.POST.get('new_questions_count', 0))
            for i in range(1, new_questions_count + 1):
                text = request.POST.get(f'new_question_{i}_text')
                
                if text:
                    new_question = Question.objects.create(
                        quiz=quiz,
                        text=text
                    )
                    
                    # Add options for this new question
                    option_count = int(request.POST.get(f'new_question_{i}_option_count', 0))
                    for j in range(option_count):
                        option_text = request.POST.get(f'new_question_{i}_option_text_{j}')
                        is_correct = request.POST.get(f'new_question_{i}_is_correct_{j}') == 'on'
                        
                        if option_text:
                            Option.objects.create(
                                question=new_question,
                                text=option_text,
                                is_correct=is_correct
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