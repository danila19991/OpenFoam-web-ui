from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import loader
from django.db.utils import IntegrityError
from django.urls import reverse, resolve
from django.contrib.auth.decorators import login_required
from taskshower.models import Tasks
from taskshower.tasks import execute_task


def register(request):
    template = loader.get_template('register.html')
    if request.method == 'POST':
        if 'user_name' in request.POST and 'password' in request.POST:
            if User.objects.filter(username=request.POST['user_name']).exists():
                return HttpResponse(template.render(
                    {'used_name': request.POST['user_name']}, request))
            user = User.objects.create_user(request.POST['user_name'],
                                     request.POST['user_name'] + '@host.net',
                                     request.POST['password'])
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('taskshower:index'))

    context = {
        'any_data': [],
    }
    return HttpResponse(template.render(context, request))


def login_view(request):
    template = loader.get_template('login.html')
    if request.method == 'POST':
        print(dict(request.POST))
        if 'user_name' in request.POST and 'password' in request.POST:
            user = authenticate(request, username=request.POST['user_name'],
                                    password=request.POST['password'])
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('taskshower:index'))
            else:
                return HttpResponse(template.render({
                                'incorrect_data': request.POST['user_name'],
                                                    }, request))

    context = {
        'any_data': [],
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/login')
def index(request):
    template = loader.get_template('index.html')
    context = {
        'any_data': [],
        'user_name': request.user.username
    }
    if request.method == 'POST':
        if 'exit' in request.POST:
            logout(request)
            return HttpResponseRedirect(reverse('taskshower:login'))

        if 'time' in request.POST and 'name' in request.POST:
            try:
                val = int(request.POST['time'])
                name = request.POST['name']
                if val < 1 or val > 60:
                    raise ValueError
                task = Tasks.objects.create(name=name, time=val,
                                            user=request.user,
                                            state=Tasks.QUEUED)
                task.save()
                execute_task.delay(task.pk)
                context['correct_task'] = request.POST['name']
            except ValueError:
                context['incorrect_task_t'] = request.POST['time']
                context['incorrect_task_n'] = request.POST['name']

    tasks_descr = list()
    tasks = Tasks.objects.filter(related_user=request.user)
    state_dict = {
        Tasks.QUEUED: 'queued',
        Tasks.IN_PROCESS: 'in progress',
        Tasks.ERRORED: 'errored',
        Tasks.FINISHED: 'finished',
    }
    for task in tasks:
        tasks_descr.append((
            task.name,
            state_dict[task.state]
        ))

    context['tasks'] = tasks_descr

    return HttpResponse(template.render(context, request))
