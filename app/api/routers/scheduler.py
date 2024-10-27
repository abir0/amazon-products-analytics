from fastapi import APIRouter

from scraper.scheduler import job_scheduler


router = APIRouter(prefix="/scheduler")


@router.get("/status")
async def get_scheduler_status():
    try:
        jobs = []
        for job in job_scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": (
                        job.next_run_time.isoformat() if job.next_run_time else None
                    ),
                    "trigger": str(job.trigger),
                    "status": "active" if job.next_run_time else "paused",
                }
            )

        return {
            "status": "running" if job_scheduler.running else "stopped",
            "jobs": jobs,
        }

    except Exception as e:
        print(f"Error getting scheduler status: {str(e)}")
        raise


# Scheduler control endpoints
@router.post("/pause/{job_id}")
async def pause_job(job_id: str):
    try:
        job_scheduler.pause_job(job_id)
        return {"message": f"Successfully paused job {job_id}"}
    except Exception as e:
        print(f"Error pausing job {job_id}: {str(e)}")
        raise


@router.post("/resume/{job_id}")
async def resume_job(job_id: str):
    try:
        job_scheduler.resume_job(job_id)
        return {"message": f"Successfully resumed job {job_id}"}
    except Exception as e:
        print(f"Error resuming job {job_id}: {str(e)}")
        raise
