from django.db import models
from django.contrib.auth.models import User

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
    time = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
