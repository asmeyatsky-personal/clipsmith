from abc import ABC, abstractmethod
from uuid import UUID


class VideoQueuePort(ABC):
    @abstractmethod
    def enqueue_video_processing(self, video_id: UUID) -> None: ...
