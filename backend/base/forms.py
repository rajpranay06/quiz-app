from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz, Question, Option
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        
        # Ensure email is unique
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use. Please use a different email.")
        
        # Extract domain from email
        domain = email.split('@')[-1].lower()
        
        # Only allow specific approved domains
        allowed_domains = [
            'gmail.com',
            'yahoo.com',
            'sjsu.edu'
        ]
        
        if domain not in allowed_domains:
            raise ValidationError(f"Only email addresses from the following domains are accepted: {', '.join(allowed_domains)}")
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter quiz title', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter quiz description', 'class': 'form-control', 'rows': 4}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        
        # Check if this is an update (instance with id exists)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # Exclude the current instance from the uniqueness check
            quizzes = Quiz.objects.filter(title=title).exclude(pk=instance.pk)
        else:
            # New quiz - check against all existing quizzes
            quizzes = Quiz.objects.filter(title=title)
            
        if quizzes.exists():
            raise forms.ValidationError("A quiz with this title already exists. Please choose a different title.")
            
        return title

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Enter question text', 'class': 'form-control mb-3'}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Enter option text', 'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

OptionFormSet = inlineformset_factory(
    Question, 
    Option, 
    form=OptionForm, 
    extra=2,  # Start with 2 options 
    can_delete=True,
    min_num=2,  # Require at least 2 options
    validate_min=True
)
    
class JoinQuizForm(forms.Form):
    quiz_id = forms.IntegerField(
        label="Enter Quiz ID",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter Quiz ID', 'class': 'form-control'})
    )