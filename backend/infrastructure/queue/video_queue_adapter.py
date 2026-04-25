from uuid import UUID

from backend.domain.ports.queue_port import VideoQueuePort

from ..queue import get_video_queue
from .tasks import process_video_task


class RQVideoQueueAdapter(VideoQueuePort):
    def __init__(self, file_path_resolver):
        """file_path_resolver: callable(video_id) -> filesystem path."""
        self._queue = get_video_queue()
        self._resolve_path = file_path_resolver

    def enqueue_video_processing(self, video_id: UUID) -> None:
        path = self._resolve_path(video_id)
        self._queue.enqueue(process_video_task, video_id, path, job_timeout=3600)
