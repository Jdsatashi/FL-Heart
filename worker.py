import os

import redis
from rq import Worker, Queue, Connection

from src import app

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        app.app_context().push()  # Tạo ngữ cảnh ứng dụng
        worker = Worker(list(map(Queue, listen)))
        worker.work()