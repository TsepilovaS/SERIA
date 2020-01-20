from django.contrib.auth.models import AbstractUser, User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, null=True)
    group = models.ManyToManyField('Group', null=True, related_name='profiles')
    avatar = models.ImageField(upload_to='avatar', null=True, blank=True)
    quizzes_passed = models.IntegerField(null=False, default=0)
    right_answers = models.IntegerField(null=False, default=0)
    wrong_answers = models.IntegerField(null=False, default=0)
    is_admin = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-right_answers']


class Group(models.Model):
    title = models.TextField(max_length=50, null=True, blank=True)
    admin = models.ManyToManyField('Profile', null=True, related_name='groups')

    def __str__(self):
        return self.title


class Attempt(models.Model):
    quiz = models.ForeignKey('quizzes.Quiz', null=False, on_delete=models.CASCADE, related_name='attempted')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='attempts')
    right_answers = models.IntegerField(null=False, default=0)
    wrong_answers = models.IntegerField(null=False, default=0)

