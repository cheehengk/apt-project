import os
from flask import Flask
from redis import Redis
from rq import Worker, Queue, Connection
from flask_app.src.scripter import main


app = Flask(__name__)
# load_dotenv()
redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_pw = os.environ.get("REDIS_PW")

redis_conn = Redis(
    host=redis_host,
    port=int(redis_port),
    password=redis_pw
)


@app.route('/')
def process_tasks():
    listen = ['default']

    with Connection(connection=redis_conn):
        queues = [Queue(queue_name, connection=redis_conn) for queue_name in listen]
        worker = Worker(queues)
        worker.work()

    return 'Worker started successfully.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
