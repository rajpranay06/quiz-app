from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Quiz, QuizAttempt, Question, Option, UserAnswer
from ..forms import JoinQuizForm, QuizForm, QuestionForm, OptionForm
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Max, Min, Sum, F, ExpressionWrapper, FloatField, Q
import json
from django.utils import timezone
from datetime import timedelta


 
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

    # Verify options contain text data - fix empty option text if needed
    for question in questions:
        options = list(question.options.all())
        for i, option in enumerate(options):
            if not option.text or option.text.strip() == '':
                option.text = f"Option {i+1}"
                option.save()

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

    # Log the questions and options for debugging
    for question in questions:
        options_data = [{'id': opt.id, 'text': opt.text} for opt in question.options.all()]
        print(f"Question {question.id}: {question.text}")
        print(f"Options: {options_data}")

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

    # Verify options contain text data
    for question in questions:
        options = list(question.options.all())
        for i, option in enumerate(options):
            if not option.text or option.text.strip() == '':
                option.text = f"Option {i+1}"
                option.save()

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
                question_id = question.id
                question_text = request.POST.get(f'question_{question_id}_text')
                
                if question_text:
                    question.text = question_text
                    question.save()
                    
                    # Get option IDs for this question
                    option_ids = request.POST.getlist(f'question_{question_id}_option_ids')
                    
                    # Create a list to track which options have been processed
                    processed_options = []
                    
                    # Process each option in the form
                    option_index = 0
                    while f'question_{question_id}_option_text_{option_index}' in request.POST:
                        option_text = request.POST.get(f'question_{question_id}_option_text_{option_index}')
                        is_correct = request.POST.get(f'question_{question_id}_is_correct_{option_index}') == 'on'
                        
                        # If we have a corresponding option ID for this index
                        if option_index < len(option_ids) and option_ids[option_index]:
                            # Update existing option
                            option_id = option_ids[option_index]
                            try:
                                option = Option.objects.get(id=option_id)
                                # Ensure option text is not empty
                                option.text = option_text if option_text and option_text.strip() else f"Option {option_index + 1}"
                                option.is_correct = is_correct
                                option.save()
                                processed_options.append(int(option_id))
                            except Option.DoesNotExist:
                                # Create new option if ID doesn't exist
                                new_option = Option.objects.create(
                                    question=question,
                                    text=option_text if option_text and option_text.strip() else f"Option {option_index + 1}",
                                    is_correct=is_correct
                                )
                                processed_options.append(new_option.id)
                        else:
                            # Create new option
                            new_option = Option.objects.create(
                                question=question,
                                text=option_text if option_text and option_text.strip() else f"Option {option_index + 1}",
                                is_correct=is_correct
                            )
                            processed_options.append(new_option.id)
                        
                        option_index += 1
                    
                    # Delete options that are no longer in the form
                    for option in question.options.all():
                        if option.id not in processed_options:
                            option.delete()

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
                                text=option_text if option_text.strip() else f"Option {j + 1}",
                                is_correct=is_correct
                            )

            messages.success(request, "Quiz updated successfully!")
            return redirect('update_quiz', quiz_id=quiz.id)

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

@login_required
def user_stats(request):
    """View function to display user statistics and analytics."""
    user = request.user
    
    # Basic stats
    total_attempts = QuizAttempt.objects.filter(user=user).count()
    unique_quizzes_taken = QuizAttempt.objects.filter(user=user).values('quiz').distinct().count()
    
    # Quiz completion stats
    completed_quizzes = QuizAttempt.objects.filter(user=user)
    
    # Score stats
    if completed_quizzes.exists():
        avg_score = completed_quizzes.aggregate(Avg('score'))['score__avg']
        highest_score = completed_quizzes.aggregate(Max('score'))['score__max']
        lowest_score = completed_quizzes.aggregate(Min('score'))['score__min']
    else:
        avg_score = highest_score = lowest_score = 0
    
    # Recent activity
    recent_attempts = []
    for attempt in QuizAttempt.objects.filter(user=user).order_by('-attempted_at')[:5]:
        if attempt.quiz.questions.count() > 0:
            percentage = round((attempt.score / attempt.quiz.questions.count()) * 100, 1)
        else:
            percentage = 0
            
        recent_attempts.append({
            'quiz': attempt.quiz,
            'score': attempt.score,
            'percentage': percentage,
            'attempted_at': attempt.attempted_at
        })
    
    # Quizzes created by user
    created_quizzes = Quiz.objects.filter(creator=user).count()
    
    # Count total questions answered
    total_questions_answered = 0
    for attempt in QuizAttempt.objects.filter(user=user):
        total_questions_answered += attempt.quiz.questions.count()
    
    # Calculate average percentage
    avg_percentage = 0
    if total_attempts > 0:
        total_possible_score = 0
        total_achieved_score = 0
        for attempt in QuizAttempt.objects.filter(user=user):
            question_count = attempt.quiz.questions.count()
            total_possible_score += question_count
            total_achieved_score += attempt.score
        
        if total_possible_score > 0:
            avg_percentage = round((total_achieved_score / total_possible_score) * 100, 1)
    
    # Prepare stats dictionary
    stats = {
        'quizzes_taken': unique_quizzes_taken,
        'questions_answered': total_questions_answered,
        'avg_percentage': avg_percentage
    }
    
    # Prepare data for performance chart
    performance_data = None
    quiz_attempts = QuizAttempt.objects.filter(user=user).order_by('-attempted_at')[:10]
    if quiz_attempts.exists():
        labels = []
        scores = []
        for attempt in quiz_attempts:
            if attempt.quiz.questions.count() > 0:
                score_percentage = round((attempt.score / attempt.quiz.questions.count()) * 100, 1)
                labels.append(attempt.quiz.title)
                scores.append(score_percentage)
        
        if labels and scores:
            performance_data = {
                'labels': labels,
                'scores': scores
            }
    
    # Get created quiz stats
    user_created_quizzes = Quiz.objects.filter(creator=user)
    created_quizzes_data = []
    
    for quiz in user_created_quizzes:
        quiz_attempts = QuizAttempt.objects.filter(quiz=quiz)
        attempts_count = quiz_attempts.count()
        
        # Calculate average score for this quiz
        avg_score_value = 0
        if attempts_count > 0:
            scores_sum = quiz_attempts.aggregate(Sum('score'))['score__sum'] or 0
            total_possible = attempts_count * quiz.questions.count()
            if total_possible > 0:
                avg_score_value = round((scores_sum / total_possible) * 100, 1)
        
        quiz_stat = {
            'title': quiz.title,
            'attempts': attempts_count,
            'avg_score': avg_score_value
        }
        created_quizzes_data.append(quiz_stat)
    
    # Categorize by quiz topics (placeholder for category performance)
    category_performance = []
    for quiz in Quiz.objects.filter(quizattempt__user=user).distinct():
        quiz_attempts = QuizAttempt.objects.filter(user=user, quiz=quiz)
        attempts_count = quiz_attempts.count()
        
        # Calculate average score for this category
        avg_score_val = 0
        if attempts_count > 0 and quiz.questions.count() > 0:
            total_score = quiz_attempts.aggregate(Sum('score'))['score__sum'] or 0
            total_possible = attempts_count * quiz.questions.count()
            if total_possible > 0:
                avg_score_val = round((total_score / total_possible) * 100, 1)
                
        category_performance.append({
            'name': quiz.title,  # Using quiz title as category
            'count': attempts_count,
            'avg_score': avg_score_val
        })
    
    context = {
        'stats': stats,
        'total_attempts': total_attempts,
        'avg_score': round(avg_score, 1) if avg_score else 0,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
        'recent_attempts': recent_attempts,
        'created_quizzes': created_quizzes,
        'performance_data': performance_data,
        'created_quizzes_data': created_quizzes_data,
        'category_performance': category_performance
    }
    
    return render(request, 'base/user_stats.html', context)

