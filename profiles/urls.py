from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from .views import *

app_name = "profiles"
# app_name will help us do a reverse look-up latter.
def login_forbidden(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous, login_url='/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

urlpatterns = [
    path('', login_required(profile), name='profile'),
    path('logout/', login_required(logout_view), name='logout'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('dashboard/', login_required(dashboard), name='dashboard'),
    path('stat/', login_required(stat), name='stat'),
    path('quiz/check/<int:pk>', login_required(quiz_check), name='quiz_check'),
    path('quiz/<int:pk>', login_required(quiz_start), name='quiz_start'),
    path('dashboard/result', login_required(dashboard_result), name='dashboard_result'),
    path('dashboard/lang/<str:lang>', login_required(dashboard_lang) ,name='dashboard_lang'),
    path('update/', login_required(ProfileUpdate.as_view()), name='profile_update'),
    path('quiz/<int:pk>/question/', login_required(QuestionList.as_view()), name='question_list'),
    path('quiz/<int:pk>/question/add/', login_required(QuestionCreate.as_view()), name='question_add'),
    path('quiz/<int:pk>/question/<int:pk2>/answer/add/', login_required(AnswerCreate.as_view()), name='answer_add'),
    path('quiz/<int:pk>/question/<int:pk2>/answer/delete/<int:pk3>', login_required(AnswerDelete.as_view()), name='answer_delete'),
    path('quiz/<int:pk>/question/<int:pk2>/answer/update/<int:pk3>', login_required(AnswerUpdate.as_view()), name='answer_update'),
    path('quiz/<int:pk>/question/<int:pk2>/answer/', login_required(AnswerList.as_view()), name='answer_list'),
    path('quiz/<int:pk>/question/update/<int:pk2>', login_required(QuestionUpdate.as_view()), name='question_update'),
    path('quiz/<int:pk>/question/delete/<int:pk2>', login_required(QuestionDelete.as_view()), name='question_delete'),
    path('quiz/', login_required(QuizList.as_view()), name='quiz_list'),
    path('quiz/add/', login_required(QuizCreate.as_view()), name='quiz_add'),
    path('quiz/update/<int:pk>', login_required(QuizUpdate.as_view()), name='quiz_update'),
    path('quiz/delete/<int:pk>', login_required(QuizDelete.as_view()), name='quiz_delete'),
    path('quiz/<int:pk>/', login_required(QuizDetail.as_view()), name='quiz_detail'),
]