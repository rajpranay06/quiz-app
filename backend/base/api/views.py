from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg

from base.models import Quiz, Question, Option, QuizAttempt, UserAnswer
from .serializers import (
    QuizSerializer, 
    QuizDetailSerializer, 
    QuestionSerializer, 
    OptionSerializer, 
    QuizAttemptSerializer,
    UserAnswerSerializer,
    QuizSubmissionSerializer
)

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        # Authentication routes
        'POST /api/auth/register/',
        'POST /api/auth/login/',
        'POST /api/token/',
        'POST /api/token/refresh/',
        'POST /api/token/verify/',
        # Quiz routes
        'GET /api/quizzes',
        'GET /api/quizzes/:id',
        'POST /api/quizzes/create',
        'PUT /api/quizzes/:id/update',
        'DELETE /api/quizzes/:id/delete',
        'GET /api/quizzes/:id/questions',
        'POST /api/quizzes/:id/add-question',
        'POST /api/quizzes/:id/submit',
        'GET /api/quizzes/:id/statistics',
        # Question routes
        'GET /api/questions',
        'GET /api/questions/:id',
        'PUT /api/questions/:id/update',
        'DELETE /api/questions/:id/delete',
        'POST /api/questions/:id/add-option',
        # User stats routes
        'GET /api/user-stats',
        'GET /api/user-stats/summary',
        # Join quiz
        'POST /api/join-quiz'
    ]
    return Response(routes)

