from django.urls import path

from . import views

app_name = 'auth_and_static'
urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('params/', views.params, name='params'),
]
