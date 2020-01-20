from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView

from quizzes.models import Language, Quiz, Question, Answer
from .forms import SignupForm, ProfileEditForm, QuizForm, QuestionForm, AnswerForm
from .models import Profile, Group, Attempt


def logout_view(request):
    logout(request)
    return redirect('profiles:login')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(password=form.cleaned_data['password1'],
                                            username=form.cleaned_data['username'],
                                            email=form.cleaned_data['email'])
            print(user)
            if form.cleaned_data.get('status') == "Student":
                is_admin = False
                avatar = 'default/default_student_avatar.png'
            else:
                is_admin = True
                avatar = 'default/default_admin_avatar.png'
            profile = Profile.objects.create(
                avatar=avatar,
                is_admin=is_admin
            )
            profile.user = user
            profile.save()
            if form.cleaned_data['custom_group'] is not '':
                if profile.is_admin:
                    groups = (form.cleaned_data.get('custom_group')).split(',')
                    for group in groups:
                        group, _ = Group.objects.get_or_create(title=group)
                        group.admin.add(profile)
                        group.save()
                else:
                    group, _ = Group.objects.get_or_create(title=form.cleaned_data.get('custom_group'))
                    profile.group.add(group)
            profile.save()
            user.save()
            return redirect('profiles:login')
    else:
        form = SignupForm()
    return render(request, 'profiles/signup.html', {'form': form})


def dashboard(request):
    if request.user.profile.is_admin:
        return redirect('profiles:profile')
    languages = Language.objects.all()
    return render(request, 'profiles/dashboard.html', {'languages': languages})


def dashboard_result(request):
    if request.user.profile.is_admin:
        return redirect('profiles:profile')

    at=None
    languages = Language.objects.all()

    query = request.GET.get('search', None)

    print(query)
    quiz = None
    attempts_left = None

    try:
        quiz = Quiz.objects.get(name=query)
    except:
        quiz = None
    if not quiz:
        return render(request, 'quizzes/dashboard_result.html', {'quiz': quiz, 'languages': languages})
    try:
        attemted_times = Attempt.objects.filter(quiz=quiz, user=request.user).count()
    except:
        attemted_times = 0
    if quiz.attempts != 0:
        attempts_left = quiz.attempts - attemted_times
    else:
        at="okay"

    return render(request, 'quizzes/dashboard_result.html', {'quiz': quiz, 'attempts_left': attempts_left, 'at':at, 'languages': languages})


def quiz_start(request, pk):
    if request.user.profile.is_admin:
        return redirect('profiles:profile')
    quiz = get_object_or_404(Quiz, id=pk)
    try:
        attemted_times = Attempt.objects.filter(quiz=quiz, user=request.user).count()
    except:
        attemted_times = 0
    print(attemted_times)
    #print(attemted_times)
    attempts = quiz.attempts
    if attempts == 0:
        pass
    elif attempts-attemted_times <= 0:
        return redirect('profiles:dashboard')
    attempt = Attempt.objects.create(user=request.user, quiz=quiz)
    attempt.save()
    request.user.profile.quizzes_passed += 1
    request.user.profile.save()
    return render(request, 'quizzes/quiz.html', {'quiz': quiz, 'attempt_id': attempt.id})


def quiz_check(request, pk):
    if request.user.profile.is_admin:
        return redirect('profiles:profile')
    right_count = int(request.GET.get('right'))
    wrong_count = int(request.GET.get('wrong'))
    quiz_id = request.GET.get('quizId', None)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = Attempt.objects.get(id=pk, quiz=quiz, user=request.user)
    attempt.right_answers = right_count
    attempt.wrong_answers = wrong_count
    profile = request.user.profile
    attempt.save()
    print(profile.right_answers)
    profile.right_answers += right_count
    profile.wrong_answers += wrong_count
    profile.save()

    return JsonResponse(data = {'status': 'okay'})


def dashboard_lang(request, lang):
    languages = Language.objects.all()
    language = get_object_or_404(Language, name=lang)
    return render(request, 'profiles/dashboard_lang.html', {'languages': languages, 'lang': language})


def profile(request):
    if request.method == 'GET':
        if request.user.profile.is_admin:
            status = "Teacher"
            group_count = Group.objects.filter(admin=request.user.profile)
        else:
            status = "Student"
            group_count = None
        return render(request, 'profiles/profile.html', {'status': status, 'group_count': group_count})


