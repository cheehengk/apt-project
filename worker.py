import os

from redis import Redis
from rq import Worker, Queue, Connection
from flask_app.src.scripter import main
from dotenv import load_dotenv

# load_dotenv()
redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_pw = os.environ.get("REDIS_PW")

listen = ['default']

if __name__ == '__main__':
    redis_conn = Redis(host='redis', port=6379, db=0)
    with Connection(connection=redis_conn):
        worker = Worker(map(Queue, listen))

        # @worker.perform_job
        # def perform_job(job):
        #     try:
        #         return job.perform()
        #     except Exception as e:
        #         return f'Error occurred: {str(e)}'

        worker.work()
