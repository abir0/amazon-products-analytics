from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

from config import get_config


config = get_config()

jobstores = {"default": SQLAlchemyJobStore(url=config.DATABASE_URL)}

executors = {
    "default": {"type": "threadpool", "max_workers": 20},
    "processpool": ProcessPoolExecutor(max_workers=5),
}

job_defaults = {
    "coalesce": False,
    "max_instances": 1,
    "misfire_grace_time": 3600,  # 1 hour grace time for missed jobs
}

job_scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="Asia/Dhaka",
)
