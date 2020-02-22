import psutil


def avg(x):
    total = 0.0
    for item in x:
        total += item
    return round(total/len(x)*100)/100


def cpu_usage():
    usage = psutil.cpu_percent(interval=None, percpu=True)
    cores = {}
    index = 0
    for cpu in usage:
        cores[index] = cpu
        index += 1
    return {'avg': avg(usage), 'max': max(usage), 'cores': cores}


def memory_usage():
    v = psutil.virtual_memory()
    return {
        'usedBytes': v.used,
        'usedPercent': v.percent}


def disk_usage_fn():
    disk_io = psutil.disk_io_counters()
    usage = {
        'read_count': disk_io.read_count,
        'write_count': disk_io.write_count,
        'read_bytes': disk_io.read_bytes,
        'write_bytes': disk_io.write_bytes
    }

    def disk_usage():
        nonlocal usage
        disk_io = psutil.disk_io_counters()
        result = {
            'readCount': disk_io.read_count - usage['read_count'],
            'writeCount': disk_io.write_count - usage['write_count'],
            'readBytes': disk_io.read_bytes - usage['read_bytes'],
            'writeBytes': disk_io.write_bytes - usage['write_bytes']
        }
        usage['read_count'] = disk_io.read_count
        usage['write_count'] = disk_io.write_count
        usage['read_bytes'] = disk_io.read_bytes
        usage['write_bytes'] = disk_io.write_bytes
        return result
    return disk_usage


def network_usage_fn():
    net_io = psutil.net_io_counters()
    usage = {
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv
    }

    def network_usage():
        nonlocal usage
        net_io = psutil.net_io_counters()
        result = {
            'bytesSent': net_io.bytes_sent - usage['bytes_sent'],
            'bytesReceived': net_io.bytes_recv - usage['bytes_recv']
        }
        usage['bytes_sent'] = net_io.bytes_sent
        usage['bytes_recv'] = net_io.bytes_recv
        return result
    return network_usage
