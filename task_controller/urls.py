from django.urls import path

from task_controller import views

app_name = 'task_controller'
urlpatterns = [
    path('task/', views.task, name='task'),
    path('result/', views.result, name='base_view'),
]
