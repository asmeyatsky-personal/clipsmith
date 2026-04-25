import uuid
from typing import BinaryIO

from ...domain.entities.video import Video, VideoStatus
from ...domain.ports.queue_port import VideoQueuePort
from ...domain.ports.repository_ports import HashtagRepositoryPort, VideoRepositoryPort
from ...domain.ports.storage_port import StoragePort
from ..dtos.video_dto import VideoCreateDTO, VideoResponseDTO
from ..services.hashtag_service import HashtagService


class UploadVideoUseCase:
    def __init__(
        self,
        video_repo: VideoRepositoryPort,
        storage_adapter: StoragePort,
        hashtag_repo: HashtagRepositoryPort,
        video_queue: VideoQueuePort,
    ):
        self._video_repo = video_repo
        self._storage_adapter = storage_adapter
        self._hashtag_repo = hashtag_repo
        self._hashtag_service = HashtagService(hashtag_repo)
        self._video_queue = video_queue

    def execute(
        self, dto: VideoCreateDTO, file_data: BinaryIO, filename: str
    ) -> VideoResponseDTO:
        unique_filename = f"{uuid.uuid4()}_{filename}"
        uploaded_file_path = self._storage_adapter.save(unique_filename, file_data)

        video = Video(
            title=dto.title,
            description=dto.description,
            creator_id=dto.creator_id,
            status=VideoStatus.UPLOADING,
        )

        saved_video = self._video_repo.save(video)

        self._hashtag_service.process_video_hashtags(
            saved_video.id, dto.title, dto.description
        )

        self._video_queue.enqueue_video_processing(saved_video.id)

        return VideoResponseDTO(
            id=saved_video.id,
            title=saved_video.title,
            description=saved_video.description,
            creator_id=saved_video.creator_id,
            status=saved_video.status,
            url=None,
            thumbnail_url=None,
            views=saved_video.views,
            likes=saved_video.likes,
            duration=saved_video.duration,
        )
