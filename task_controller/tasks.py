import logging
import time
import sys
import json

from remoteexperements.celery import app
from task_controller.models import Tasks
from django.conf import settings
from django.utils import timezone
from django.core.files import File
from datetime import datetime


class TaskDispatcher:
    __instance = None

    def __init__(self, tasks):
        if not TaskDispatcher.__instance:
            self._tasks = dict()
            self._params = None
            for task in tasks:
                task_elems = task.split('.')
                task_obj = getattr(sys.modules['.'.join(task_elems[:-1])],
                                   task_elems[-1])
                self._tasks[task_obj.get_name()] = task_obj
                logging.info(f"task '{task_obj.get_name()}' was added to list")
        else:
            # self = self.getInstance()
            # return self.getInstance()
            print("Instance already created:", self.get_instance())
            raise NotImplementedError

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = TaskDispatcher(settings.USED_TASKS)
        return cls.__instance

    def get_task_by_name(self, name):
        if name not in self._tasks:
            raise ValueError
        return self._tasks[name]

    def get_all_params(self):
        if not self._params:
            self._params = dict()
            for key, val in self._tasks.items():
                self._params[key] = val.get_param_description()
        return self._params


class HelloWorld:

    @classmethod
    def get_name(cls):
        return "Тестовая задача"

    @classmethod
    def validate(cls, params, files):
        return True

    @classmethod
    def get_param_description(cls):
        return {
            "params": {
                "name": "string"
            },
            "add_param_blocks": {
                "params": {
                    "name": "string"
                },
                "params2": {
                    "name1": "string",
                    "name2": "string"
                }

            }
        }

    @classmethod
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


class HelloWorld2:

    @classmethod
    def get_name(cls):
        return "Тестовая парабола"

    @classmethod
    def get_param_description(cls):
        return {
            "params": {
                "имя": "string",
                "сообщение": "string",
                "файл": "file"
            }
        }

    @classmethod
    def validate(cls, params, files):
        try:
            assert "имя" in params
            assert params["имя"]
            assert "сообщение" in params
            assert params["сообщение"]
            assert "file" in files
            return True
        except AssertionError:
            return False

    @classmethod
    def create_task(cls, params, files, user):
        if not cls.validate(params, files):
            raise ValueError
        descr = {
            "сообщение": params["сообщение"]
        }
        task = Tasks.objects.create(name=params['имя'],
                                    description=json.dumps(descr),
                                    user=user,
                                    param_file=files['file'],
                                    state=Tasks.QUEUED)
        task.save()
        return task.pk

    @classmethod
    #@app.task
    def execute_task(cls,task_id):
        logging.info(f"task {task_id} was accepted")
        try:
            task = Tasks.objects.get(pk=task_id)
            task.state = Tasks.IN_PROCESS
            task.save()
            params = json.loads(task.description)
            result_name = task.name + '_' + str(task.pk)

            #time.sleep(10)

            if task.state == Tasks.STOPED:
                task.delete()
                return

            task.log = f"ваше сообщение {params['сообщение']}"
            f1 = open('data/' + task.param_file.url)
            f2 = open('test.gif', "rb")
            task.result_log_file.save(result_name, File(f1))
            logging.info(f"file url: {task.result_log_file.url}")
            task.result_file.save(result_name + ".gif", File(f2))
            task.state = Tasks.FINISHED
            task.finish_time = timezone.now()
            task.save()
            f1.close()
            f2.close()
        except Tasks.DoesNotExist:
            logging.warning(
                "Tried to make  non-existing task '%s'" % task_id)
