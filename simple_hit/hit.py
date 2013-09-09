import sys
import time
import signal
from datetime import datetime
from multiprocessing import Process, Queue

import requests

WORKER_REFRESH_INTERVAL = 1
REFRESH_INTERVAL = 5
TIME_FORMAT = '%H:%M:%S'

PROCS = []
CMD_QUEUES = []

def signal_handler(sig, frame):
    print('exiting program')
    for queue in CMD_QUEUES:
        queue.put('stop')
    for proc in PROCS:
        proc.join()
    sys.exit(0)

def worker(index, queue, cmd_queue, url):
    count = 0
    print('process-{} started'.format(index))
    last_update_time = time.time()
    while cmd_queue.empty():
        requests.get(url)
        count += 1
        now = time.time()
        if now - last_update_time > WORKER_REFRESH_INTERVAL:
            queue.put(count)
            last_update_time = now
    print('process-{} ended: {}'.format(index, count))

def load_test(url, process_count=1):
    if not process_count:
        process_count = 1
    queues = []
    counts = []
    for index in range(process_count):
        queue = Queue()
        cmd_queue = Queue()
        proc = Process(target=worker, args=(index, queue, cmd_queue, url), daemon=True)
        proc.start()
        PROCS.append(proc)
        queues.append(queue)
        CMD_QUEUES.append(cmd_queue)
        counts.append(0)
    signal.signal(signal.SIGINT, signal_handler)
    start_time = time.time()
    last_time = start_time
    last_total = 0
    while True:
        total = 0
        for index in range(process_count):
            queue = queues[index]
            while not queue.empty():
                counts[index] = queue.get()
            total += counts[index]
        now = time.time()
        used_time = now - start_time
        print('{} [hit: {}, {:.2f} /s] [total: {}, used: {:.2f}, {:.2f} /s]'
                .format(
                        datetime.now().strftime(TIME_FORMAT),
                        total - last_total,
                        (total - last_total + 0.0) / (now - last_time),
                        total,
                        used_time,
                        (total + 0.0) / used_time))
        last_time = now
        last_total = total
        time.sleep(REFRESH_INTERVAL)

