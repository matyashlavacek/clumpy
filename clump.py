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
        for k, v in request.app['m'].items():
            if k >= since:
                raw[k] = copy.deepcopy(v)  # I fear this will be slow
    payload = json.dumps(raw)
    return web.Response(
        status=200, text=payload, content_type='application/json')


async def monitor(app):
    disk_usage = resources.disk_usage_fn()
    network_usage = resources.network_usage_fn()
    deviation = 0.01
    try:
        while True:
            now = time.time()
            # check if we're on the second (approximately)
            if now % 1 < deviation:
                key = int(now)
                # don't waste cycles inside a lock
                # also calculate immediately (in case lock would block a bit)
                cpu = resources.cpu_usage()
                mem = resources.memory_usage()
                disk = disk_usage()
                net = network_usage()
                async with app['lock']:
                    app['m'][key] = {
                        'cpu': cpu,
                        'memory': mem,
                        'disk': disk,
                        'network': net}
                # make sure we don't run twice in the same second
                await asyncio.sleep(deviation)
            await asyncio.sleep(1/200)
    except asyncio.CancelledError:
        pass


async def start_monitor(app):
    app['monitor'] = asyncio.create_task(monitor(app))


async def stop_monitor(app):
    app['monitor'].cancel()
    await app['monitor']


if __name__ == '__main__':
    app = web.Application()
    app['m'] = {}
    app['lock'] = asyncio.Lock()
    app.add_routes(routes)
    app.on_startup.append(start_monitor)
    app.on_cleanup.append(stop_monitor)
    web.run_app(app)
