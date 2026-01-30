"""
FK94 Security Platform - Background Job Worker
"""
import asyncio
from datetime import datetime, timezone

from app.core.config import settings
from app.models.schemas import FullAuditRequest, MultiAuditRequest
from app.services import job_store
from app.services.audit_runner import run_full_audit, run_multi_audit


class JobWorker:
    def __init__(self, db_path: str, poll_seconds: int = 5):
        self.db_path = db_path
        self.poll_seconds = max(1, poll_seconds)
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task:
            await self._task

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            await self._process_due_jobs()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.poll_seconds)
            except asyncio.TimeoutError:
                continue

    async def _process_due_jobs(self) -> None:
        jobs = job_store.fetch_due_jobs(self.db_path, limit=3)
        for job in jobs:
            await self._process_job(job)

    async def _process_job(self, job: dict) -> None:
        job_id = job["id"]
        job_type = job["job_type"]
        payload = job["payload"]

        job_store.update_job(
            self.db_path,
            job_id,
            status="running",
            started_at=self._utc_now(),
        )

        try:
            if job_type == "full_audit":
                request = FullAuditRequest(**payload)
                result = await run_full_audit(request)
                job_store.update_job(
                    self.db_path,
                    job_id,
                    status="completed",
                    result=result.model_dump(),
                    finished_at=self._utc_now(),
                )
            elif job_type == "multi_audit":
                request = MultiAuditRequest(**payload)
                result = await run_multi_audit(request)
                job_store.update_job(
                    self.db_path,
                    job_id,
                    status="completed",
                    result=result.model_dump(),
                    finished_at=self._utc_now(),
                )
            else:
                job_store.update_job(
                    self.db_path,
                    job_id,
                    status="failed",
                    error=f"Unknown job type: {job_type}",
                    finished_at=self._utc_now(),
                )
        except Exception as exc:
            job_store.update_job(
                self.db_path,
                job_id,
                status="failed",
                error=str(exc),
                finished_at=self._utc_now(),
            )

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()


job_worker = JobWorker(settings.JOB_DB_PATH, settings.JOB_WORKER_POLL_SECONDS)