def stat(request):
    if request.user.profile.is_admin:
        groups = Group.objects.filter(admin=request.user.profile)
    else:
        groups = request.user.profile.group.all()
    return render(request, 'profiles/user_stat.html', {'groups': groups})


class ProfileUpdate(View):
    def get(self, request):
        # profile = get_object_or_404(Profile, pk=request.user.pk)
        if request.user.profile.is_admin:
            group = (',').join([group.title for group in Group.objects.filter(admin=request.user.profile).all()])
        else:
            group = (',').join([group.title for group in request.user.profile.group.all()])
        form = ProfileEditForm()
        return render(request, 'profiles/update-profile.html', {'form':form, 'group': group})

    def post(self, request):
        # profile = get_object_or_404(Profile, pk=request.user.pk)
        if request.user.profile.is_admin:
            _ = [group.admin.remove(request.user.profile) for group in Group.objects.filter(admin=request.user.profile).all()]
        else:
            request.user.profile.group.clear()
        form = ProfileEditForm(request.POST, request.FILES)
        # print(form.save())
        print(request.FILES.get('avatar'))
        if request.FILES.get('avatar') != '':
            profile = request.user.profile
            profile.avatar = request.FILES.get('avatar')
            profile.save()
        if request.POST.get('group') != '':
            if request.user.profile.is_admin:
                groups = (request.POST.get('group')).split(',')
                for group in groups:
                    group, _ = Group.objects.get_or_create(title=group)
                    group.admin.add(request.user.profile)
            else:
                group = request.POST.get('group')
                group, _ = Group.objects.get_or_create(title=group)
                request.user.profile.group.add(group)
        # profile.save()
        return redirect('profiles:profile')


class QuizList(ListView):
    template_name = 'profiles/quiz_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        return Quiz.objects.filter(admin=self.request.user)


class QuestionList(ListView):
    template_name = 'profiles/question_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.filter(quiz__id=self.kwargs['pk'])


class AnswerList(ListView):
    template_name = 'profiles/answer_list.html'
    context_object_name = 'answers'

    def get_queryset(self):
        return Answer.objects.filter(question__id=self.kwargs['pk2'])


class QuizDetail(DetailView):
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'

    def get_queryset(self):
        return Quiz.objects.filter(admin=self.request.user)


class QuizDelete(DeleteView):
    model = Quiz
    success_url = reverse_lazy('profiles:quiz_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class QuestionDelete(DeleteView):
    model = Question
    pk_url_kwarg = 'pk2'

    def get_success_url(self):
        if Question.objects.filter(id=self.kwargs["pk"]).count() == 0:
            return f'/profile/quiz'
        return f'/profile/quiz/{self.kwargs["pk"]}/question/'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class AnswerDelete(DeleteView):
    model = Answer
    pk_url_kwarg = 'pk3'

    def get_success_url(self):
        return f'/profile/quiz/{self.kwargs["pk"]}/question'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class QuizCreate(CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_create.html'
    success_url = reverse_lazy('profiles:quiz_list')

    def form_valid(self, form):
        quiz = form.instance
        quiz.admin = self.request.user
        return super(QuizCreate, self).form_valid(form)


class QuestionCreate(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quizzes/question_create.html'

    def form_valid(self, form):
        question = form.instance
        quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
        question.quiz = quiz
        return super(QuestionCreate, self).form_valid(form)

    def get_success_url(self):
        return f'/profile/quiz/{self.kwargs["pk"]}/question/'


class AnswerCreate(CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'quizzes/answer_create.html'

    def form_valid(self, form):
        answer = form.instance
        question = get_object_or_404(Question, pk=self.kwargs['pk2'])
        answer.question = question
        return super(AnswerCreate, self).form_valid(form)

    def get_success_url(self):
        return f'/profile/quiz/{self.kwargs["pk"]}/question/{self.kwargs["pk2"]}/answer/'



class QuizUpdate(UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_update.html'
    success_url = reverse_lazy('profiles:quiz_list')


class QuestionUpdate(UpdateView):
    model = Question
    form_class = QuestionForm
    pk_url_kwarg = 'pk2'
    template_name = 'quizzes/question_update.html'

    def get_success_url(self):
        return f'/profile/quiz/{self.kwargs["pk"]}/question'


class AnswerUpdate(UpdateView):
    model = Answer
    form_class = AnswerForm
    pk_url_kwarg = 'pk3'
    template_name = 'quizzes/answer_update.html'

    def get_success_url(self):
        return f'/profile/quiz/{self.kwargs["pk"]}/question/{self.kwargs["pk2"]}/answer'