# Quiz Views
@api_view(['GET'])
def getQuizzes(request):
    quizzes = Quiz.objects.all().order_by('-created_at')
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getQuiz(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    serializer = QuizDetailSerializer(quiz)
    return Response(serializer.data)

@api_view(['POST'])
def createQuiz(request):
    serializer = QuizSerializer(data=request.data)
    if serializer.is_valid():
        # If user is authenticated, associate the quiz with them
        if request.user.is_authenticated:
            serializer.save(creator=request.user)
        else:
            serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def updateQuiz(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and quiz.creator and quiz.creator != request.user:
        return Response({"detail": "You don't have permission to edit this quiz."}, status=403)
    
    serializer = QuizSerializer(quiz, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def deleteQuiz(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and quiz.creator and quiz.creator != request.user:
        return Response({"detail": "You don't have permission to delete this quiz."}, status=403)
    
    quiz.delete()
    return Response(status=204)

@api_view(['GET'])
def getQuizQuestions(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    questions = Question.objects.filter(quiz=quiz)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addQuestion(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and quiz.creator and quiz.creator != request.user:
        return Response({"detail": "You don't have permission to add questions to this quiz."}, status=403)
    
    # Create question
    question_text = request.data.get('text')
    if not question_text:
        return Response({"detail": "Question text is required"}, status=400)
    
    question = Question.objects.create(quiz=quiz, text=question_text)
    
    # Create options
    options_data = request.data.get('options', [])
    if not options_data or len(options_data) < 2:
        question.delete()
        return Response({"detail": "At least 2 options are required"}, status=400)
    
    has_correct = False
    for option_data in options_data:
        text = option_data.get('text')
        is_correct = option_data.get('is_correct', False)
        
        if is_correct:
            has_correct = True
            
        Option.objects.create(
            question=question,
            text=text if text.strip() else f"Option {len(question.options.all()) + 1}",
            is_correct=is_correct
        )
    
    # Handle case where no correct option selected
    if not has_correct:
        # Mark first option as correct
        first_option = question.options.first()
        if first_option:
            first_option.is_correct = True
            first_option.save()
        else:
            question.delete()
            return Response({"detail": "At least one option must be marked as correct"}, status=400)
    
    serializer = QuestionSerializer(question)
    return Response(serializer.data, status=201)

@api_view(['POST'])
def submitQuiz(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    
    # Handle anonymous users
    if not request.user.is_authenticated:
        return Response({"detail": "You need to be logged in to submit quiz answers and save your score."}, status=403)
    
    user = request.user
    
    serializer = QuizSubmissionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    # Check if quiz_id in request matches the URL param
    if serializer.validated_data['quiz_id'] != int(pk):
        return Response({"detail": "Quiz ID mismatch"}, status=400)
    
    # Get the questions and prepare data for processing
    questions = Question.objects.filter(quiz=quiz).prefetch_related('options')
    
    # Create or get quiz attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        user=user,
        quiz=quiz,
        defaults={'score': 0, 'attempts': 1}
    )
    
    if not created:
        # Increment attempt count if this is a retry
        attempt.attempts += 1
    
    # Clear previous answers
    UserAnswer.objects.filter(quiz_attempt=attempt).delete()
    
    # Process answers using the same scoring logic as in quizService
    score = 0
    total_questions = questions.count()
    correct_answers = 0
    
    # Process each answer
    user_answers = serializer.validated_data['answers']
    for answer_data in user_answers:
        for question_id, option_ids in answer_data.items():
            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
                
                # Create user answer
                user_answer = UserAnswer.objects.create(
                    quiz_attempt=attempt,
                    question=question
                )
                
                # Add selected options
                selected_options = Option.objects.filter(id__in=option_ids, question=question)
                user_answer.selected_options.set(selected_options)
                
                # Check if answer is correct
                correct_options = question.options.filter(is_correct=True).count()
                selected_correct = selected_options.filter(is_correct=True).count()
                
                # Full point if all correct options are selected and no incorrect ones
                if (selected_correct == correct_options and 
                    len(option_ids) == correct_options):
                    correct_answers += 1
                # Partial credit for partially correct answers
                elif selected_correct > 0:
                    correct_answers += selected_correct / correct_options * 0.5
                
            except Question.DoesNotExist:
                continue
    
    # Calculate score percentage
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    attempt.score = score
    attempt.save()
    
    return Response({
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'attempt': attempt.attempts
    })

@api_view(['GET'])
def getQuizStatistics(request, pk):
    quiz = get_object_or_404(Quiz, id=pk)
    
    # Use logic from quizService.quiz_stats
    attempts = QuizAttempt.objects.filter(quiz=quiz)
    total_participants = attempts.count()
    
    stats = {
        'total_attempts': total_participants,
        'average_score': 0,
        'highest_score': 0,
        'lowest_score': 0
    }
    
    if total_participants > 0:
        # Calculate statistics
        total_questions = quiz.questions.count()
        
        if total_questions > 0:
            # Average score
            avg_score_raw = attempts.aggregate(avg=Avg('score'))['avg'] or 0
            avg_score_percentage = round((avg_score_raw / total_questions) * 100, 1)
            stats['average_score'] = avg_score_percentage
            
            # Highest and lowest scores
            highest_attempt = attempts.order_by('-score').first()
            if highest_attempt:
                highest_percentage = round((highest_attempt.score / total_questions) * 100, 1)
                stats['highest_score'] = highest_percentage
            
            lowest_attempt = attempts.order_by('score').first()
            if lowest_attempt:
                lowest_percentage = round((lowest_attempt.score / total_questions) * 100, 1)
                stats['lowest_score'] = lowest_percentage
    
    return Response(stats)

# Question Views
@api_view(['GET'])
def getQuestions(request):
    quiz_id = request.query_params.get('quiz_id')
    if quiz_id:
        questions = Question.objects.filter(quiz_id=quiz_id)
    else:
        questions = Question.objects.all()
    
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getQuestion(request, pk):
    question = get_object_or_404(Question, id=pk)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)

@api_view(['PUT'])
def updateQuestion(request, pk):
    question = get_object_or_404(Question, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and question.quiz.creator and question.quiz.creator != request.user:
        return Response({"detail": "You don't have permission to edit this question."}, status=403)
    
    serializer = QuestionSerializer(question, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def deleteQuestion(request, pk):
    question = get_object_or_404(Question, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and question.quiz.creator and question.quiz.creator != request.user:
        return Response({"detail": "You don't have permission to delete this question."}, status=403)
    
    question.delete()
    return Response(status=204)

@api_view(['POST'])
def addOption(request, pk):
    question = get_object_or_404(Question, id=pk)
    
    # Check permissions if user is authenticated
    if request.user.is_authenticated and question.quiz.creator and question.quiz.creator != request.user:
        return Response({"detail": "You don't have permission to add options to this question."}, status=403)
    
    # Create option
    text = request.data.get('text')
    is_correct = request.data.get('is_correct', False)
    
    if not text:
        return Response({"detail": "Option text is required"}, status=400)
    
    option = Option.objects.create(
        question=question,
        text=text if text.strip() else f"Option {question.options.count() + 1}",
        is_correct=is_correct
    )
    
    serializer = OptionSerializer(option)
    return Response(serializer.data, status=201)

# User Stats Views - these still require authentication
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserStats(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user).order_by('-attempted_at')
    serializer = QuizAttemptSerializer(attempts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserStatsSummary(request):
    user = request.user
    attempts = QuizAttempt.objects.filter(user=user)
    
    # Calculate stats
    total_attempts = attempts.count()
    unique_quizzes_taken = attempts.values('quiz').distinct().count()
    
    # Score stats
    if attempts.exists():
        avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
        highest_score = attempts.order_by('-score').first().score if attempts.exists() else 0
        lowest_score = attempts.order_by('score').first().score if attempts.exists() else 0
        
        # Calculate average percentage 
        total_possible_score = 0
        total_achieved_score = 0
        for attempt in attempts:
            question_count = attempt.quiz.questions.count()
            total_possible_score += question_count
            total_achieved_score += attempt.score
        
        avg_percentage = 0
        if total_possible_score > 0:
            avg_percentage = round((total_achieved_score / total_possible_score) * 100, 1)
    else:
        avg_score = highest_score = lowest_score = avg_percentage = 0
    
    stats = {
        'total_quizzes_taken': unique_quizzes_taken,
        'best_score': highest_score,
        'average_score': round(avg_score, 1) if avg_score else 0,
        'average_percentage': avg_percentage,
        'total_attempts': total_attempts,
    }
    
    return Response(stats)

@api_view(['POST'])
def joinQuiz(request):
    code = request.data.get('code')
    
    try:
        quiz_id = int(code)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        return Response({'quiz_id': quiz.id, 'title': quiz.title})
    except (ValueError, Quiz.DoesNotExist):
        return Response({'detail': 'Invalid quiz code'}, status=404) 