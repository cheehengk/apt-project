from redis import Redis
from rq import Worker, Queue, Connection
from flask_app.src.scripter import main
from dotenv import dotenv_values

env_vars = dotenv_values("flask_app/src/.env")
redis_host = env_vars.get("REDIS_HOST")
redis_port = env_vars.get("REDIS_PORT")
redis_pw = env_vars.get("REDIS_PW")

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
