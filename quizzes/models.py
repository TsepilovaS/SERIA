from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Language(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    admin = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='quizzes')
    is_native = models.BooleanField(default=False)
    language = models.ForeignKey(Language, null=True, on_delete=models.CASCADE, related_name='quizzes')
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_text = models.TextField(max_length=300, null=False, blank=False)
    quiz = models.ForeignKey(Quiz, null=False, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey('Question', null=False, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(max_length=100, null=False, blank=False)
    is_right = models.BooleanField(null=False, default=True)

    # def __str__(self):
    #     return self.answer_text + 'is' + self.is_right