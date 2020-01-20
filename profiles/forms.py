from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

from .models import Profile
from quizzes.models import Quiz, Question, Answer

STATUS_CHOICES = [('Student', 'Student'),
                  ('Teacher', 'Teacher')]


class SignupForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    # last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    status = forms.ChoiceField(required=True, choices=STATUS_CHOICES)
    custom_group = forms.CharField(required=False)
    # email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'status', 'custom_group', 'password1', 'password2',)


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('avatar',)


class QuizForm(forms.ModelForm):

    class Meta:
        model = Quiz
        fields = ('name', 'attempts')


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('question_text',)


class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ('answer_text', 'is_right')
