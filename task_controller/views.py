from django.http import HttpResponse, JsonResponse, FileResponse
from .models import Tasks, Params
from task_controller.tasks import execute_task

state_dict = {
    Tasks.QUEUED: 'queued',
    Tasks.IN_PROCESS: 'in progress',
    Tasks.ERRORED: 'errored',
    Tasks.FINISHED: 'finished',
}


def result(request):
    if not request.user.is_authenticated:
        result = {
            'status': 'error',
            'message': 'need auth'
        }
        return JsonResponse(result, content_type='application/json', status=403)
    id = request.GET.get('id', None)
    if id is not None:
        try:
            id = int(id)
        except ValueError:
            result = {
                'status': 'error',
                'message': 'incorrect id'
            }
            return JsonResponse(result, content_type='application/json', status=400)

        task_query = Tasks.objects.filter(id=id)
        if not len(task_query):
            result = {
                'status': 'error',
                'message': 'task not found'
            }
            return JsonResponse(result, content_type='application/json', status=404)
        task = task_query[0]
        if task.user != request.user:
            result = {
                'status': 'error',
                'message': 'wrong user'
            }
            return JsonResponse(result, content_type='application/json', status=403)

        if not task.result:
            result = {
                'status': 'error',
                'message': 'no result'
            }
            return JsonResponse(result, content_type='application/json', status=400)

        return FileResponse(task.result)

    result = {
        'status': 'error',
        'message': 'unknown'
    }
    return JsonResponse(result, content_type='application/json', status=400)


def task(request):
    result = dict()
    if not request.user.is_authenticated:
        result['message'] = 'need auth'
        result['status'] = 'error'
        return JsonResponse(result, content_type='application/json', status=403)

    if request.method == 'POST':
        try:
            if 'name' not in request.POST:
                raise ValueError
            task = Tasks.objects.create(name=request.POST['name'],
                                        description=request.POST.get("description", None),
                                        user=request.user,
                                        state=Tasks.QUEUED)
            task.save()

            if 'params' in request.POST:
                for elem in request.POST['params']:
                    f = None
                    if 'file' in elem:
                        f = elem['file']
                    p = Params.objects.create(task=task,
                                              args=elem['args'],
                                              file=f)
                    p.save()

            execute_task.delay(task.pk)

            result['correct_task_name'] = request.POST['name']
            result['status'] = 'ok'
        except ValueError:
            result['incorrect_task_time'] = request.POST['time']
            result['incorrect_task_name'] = request.POST['name']
            result['status'] = 'error'
    elif request.method == 'DELETE':
        request.method = "POST"
        request._load_post_and_files()
        request.method = "DELETE"
        id = request.POST.get('id', None)
        flag = False
        task = None
        if id is not None:
            try:
                id = int(id)
                task = Tasks.objects.get(id=id)
                if task.user != request.user:
                    result['message'] = 'incorrect user'
                    result['status'] = 'error'
                    return JsonResponse(result,
                                        content_type='application/json',
                                        status=403)
                flag = True
            except :
                pass
        if flag and task:
            task.delete()
            result['state'] = 'ok'
        else:
            result['message'] = 'incorrect task'
            result['status'] = 'error'
    else:
        id = request.GET.get('id', None)
        flag = False
        task = None
        if id is not None:
            try:
                id = int(id)
                task = Tasks.objects.get(id=id)
                if task.user != request.user:
                    result['message'] = 'incorrect user'
                    result['status'] = 'error'
                    return JsonResponse(result,
                                        content_type='application/json',
                                        status=403)
                flag = True
            except :
                pass
        if flag and task:
            result["info"] = {
                'task_state': state_dict[task.state],
                'name': task.name,
                'description': task.description,
                'start_time': task.accept_time,
            }
            if task.result:
                result['result'] = {
                    "file":task.result.url,
                    "log": task.log,
                }
            params = list()
            for param in Params.objects.filter(task=task):
                elem = {
                    "args": param.args,
                }
                if param.file:
                    elem['file'] = param.file.url
                params.append(elem)
            result['params'] = params
            result['status'] = 'ok'

        else:
            tasks_descr = list()
            tasks = Tasks.objects.filter(user=request.user)
            for task in tasks:
                tasks_descr.append({
                    'id': task.id,
                    'name': task.name,
                    'state': state_dict[task.state]
                }
                )

            result['tasks'] = tasks_descr
            result['status'] = 'ok'

    return JsonResponse(result, content_type='application/json')
