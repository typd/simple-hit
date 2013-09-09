import sys
from multiprocessing import Process, Queue

import requests

HIT_COUNT = 0
URL = sys.argv[1]

for _ in range(10):
    requests.get(URL)
    HIT_COUNT += 1
