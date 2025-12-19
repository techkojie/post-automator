# celery_worker.py
from app.tasks import celery
# run worker:
# celery -A celery_worker.celery worker --loglevel=info
if __name__ == "__main__":
    celery.start()
