from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Quiz, Question
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
            'title': forms.TextInput(attrs={'placeholder': 'Enter quiz title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter quiz description'}),
        }

class QuestionForm(forms.ModelForm):
    correct_option = forms.ChoiceField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Question
        fields = ['text', 'option1', 'option2', 'option3', 'option4', 'correct_option']  # Removed 'quiz'
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Enter question text'}),
            'option1': forms.TextInput(attrs={'placeholder': 'Option 1'}),
            'option2': forms.TextInput(attrs={'placeholder': 'Option 2'}),
            'option3': forms.TextInput(attrs={'placeholder': 'Option 3'}),
            'option4': forms.TextInput(attrs={'placeholder': 'Option 4'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        correct_option = cleaned_data.get("correct_option")
        options = [
            cleaned_data.get("option1"),
            cleaned_data.get("option2"),
            cleaned_data.get("option3"),
            cleaned_data.get("option4"),
        ]

        # Ensure the correct option is not empty
        if not options[int(correct_option) - 1]:  
            raise forms.ValidationError("The selected correct option cannot be empty.")

        return cleaned_data
    
class JoinQuizForm(forms.Form):
    quiz_id = forms.IntegerField(
        label="Enter Quiz ID",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter Quiz ID'})
    )