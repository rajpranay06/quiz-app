from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text
    
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255, blank=False, null=False)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        if not self.text or self.text.strip() == '':
            return f"Option for Question {self.question.id}"
        return self.text
    
    def clean(self):
        # Validate that text is not empty
        if not self.text or self.text.strip() == '':
            raise ValidationError({'text': 'Option text cannot be empty'})
        
    def save(self, *args, **kwargs):
        # Set a default value if text is empty
        if not self.text or self.text.strip() == '':
            self.text = f"Option for Question {self.question.id}"
        super().save(*args, **kwargs)

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)
    score = models.IntegerField()
    attempts = models.IntegerField(default=0)  # ➡️ Track attempts
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.attempts} Attempt(s)"

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="user_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option)
    
    class Meta:
        unique_together = ('quiz_attempt', 'question')
