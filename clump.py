#!/usr/bin/env python3
import asyncio
import copy
import json
import time

from aiohttp import web

import resources

routes = web.RouteTableDef()


@routes.get('/')
async def handle(request):
    since = request.query.get('since')
    if not since:
        return web.Response(status=400, text='Missing "since" url parameter')
    try:
        since = int(since)
    except ValueError:
        return web.Response(status=400, text='Could not parse "since" as int')
    raw = {}
    async with request.app['lock']:
        for k, v in request.app['resources'].items():
            if k >= since:
                raw[k] = copy.deepcopy(v)  # I fear this will be slow
    payload = json.dumps(raw)
    return web.Response(
        status=200, text=payload, content_type='application/json')


async def cleanup(app):
    # not the prettiest but does the job
    keep_records = 10
    cleanup_every = 5
    try:
        while True:
            async with app['lock']:
                if len(app['resources']) > keep_records:
                    for k, v in app['resources'].copy().items():
                        if k <= app['info']['latest']-keep_records:
                            del app['resources'][k]
            await asyncio.sleep(cleanup_every)
    except asyncio.CancelledError:
        pass


async def monitor(now, disk_usage, network_usage, app):
    try:
        key = int(now)
        cpu = resources.cpu_usage()
        mem = resources.memory_usage()
        disk = disk_usage()
        net = network_usage()
        async with app['lock']:
            app['info']['latest'] = key
            app['resources'][key] = {
                'cpu': cpu,
                'memory': mem,
                'disk': disk,
                'network': net}
    except asyncio.CancelledError:
        pass


async def cron(app):
    try:
        # sleep till almost exactly on the second #good_enough
        await asyncio.sleep(1 - (time.time() % 1))
        disk_usage = resources.disk_usage_fn()
        network_usage = resources.network_usage_fn()
        await asyncio.sleep(1 - (time.time() % 1))
        while True:
            now = time.time()
            asyncio.create_task(monitor(now, disk_usage, network_usage, app))
            await asyncio.sleep(1 - (now % 1))
    except asyncio.CancelledError:
        pass


async def start_tasks(app):
    asyncio.create_task(cron(app))
    asyncio.create_task(cleanup(app))


async def cancel_tasks(app):
    pending = asyncio.Task.all_tasks()
    for task in pending:
        task.cancel()
        await task


if __name__ == '__main__':
    app = web.Application()
    app['info'] = {'latest': 0}
    app['resources'] = {}
    app['lock'] = asyncio.Lock()
    app.add_routes(routes)
    app.on_startup.append(start_tasks)
    app.on_cleanup.append(cancel_tasks)
    web.run_app(app)
