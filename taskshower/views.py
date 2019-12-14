from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template import loader
from django.db.utils import IntegrityError
from django.urls import reverse, resolve
from django.contrib.auth.decorators import login_required


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
    if request.method == 'POST':
        if 'exit' in request.POST:
            logout(request)
            return HttpResponseRedirect(reverse('taskshower:login'))

    template = loader.get_template('index.html')
    context = {
        'any_data': [],
        'user_name': request.user.username
    }
    return HttpResponse(template.render(context, request))
