import re
import ujson
from sanic.response import json
from sanic import Blueprint

from connections import get_client

task_bp = Blueprint('task')

task_query_regex = re.compile('source\[(.*)\]')


@task_bp.route('/cancle', methods=['POST'])
async def cancle_task(request):
    client = get_client(request)
    task_id = request.json['taskId']
    await client.tasks.cancle(task_id=task_id)
    return json({"status": "ok"})


@task_bp.route('/list')
async def list_tasks(request):
    result = []
    client = get_client(request)
    tasks = await client.tasks.list(detailed=True, group_by='parents')
    for task_id, task in tasks['tasks'].items():
        formatted = {
            "taskId": task_id,
            "action": task['action'],
            "running_time_in_ms": task["running_time_in_nanos"] / 1_000_000,
            "cancellable": task["cancellable"],
            "nodeName": task['node'],
        }
        if task['description']:
            formatted['description'] = task['description']
            query = task_query_regex.search(task['description'])
            if query is not None:
                formatted['query'] = ujson.loads(query.groups()[0])
        formatted['children'] = [{
            "node": child["node"],
            "type": child["type"],
            "action": child["action"]
        } for child in task.get('children', [])]
        result.append(formatted)
    return json(result)
