from django.urls import path

from task_controller import views

app_name = 'task_controller'
urlpatterns = [
    path('task/', views.list_view, name='base_view'),
]
