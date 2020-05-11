from django.urls import path

from task_controller import views

app_name = 'task_controller'
urlpatterns = [
    path('task/', views.task, name='task'),
    path('download/<str:file_class>/<str:file_name>', views.get_file, name='download'),
    path('result/', views.result, name='base_view'),
    path('params/', views.params, name='params'),
]
