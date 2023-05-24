from redis import Redis
from rq import Worker, Queue, Connection
from flask_app.src.scripter import main


listen = ['default']

if __name__ == '__main__':
    redis_conn = Redis()
    with Connection(connection=redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()

# def do_something(input):
#     print(input)
#     return 'received:{}'.format(input)
#
#
# if __name__ == '__main__':
#     redis = Redis(host='127.0.0.1', port=6379)
#     queue = Queue(name='queue_eee', connection=redis, serializer='rq.serializers.JSONSerializer')
#
#     # Start a worker with a custom name
#     worker = Worker([queue], connection=redis)
#     worker.work(with_scheduler=True)

# redis_conn = Redis()
# with Queue(connection=redis_conn) as queue:
#     job = queue.enqueue(do_something, 'test first time')
