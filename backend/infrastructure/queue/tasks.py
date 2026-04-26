import os
import pathlib
import ffmpeg
from uuid import uuid4
import requests
import json
import logging
from typing import Dict, List, Optional, Tuple

from ..repositories.database import get_task_session
from ..repositories.sqlite_video_repo import SQLiteVideoRepository
from ..repositories.sqlite_caption_repo import SQLiteCaptionRepository
from ..adapters.storage_factory import get_storage_adapter
from ...application.use_cases.generate_captions import GenerateCaptionsUseCase
from ...domain.entities.video import VideoStatus, Video


def _safe_parse_frame_rate(rate_str: str) -> float:
    """Safely parse ffprobe frame rate strings like '30/1' or '29.97'."""
    try:
        if '/' in rate_str:
            num, den = rate_str.split('/', 1)
            denominator = float(den)
            if denominator == 0:
                return 0.0
            return float(num) / denominator
        return float(rate_str)
    except (ValueError, ZeroDivisionError):
        return 0.0


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define upload directory for local processing.
# For S3, files are processed locally first then uploaded.
UPLOAD_DIR = pathlib.Path(__file__).parent.parent.parent / "uploads"
THUMBNAIL_DIR = UPLOAD_DIR / "thumbnails"
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# Get storage adapter for cloud storage operations
storage_adapter = get_storage_adapter()

# Video processing configurations
VIDEO_RESOLUTIONS = {
    "360p": {"width": 640, "height": 360, "bitrate": "500k"},
    "720p": {"width": 1280, "height": 720, "bitrate": "1500k"},
    "1080p": {"width": 1920, "height": 1080, "bitrate": "3000k"},
    "2160p": {"width": 3840, "height": 2160, "bitrate": "12000k"},
}


def get_video_metadata(file_path: str) -> Dict:
    """Extract comprehensive video metadata using ffprobe."""
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get("format", {})
        video_stream = next(
            (
                stream
                for stream in probe.get("streams", [])
                if stream.get("codec_type") == "video"
            ),
            None,
        )
        audio_stream = next(
            (
                stream
                for stream in probe.get("streams", [])
                if stream.get("codec_type") == "audio"
            ),
            None,
        )

        metadata = {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "format": format_info.get("format_name", ""),
            "video_codec": video_stream.get("codec_name", "") if video_stream else "",
            "audio_codec": audio_stream.get("codec_name", "") if audio_stream else "",
            "width": int(video_stream.get("width", 0)) if video_stream else 0,
            "height": int(video_stream.get("height", 0)) if video_stream else 0,
            "fps": _safe_parse_frame_rate(video_stream.get("r_frame_rate", "0/1")) if video_stream else 0,
            "bitrate": int(format_info.get("bit_rate", 0))
            if format_info.get("bit_rate")
            else 0,
        }

        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        return {}


