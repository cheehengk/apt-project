from redis import Redis
from rq import Worker, Queue, Connection

listen = ['default']

if __name__ == '__main__':
    redis_conn = Redis()
    with Connection(connection=redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
