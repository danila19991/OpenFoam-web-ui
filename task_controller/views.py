from django.http import HttpResponse, JsonResponse
from .models import Tasks


def list_view(request):
    result = dict()
    if not request.user.is_authenticated:
        result['message'] = 'need auth'
        result['status'] = 'error'
        return JsonResponse(result, content_type='application/json', status=403)

    if request.method == 'POST':
        if 'time' in request.POST and 'name' in request.POST:
            try:
                val = int(request.POST['time'])
                name = request.POST['name']
                if val < 1 or val > 60:
                    raise ValueError
                task = Tasks.objects.create(name=name, time=val,
                                            user=request.user,
                                            state=Tasks.QUEUED)
                task.save()
                # execute_task.delay(task.pk)
                result['correct_task_name'] = request.POST['name']
                result['status'] = 'ok'
            except ValueError:
                result['incorrect_task_time'] = request.POST['time']
                result['incorrect_task_name'] = request.POST['name']
                result['status'] = 'error'
        else:
            result['message'] = 'field error'
            result['status'] = 'error'
    else:
        tasks_descr = list()
        tasks = Tasks.objects.filter(user=request.user)
        state_dict = {
            Tasks.QUEUED: 'queued',
            Tasks.IN_PROCESS: 'in progress',
            Tasks.ERRORED: 'errored',
            Tasks.FINISHED: 'finished',
        }
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
