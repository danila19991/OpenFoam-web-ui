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
import openfoamparser as Ofpp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from distutils.dir_util import copy_tree
import subprocess
from shutil import copyfile
import os
import zipfile
import shutil


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


class OpenFoamTask:

    @classmethod
    def get_name(cls):
        return "обтекание объекта"

    @classmethod
    def get_param_description(cls):
        return {
            "params": {
                "название": "string",
                "скорость течения": "string",
                "временной шаг": "string",
                "количество итераций": "string",
                "модель оптикаемого объекта": "file"
            }
        }

    @classmethod
    def validate(cls, params, files):
        try:
            assert "название" in params
            assert params["название"]
            assert "скорость течения" in params
            assert float(params["скорость течения"])
            assert "временной шаг" in params
            assert float(params["временной шаг"])
            assert "количество итераций" in params
            assert int(params["количество итераций"])
            assert "file" in files
            return True
        except AssertionError:
            return False
        except ValueError:
            return False

    @classmethod
    def create_task(cls, params, files, user):
        if not cls.validate(params, files):
            raise ValueError
        descr = {
            "скорость течения": params["скорость течения"],
            "временной шаг": params["временной шаг"],
            "количество итераций": params["количество итераций"]
        }
        task = Tasks.objects.create(name=params['название'],
                                    description=json.dumps(descr),
                                    user=user,
                                    param_file=files['file'],
                                    state=Tasks.QUEUED)
        task.save()
        return task.pk

    @classmethod
    @app.task
    def execute_task(task_id):
        logging.info(f"task {task_id} was accepted")
        try:
            task = Tasks.objects.get(pk=task_id)
            task.state = Tasks.IN_PROCESS
            task.save()
            params = json.loads(task.description)
            result_name = '_' + str(task.pk)

            logging.info(f"task {task_id} state 1")

            template_dir = 'template/'
            work_dir = f'auto_sol_{task_id}/'
            obj_file = 'data/' + task.param_file.url
            time_step = float(params["временной шаг"])
            it_num = int(params["количество итераций"])
            result_gif_path = 'tmp/' + result_name + ".gif"
            result_zip_path = 'tmp/' + result_name + ".zip"
            water_speed = float(params["скорость течения"])
            log_line = ''

            logging.info(f"task {task_id} state 2")

            def read_velocity(file):
                if file == 0:
                    file = 0
                file = work_dir + str(file)
                cells = Ofpp.FoamMesh(work_dir)
                cells.read_cell_centres(work_dir + '0/C')
                cc = cells.cell_centres

                vals = Ofpp.parse_internal_field(file + '/U')

                pres = 80

                map = np.zeros((pres, pres), dtype=float)
                map_n = np.zeros((pres, pres), dtype=float)
                mn = np.min(cc, axis=0)
                mx = np.max(cc, axis=0)
                # print(mn, mx)
                for line, v in zip(cc, vals):
                    p = (line - mn) / (mx - mn) * pres
                    map_n[min(int(p[1]), pres - 1), min(int(p[0]), pres - 1)] += 1
                    map[min(int(p[1]), pres - 1), min(int(p[0]), pres - 1)] += np.sqrt(np.sum(v * v))
                for i, line in enumerate(map_n):
                    for j, v in enumerate(line):
                        if not v:
                            map_n[i][j] = 1

                map = map / map_n
                return map

            def zipdir(path, ziph):
                # ziph is zipfile handle
                for root, dirs, files in os.walk(path):
                    for file in files:
                        ziph.write(os.path.join(root, file))

            control_dict = {
                "application": "icoFoam",
                "startFrom": "startTime",
                "startTime": 0,
                'stopAt': "endTime",
                "endTime": time_step * it_num,
                "deltaT": time_step / 2,
                "writeControl": "timeStep",
                "writeInterval": 2,
                "purgeWrite": 0,
                "writeFormat": "ascii",
                "writePrecision": 6,
                "writeCompression": "off",
                "timeFormat": "general",
                "timePrecision": 6,
                "runTimeModifiable": "true"
            }

            logging.info(f"task {task_id} state 3")

            copy_tree(template_dir, work_dir)
            copy_tree(work_dir + '/0.orig', work_dir + '/0')
            tmp_line = ''
            with open(work_dir + '0/U', "r") as f:
                for line in f:
                    if '(1 0 0)' in line:
                        line = line.replace('(1 0 0)', f"({water_speed} 0 0)")
                    tmp_line += line
            with open(work_dir + '0/U', "w") as f:
                f.write(tmp_line)

            os.makedirs(work_dir + 'constant/triSurface')
            copyfile(obj_file, work_dir + 'constant/triSurface/wing.obj')

            logging.info(f"task {task_id} state 4")

            with open(work_dir + 'system/controlDict', "a") as f_out:
                f_out.write('\n'.join([f"{key}   {val};" for key, val in control_dict.items()]))

            res = subprocess.run(['blockMesh'], stdout=subprocess.PIPE, cwd=work_dir)
            # print(res.stdout.decode())
            log_line += res.stdout.decode() + '\n'
            res = subprocess.run(['surfaceFeatures'], stdout=subprocess.PIPE, cwd=work_dir)
            # print(res.stdout.decode())
            log_line += res.stdout.decode() + '\n'
            res = subprocess.run(['snappyHexMesh', '-overwrite'], stdout=subprocess.PIPE, cwd=work_dir)
            # print(res.stdout.decode())
            log_line += res.stdout.decode() + '\n'
            res = subprocess.run(['icoFoam'], stdout=subprocess.PIPE, cwd=work_dir)
            # print(res.stdout.decode())
            log_line += res.stdout.decode() + '\n'
            res = subprocess.run(['postProcess', '-func', "writeCellCentres", '-time', '0'], stdout=subprocess.PIPE,
                                 cwd=work_dir)
            log_line += res.stdout.decode() + '\n'
            # print(res.stdout.decode())

            logging.info(f"task {task_id} state 5")

            maps = [read_velocity(i * time_step) for i in range(it_num + 1)]

            mx = max([np.max(mp) for mp in maps])
            map = maps[1]
            fig, axis = plt.subplots()  # il me semble que c'est une bonne habitude de faire supbplots
            heatmap = axis.imshow(map, vmin=0, vmax=mx, cmap=plt.cm.Blues)  # heatmap contient les valeurs
            plt.colorbar(heatmap)

            # plt.show()

            def init():
                heatmap.set_data(map)
                return heatmap,

            def animate(i):
                heatmap.set_data(maps[i + 1])
                return heatmap,

            anim = FuncAnimation(fig, animate, init_func=init,
                                 frames=it_num, interval=20, blit=True)

            anim.save(result_gif_path, writer='imagemagick')
            # plt.show()

            logging.info(f"task {task_id} state 6")

            zipf = zipfile.ZipFile(result_zip_path, 'w', zipfile.ZIP_DEFLATED)
            zipdir(work_dir, zipf)
            zipf.close()


            if task.state == Tasks.STOPED:
                task.delete()
                shutil.rmtree(work_dir)
                return

            logging.info(f"task {task_id} state 7")

            f1 = open(result_zip_path, "rb")
            f2 = open(result_gif_path, "rb")
            task.result_log_file.save(result_name + ".zip", File(f1))
            task.result_file.save(result_name + ".gif", File(f2))
            f1.close()
            f2.close()
            shutil.rmtree(work_dir)

            logging.info(f"task {task_id} state 8")


            task.state = Tasks.FINISHED
            task.finish_time = timezone.now()
            task.log = log_line
            task.save()
            logging.info(f"file url: {task.result_log_file.url}")

            logging.info(f"task {task_id} state 9")
        except Tasks.DoesNotExist:
            logging.warning(
                "Tried to make  non-existing task '%s'" % task_id)
        except Exception:
            logging.warning(
                "un kwown error in task '%s'" % task_id)