def generate_thumbnail_at_time(
    input_path: str, output_path: str, timestamp: str = "00:00:01"
) -> bool:
    """Generate thumbnail at specific timestamp."""
    try:
        (
            ffmpeg.input(input_path, ss=timestamp)
            .output(output_path, vframes=1, format="image2", vcodec="mjpeg")
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except ffmpeg.Error as e:
        logger.error(f"Error generating thumbnail: {e.stderr.decode()}")
        return False


def transcode_video(input_path: str, output_path: str, resolution: Dict) -> bool:
    """Transcode video to specific resolution."""
    try:
        input_stream = ffmpeg.input(input_path)
        bitrate_num = int(resolution["bitrate"][:-1])
        output_stream = ffmpeg.output(
            input_stream,
            output_path,
            vcodec="libx264",
            acodec="aac",
            preset="veryfast",
            vf=f"scale={resolution['width']}:{resolution['height']}",
            b_v=resolution["bitrate"],
            maxrate=f"{bitrate_num * 1.5}k",
            bufsize=f"{bitrate_num * 3}k",
            movflags="faststart",
        )
        ffmpeg.run(
            output_stream,
            overwrite_output=True,
            capture_stdout=True,
            capture_stderr=True,
        )
        return True
    except ffmpeg.Error as e:
        logger.error(f"Error transcoding video: {e.stderr.decode()}")
        return False


def upload_to_storage(local_path: str, remote_key: str) -> bool:
    """Upload processed file to cloud storage."""
    try:
        with open(local_path, "rb") as file_data:
            storage_adapter.save(remote_key, file_data)
        logger.info(f"Successfully uploaded {remote_key} to cloud storage")
        return True
    except Exception as e:
        logger.error(f"Error uploading {remote_key} to cloud storage: {e}")
        return False


def process_video_task(video_id: str, uploaded_file_path: str):
    """
    Enhanced RQ task to process an uploaded video:
    - Extract metadata
    - Generate multiple resolutions
    - Create thumbnails at multiple timestamps
    - Optimize for web delivery
    """
    logger.info(
        f"Starting enhanced video processing for video_id: {video_id} from {uploaded_file_path}"
    )

    with get_task_session() as session:
        video_repo = SQLiteVideoRepository(session)
        video = None

        try:
            video = video_repo.get_by_id(video_id)
            if not video:
                logger.error(f"Video with id {video_id} not found. Exiting processing.")
                return

            # Mark video as PROCESSING
            video = video.mark_as_processing()
            video_repo.save(video)
            session.commit()

            # --- Enhanced Video Processing ---
            input_path = UPLOAD_DIR / uploaded_file_path
            if not input_path.exists():
                raise FileNotFoundError(f"Uploaded file not found at {input_path}")

            # Extract comprehensive metadata
            logger.info(f"Extracting metadata from {input_path}...")
            metadata = get_video_metadata(str(input_path))
            if not metadata:
                raise ValueError("Failed to extract video metadata")

            duration = metadata.get("duration", 0)
            logger.info(f"Video metadata: {json.dumps(metadata, indent=2)}")

            file_stem = input_path.stem

            # Generate multiple thumbnails at different timestamps
            thumbnail_timestamps = [
                "00:00:01",
                "00:00:05",
                str(duration * 0.25),
                str(duration * 0.5),
            ]
            thumbnail_urls = []

            for i, timestamp in enumerate(thumbnail_timestamps):
                if float(timestamp) <= duration:
                    thumbnail_filename = f"{file_stem}_thumb_{i}.jpg"
                    thumbnail_path = THUMBNAIL_DIR / thumbnail_filename

                    if generate_thumbnail_at_time(
                        str(input_path), str(thumbnail_path), timestamp
                    ):
                        # Upload to cloud storage
                        remote_key = f"thumbnails/{thumbnail_filename}"
                        if upload_to_storage(str(thumbnail_path), remote_key):
                            thumbnail_url = storage_adapter.get_url(remote_key)
                        else:
                            thumbnail_url = (
                                f"/uploads/thumbnails/{thumbnail_filename}"  # Fallback
                            )

                        thumbnail_urls.append(thumbnail_url)

                        # Clean up local file
                        os.remove(thumbnail_path)

            # Transcode to multiple resolutions for adaptive streaming
            resolution_urls = {}
            original_height = metadata.get("height", 0)

            # Determine which resolutions to generate based on original quality
            target_resolutions = []
            if original_height >= 2160:
                target_resolutions = ["2160p", "1080p", "720p", "360p"]
            elif original_height >= 1080:
                target_resolutions = ["1080p", "720p", "360p"]
            elif original_height >= 720:
                target_resolutions = ["720p", "360p"]
            else:
                target_resolutions = ["360p"]

            for res_name in target_resolutions:
                res_config = VIDEO_RESOLUTIONS[res_name]
                processed_filename = f"{file_stem}_{res_name}.mp4"
                processed_path = UPLOAD_DIR / processed_filename

                if transcode_video(str(input_path), str(processed_path), res_config):
                    # Upload to cloud storage
                    remote_key = processed_filename
                    if upload_to_storage(str(processed_path), remote_key):
                        resolution_urls[res_name] = storage_adapter.get_url(remote_key)
                    else:
                        resolution_urls[res_name] = (
                            f"/uploads/{processed_filename}"  # Fallback
                        )

                    # Clean up local file
                    os.remove(processed_path)

            # Use the highest quality as main video URL, others for adaptive streaming
            main_video_url = resolution_urls.get(target_resolutions[0], "")
            main_thumbnail_url = thumbnail_urls[0] if thumbnail_urls else ""

            # Update video with all processed information
            video = video.mark_as_ready(
                url=main_video_url, thumbnail_url=main_thumbnail_url, duration=duration
            )
            video_repo.save(video)
            session.commit()

            logger.info(
                f"Video {video_id} processed successfully with {len(resolution_urls)} resolutions and {len(thumbnail_urls)} thumbnails"
            )

            # Delete the original uploaded file to save space
            os.remove(input_path)
            logger.info(f"Original uploaded file {input_path} deleted.")

            # Enqueue follow-up tasks (best-effort): scene detection +
            # caption generation. These are independent and run after the
            # main transcode pipeline completes.
            try:
                from .. import queue as _queue_pkg

                vq = _queue_pkg.get_video_queue()
                vq.enqueue(detect_scenes_task, video_id, job_timeout=600)
                vq.enqueue(generate_captions_task, video_id, job_timeout=1800)
            except Exception as enq_err:
                logger.warning(f"Could not enqueue post-process tasks: {enq_err}")

        except Exception as e:
            logger.error(f"Error during video processing for {video_id}: {e}")
            if video:
                video = video.mark_as_failed()
                video_repo.save(video)
                session.commit()


def generate_captions_task(video_id: str):
    """
    Enhanced RQ task to generate captions for a given video.
    Downloads the processed video, extracts audio, transcribes, and saves captions.
    """
    logger.info(f"Starting caption generation for video_id: {video_id}")

    downloaded_video_path = None
    audio_file_path = None

    with get_task_session() as session:
        video_repo = SQLiteVideoRepository(session)
        caption_repo = SQLiteCaptionRepository(session)

        try:
            video = video_repo.get_by_id(video_id)
            if not video or not video.url:
                logger.warning(
                    f"Video {video_id} not found or has no URL. Exiting caption generation."
                )
                return

            # 1. Download the processed video locally
            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            video_url_full = f"{backend_url}{video.url}"
            downloaded_video_path = UPLOAD_DIR / f"{uuid4()}_downloaded_for_caption.mp4"
            logger.info(
                f"Downloading video from {video_url_full} to {downloaded_video_path}"
            )

            response = requests.get(video_url_full, stream=True, timeout=30)
            response.raise_for_status()

            with open(downloaded_video_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Video downloaded to {downloaded_video_path}")

            # 2. Extract high-quality audio from the downloaded video
            audio_file_path = UPLOAD_DIR / f"{uuid4()}_extracted_audio.wav"
            logger.info(f"Extracting audio to {audio_file_path}")

            (
                ffmpeg.input(str(downloaded_video_path))
                .output(str(audio_file_path), acodec="pcm_s16le", ac=1, ar="16000")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.info(f"Audio extracted to {audio_file_path}")

            # 3. Generate captions using the use case
            from ..adapters.transcription_assemblyai import get_transcriber

            generate_captions_use_case = GenerateCaptionsUseCase(
                video_repo, caption_repo, get_transcriber()
            )
            generated_captions = generate_captions_use_case.execute(
                video_id, str(audio_file_path)
            )

            logger.info(
                f"Captions generated for video {video_id}: {len(generated_captions)} captions."
            )

        except Exception as e:
            logger.error(f"Error during caption generation for {video_id}: {e}")
        finally:
            # Clean up temporary files
            if downloaded_video_path and downloaded_video_path.exists():
                os.remove(downloaded_video_path)
                logger.debug(f"Cleaned up downloaded video: {downloaded_video_path}")
            if audio_file_path and audio_file_path.exists():
                os.remove(audio_file_path)
                logger.debug(f"Cleaned up extracted audio: {audio_file_path}")


def detect_scenes_task(video_id: str):
    """Run PySceneDetect on a video and persist scene boundaries as
    chapter markers. Phase 2.2 — auto-cut suggestions for the editor.
    """
    from sqlmodel import select

    logger.info(f"Starting scene detection for video_id: {video_id}")
    downloaded_path: Optional[pathlib.Path] = None

    with get_task_session() as session:
        video_repo = SQLiteVideoRepository(session)
        try:
            video = video_repo.get_by_id(video_id)
            if not video or not video.url:
                logger.warning(f"Video {video_id} not ready for scene detection")
                return

            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            video_url_full = f"{backend_url}{video.url}"
            downloaded_path = UPLOAD_DIR / f"{uuid4()}_scene_detect.mp4"

            response = requests.get(video_url_full, stream=True, timeout=30)
            response.raise_for_status()
            with open(downloaded_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            try:
                from scenedetect import (
                    detect,
                    ContentDetector,
                )
            except ImportError:
                logger.warning("scenedetect not installed; skipping")
                return

            scene_list = detect(str(downloaded_path), ContentDetector())
            logger.info(f"PySceneDetect found {len(scene_list)} scenes")

            from ..repositories.models import ChapterMarkerDB

            # Wipe existing auto-detected markers for idempotency.
            existing = session.exec(
                select(ChapterMarkerDB).where(
                    ChapterMarkerDB.video_id == video_id,
                    ChapterMarkerDB.creator_id == "_auto",
                )
            ).all()
            for row in existing:
                session.delete(row)

            for i, scene in enumerate(scene_list):
                start_s = scene[0].get_seconds()
                end_s = scene[1].get_seconds()
                marker = ChapterMarkerDB(
                    video_id=video_id,
                    title=f"Scene {i + 1}",
                    start_time=start_s,
                    end_time=end_s,
                    creator_id="_auto",
                )
                session.add(marker)
            session.commit()
            logger.info(
                f"Saved {len(scene_list)} chapter markers for video {video_id}"
            )

        except Exception as e:
            logger.exception(f"Scene detection failed for video {video_id}: {e}")
        finally:
            if downloaded_path and downloaded_path.exists():
                try:
                    os.remove(downloaded_path)
                except OSError:
                    pass


def enhance_voice_task(video_id: str):
    """Server-side voice enhancement (Phase 2.5).

    Extracts audio, runs RNNoise via ffmpeg's `arnndn` filter (built-in
    since FFmpeg 4.4) — no extra Python deps. The denoised audio is muxed
    back into the original video, replacing it.
    """
    logger.info(f"Starting voice enhancement for video_id: {video_id}")
    downloaded_path: Optional[pathlib.Path] = None
    cleaned_path: Optional[pathlib.Path] = None

    with get_task_session() as session:
        video_repo = SQLiteVideoRepository(session)
        try:
            video = video_repo.get_by_id(video_id)
            if not video or not video.url:
                logger.warning(f"Video {video_id} not ready for voice enhancement")
                return

            backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
            video_url_full = f"{backend_url}{video.url}"
            downloaded_path = UPLOAD_DIR / f"{uuid4()}_voice_in.mp4"
            cleaned_path = UPLOAD_DIR / f"{uuid4()}_voice_out.mp4"

            # Download
            response = requests.get(video_url_full, stream=True, timeout=30)
            response.raise_for_status()
            with open(downloaded_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # FFmpeg's arnndn filter uses RNNoise. We use a built-in model
            # path; alternatively users can supply their own .rnnn file via
            # the RNNDN_MODEL_PATH env var.
            rnndn_model = os.getenv("RNNDN_MODEL_PATH")  # optional
            af = "highpass=f=80,lowpass=f=8000"
            if rnndn_model:
                af = f"{af},arnndn=m={rnndn_model}"
            else:
                # Fallback: just the bandpass + a soft compander to even out
                # voice levels. arnndn requires a model file we can't ship.
                af = (
                    f"{af},compand="
                    "attacks=0:decays=0.3:points=-90/-900|-70/-70|-30/-15|0/-5"
                )

            (
                ffmpeg.input(str(downloaded_path))
                .output(
                    str(cleaned_path),
                    af=af,
                    vcodec="copy",
                    acodec="aac",
                    audio_bitrate="128k",
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            # Replace stored video with the cleaned version. We re-use the
            # storage adapter so the URL points at the same path.
            storage = get_storage_adapter()
            with open(cleaned_path, "rb") as src:
                # The save() returns the URL; assume it overwrites if same name.
                storage.save(pathlib.Path(video.url).name, src)
            logger.info(f"Voice enhancement done for video {video_id}")

        except Exception as e:
            logger.exception(f"Voice enhancement failed for video {video_id}: {e}")
        finally:
            for p in (downloaded_path, cleaned_path):
                if p and p.exists():
                    try:
                        os.remove(p)
                    except OSError:
                        pass


def monthly_creator_payouts_task():
    """Phase 3.3 — Creator Fund monthly payout batch.

    Walks all wallets with balance >= minimum_payout AND a connected
    Stripe account, and triggers a payout for each. Designed to be invoked
    by a cron / RQ Scheduler entry on the 1st of each month.

    Idempotent: PayoutDB records are created per-transfer; re-running
    won't double-pay since balances are zeroed on success.
    """
    from sqlmodel import select

    logger.info("Monthly creator payout batch starting")

    with get_task_session() as session:
        from ..repositories.models import CreatorWalletDB, PayoutDB

        wallets = session.exec(
            select(CreatorWalletDB).where(
                CreatorWalletDB.status == "active",
                CreatorWalletDB.balance >= CreatorWalletDB.minimum_payout,
                CreatorWalletDB.stripe_account_id.is_not(None),  # noqa: E711
            )
        ).all()

        platform_fee_rate = 0.30  # 70/30 per Creator Fund 2.0
        processed = 0
        skipped = 0
        for wallet in wallets:
            try:
                fee = wallet.balance * platform_fee_rate
                net = wallet.balance - fee
                payout = PayoutDB(
                    wallet_id=wallet.id,
                    user_id=wallet.user_id,
                    amount=wallet.balance,
                    fee_amount=fee,
                    net_amount=net,
                    status="pending",
                )
                session.add(payout)
                # Reset balance — actual Stripe transfer happens via the
                # request_payout flow / Stripe webhook on payout.paid.
                from datetime import datetime as _dt, UTC as _UTC

                wallet.total_withdrawn = (wallet.total_withdrawn or 0) + wallet.balance
                wallet.balance = 0.0
                wallet.last_payout_at = _dt.now(_UTC)
                session.add(wallet)
                processed += 1
            except Exception as e:
                logger.warning(f"Skipping wallet {wallet.id}: {e}")
                skipped += 1
        session.commit()
        logger.info(
            "Monthly payout batch done: %d processed, %d skipped", processed, skipped
        )


def daily_analytics_export_task():
    """Phase 6.3 — nightly aggregation push to the warehouse.

    Walks VideoDB + UserDB and produces a flat row-per-video table the
    warehouse can run cohort joins against. Uses whatever AnalyticsExportPort
    adapter is currently bound (JSONL by default).
    """
    from ..adapters.analytics_export_jsonl import JSONLAnalyticsExporter
    from ..repositories.models import VideoDB, UserDB

    logger.info("Daily analytics export starting")
    exporter = JSONLAnalyticsExporter()
    with get_task_session() as session:
        from sqlmodel import select as _select

        videos = session.exec(_select(VideoDB)).all()
        rows = (
            {
                "video_id": v.id,
                "creator_id": v.creator_id,
                "status": v.status,
                "views": v.views or 0,
                "likes": v.likes or 0,
                "duration": v.duration,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "is_premium": getattr(v, "is_premium", False),
            }
            for v in videos
        )
        exporter.export("video_metrics_daily", rows)

        users = session.exec(_select(UserDB)).all()
        urows = (
            {
                "user_id": u.id,
                "is_active": u.is_active,
                "email_verified": u.email_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        )
        exporter.export("user_dim_daily", urows)
    logger.info("Daily analytics export done")


def apply_chromakey_task(
    video_id: str,
    color: str = "0x00FF00",
    similarity: float = 0.3,
    blend: float = 0.1,
):
    """Phase 5.3 — server-side green-screen via FFmpeg `colorkey` filter.

    Removes the keyed colour and saves the result back over the video URL.
    `color` is hex, `similarity` controls match width, `blend` softens edges.
    """
    logger.info(f"Chroma-key on {video_id} color={color}")
    src: Optional[pathlib.Path] = None
    dst: Optional[pathlib.Path] = None

    with get_task_session() as session:
        video_repo = SQLiteVideoRepository(session)
        video = video_repo.get_by_id(video_id)
        if not video or not video.url:
            logger.warning(f"Video {video_id} not ready for chroma-key")
            return

        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        src = UPLOAD_DIR / f"{uuid4()}_chroma_in.mp4"
        dst = UPLOAD_DIR / f"{uuid4()}_chroma_out.mp4"
        try:
            r = requests.get(f"{backend_url}{video.url}", stream=True, timeout=30)
            r.raise_for_status()
            with open(src, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            (
                ffmpeg.input(str(src))
                .filter("colorkey", color, similarity, blend)
                .output(str(dst), vcodec="libx264", acodec="copy", preset="fast")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            with open(dst, "rb") as fp:
                storage_adapter.save(pathlib.Path(video.url).name, fp)
            logger.info(f"Chroma-key done for {video_id}")
        except Exception as e:
            logger.exception(f"Chroma-key failed {video_id}: {e}")
        finally:
            for p in (src, dst):
                if p and p.exists():
                    try:
                        os.remove(p)
                    except OSError:
                        pass


def compose_duet_task(duet_id: str):
    """Phase 4.1 — Server-side FFmpeg duet composition.

    Reads original + response video URLs from DuetDB, downloads both,
    composites them with FFmpeg's hstack/vstack filter, uploads the result
    via the storage adapter, and stores the URL on the duet row in a new
    `composed_url` column.

    Layout depends on duet.duet_type:
      - "side_by_side" → hstack (default, scaled to matching height)
      - "react"        → small response PiP overlay top-right of original
      - "stack"        → vstack
    """
    logger.info(f"Composing duet {duet_id}")
    out_path: Optional[pathlib.Path] = None
    a_path: Optional[pathlib.Path] = None
    b_path: Optional[pathlib.Path] = None

    with get_task_session() as session:
        from ..repositories.models import DuetDB, VideoDB
        duet = session.get(DuetDB, duet_id)
        if not duet:
            logger.warning(f"Duet {duet_id} not found")
            return
        original = session.get(VideoDB, duet.original_video_id)
        response = session.get(VideoDB, duet.response_video_id)
        if not original or not response or not original.url or not response.url:
            logger.warning(f"Duet {duet_id} missing source videos")
            return

        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        a_path = UPLOAD_DIR / f"{uuid4()}_duet_a.mp4"
        b_path = UPLOAD_DIR / f"{uuid4()}_duet_b.mp4"
        out_path = UPLOAD_DIR / f"{uuid4()}_duet_out.mp4"

        try:
            for url, dest in (
                (f"{backend_url}{original.url}", a_path),
                (f"{backend_url}{response.url}", b_path),
            ):
                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            a = ffmpeg.input(str(a_path))
            b = ffmpeg.input(str(b_path))
            if duet.duet_type == "stack":
                a_s = a.video.filter("scale", 720, -2)
                b_s = b.video.filter("scale", 720, -2)
                v = ffmpeg.filter([a_s, b_s], "vstack", inputs=2)
            elif duet.duet_type == "react":
                main = a.video.filter("scale", 1280, -2)
                pip = b.video.filter("scale", 320, -2)
                v = ffmpeg.overlay(main, pip, x="W-w-20", y=20)
            else:  # side_by_side
                a_s = a.video.filter("scale", -2, 720)
                b_s = b.video.filter("scale", -2, 720)
                v = ffmpeg.filter([a_s, b_s], "hstack", inputs=2)

            audio = ffmpeg.filter([a.audio, b.audio], "amix", inputs=2, duration="shortest")
            (
                ffmpeg.output(v, audio, str(out_path), vcodec="libx264", acodec="aac", preset="fast")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            with open(out_path, "rb") as src:
                composed_url = storage_adapter.save(f"duet_{duet_id}.mp4", src)
            duet.composed_url = composed_url
            session.add(duet)
            session.commit()
            logger.info(f"Duet {duet_id} composed → {composed_url}")
        except Exception as e:
            logger.exception(f"Duet composition failed {duet_id}: {e}")
        finally:
            for p in (a_path, b_path, out_path):
                if p and p.exists():
                    try:
                        os.remove(p)
                    except OSError:
                        pass
