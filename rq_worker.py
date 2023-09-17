from flask import Flask
from rq import Worker, Queue, Connection
import redis

from src import app


conn = redis.from_url(app.config['RQ_DSN'])

with app.app_context():
    worker = Worker(list(Queue.all()), connection=conn)
    worker.work()