@login_required
def quiz_stats(request, quiz_id):
    """View detailed statistics for a specific quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get all attempts for this quiz
    attempts = QuizAttempt.objects.filter(quiz=quiz)
    total_participants = attempts.count()
    
    # Calculate stats
    stats = {
        'total_participants': total_participants,
        'avg_score': 0,
        'highest_score': 0,
        'highest_user': 'None',
        'pass_rate': 0,
        'recent_attempts': [],
        'question_stats': [],
        'score_distribution': {
            'low': 0,
            'medium': 0,
            'high': 0,
            'excellent': 0
        }
    }
    
    if total_participants > 0:
        # Calculate average score as a percentage
        avg_score_raw = attempts.aggregate(avg=Avg('score'))['avg'] or 0
        total_questions = quiz.questions.count()
        if total_questions > 0:
            avg_score_percentage = round((avg_score_raw / total_questions) * 100, 1)
            stats['avg_score'] = avg_score_percentage
        
        # Find highest score
        highest_attempt = attempts.order_by('-score').first()
        if highest_attempt:
            highest_percentage = round((highest_attempt.score / total_questions) * 100, 1) if total_questions > 0 else 0
            stats['highest_score'] = highest_percentage
            stats['highest_user'] = highest_attempt.user.username
        
        # Calculate pass rate (users who scored 70% or higher)
        if total_questions > 0:
            passing_score = 0.7 * total_questions
            passing_attempts = attempts.filter(score__gte=passing_score).count()
            stats['pass_rate'] = round((passing_attempts / total_participants) * 100, 1)
        
        # Recent attempts
        recent_attempts = attempts.order_by('-attempted_at')[:10]
        for attempt in recent_attempts:
            percentage = round((attempt.score / total_questions) * 100, 1) if total_questions > 0 else 0
            stats['recent_attempts'].append({
                'user': attempt.user,
                'score': attempt.score,
                'percentage': percentage,
                'attempted_at': attempt.attempted_at
            })
        
        # Score distribution
        for attempt in attempts:
            percentage = (attempt.score / total_questions) * 100 if total_questions > 0 else 0
            if percentage < 50:
                stats['score_distribution']['low'] += 1
            elif percentage < 70:
                stats['score_distribution']['medium'] += 1
            elif percentage < 90:
                stats['score_distribution']['high'] += 1
            else:
                stats['score_distribution']['excellent'] += 1
        
        # Question performance stats
        questions = quiz.questions.all()
        for question in questions:
            # Count how many users answered this question correctly
            correct_count = 0
            total_answers = 0
            
            for attempt in attempts:
                # Get the user's answer for this question
                user_answers = UserAnswer.objects.filter(quiz_attempt=attempt, question=question)
                if user_answers.exists():
                    total_answers += 1
                    user_answer = user_answers.first()
                    
                    # Get correct options for this question
                    correct_options = question.options.filter(is_correct=True)
                    selected_options = user_answer.selected_options.all()
                    
                    # Check if user selected all correct options and only correct options
                    if (set(correct_options) == set(selected_options)):
                        correct_count += 1
            
            # Calculate percentage of correct answers
            correct_percentage = round((correct_count / total_answers) * 100, 1) if total_answers > 0 else 0
            
            stats['question_stats'].append({
                'text': question.text,
                'correct_percentage': correct_percentage
            })
    
    context = {
        'quiz': quiz,
        'stats': stats
    }
    
    return render(request, 'base/quiz_stats.html', context)