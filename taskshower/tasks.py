import logging
import time

from remoteexperements.celery import app
from taskshower.models import Tasks


@app.task
def execute_task(task_id):
    logging.info(f"task {task_id} was accepted")
    try:
        task = Tasks.objects.get(pk=task_id)
        task.state = Tasks.IN_PROCESS
        task.save()

        time.sleep(10)

        task.state = Tasks.FINISHED
        task.save()
    except Tasks.DoesNotExist:
        logging.warning(
            "Tried to make  non-existing task '%s'" % task_id)