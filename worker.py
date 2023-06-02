import os

from redis import Redis
from rq import Worker, Queue, Connection
from flask_app.src.scripter import main
from dotenv import load_dotenv

load_dotenv()
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_pw = os.getenv("REDIS_PW")

listen = ['default']

if __name__ == '__main__':
    redis_conn = Redis(
        host=redis_host,
        port=int(redis_port),
        password=redis_pw
    )
    with Connection(connection=redis_conn):
        worker = Worker(map(Queue, listen))

        # @worker.perform_job
        # def perform_job(job):
        #     try:
        #         return job.perform()
        #     except Exception as e:
        #         return f'Error occurred: {str(e)}'

        worker.work()
