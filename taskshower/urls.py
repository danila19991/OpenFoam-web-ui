from django.urls import path

from . import views

app_name = 'taskshower'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
]
