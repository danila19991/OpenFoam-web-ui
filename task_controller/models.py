from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.


class Tasks(models.Model):
    QUEUED = 1
    IN_PROCESS = 2
    ERRORED = 3
    FINISHED = 4

    TASK_STATES = [
        (0, 'none'),
        (QUEUED, 'quued'),
        (IN_PROCESS, 'in-process'),
        (ERRORED, 'errored'),
        (FINISHED, 'finished')
    ]

    state = models.IntegerField(choices=TASK_STATES, default=QUEUED)
    name = models.TextField(null=False)
    description = models.TextField(null=True)
    log = models.TextField(null=True)
    result = models.FileField(null=True, upload_to='results/')
    accept_time = models.DateTimeField(default=datetime.datetime.now())
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Params(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, null=False)
    args = models.TextField(null=False)
    file = models.FileField(null=True, upload_to='params/')
