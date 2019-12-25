import os
import glob
import socket

from celery.utils.log import get_task_logger
from django.conf import settings
from moviepy.editor import concatenate_videoclips, VideoFileClip

from core.celery import app
from core.utils import is_file_locked
from videos.models import Video
from videos.models import EmailRequest
from datetime import datetime

from .emails import send_video_email

logger = get_task_logger(__name__)


@app.task(bind=True)
def send_video_email_task(self, email, video):
    logger.info("Sending Email...")
    try:
        request = EmailRequest.objects.create(
            email=email,
            video=video
        )
        send_video_email(email, video)
    except socket.gaierror as exc:
        logger.error(str(exc))
        logger.error("Failed to send email" + " : " + email)
    else:
        logger.info("Succeed to sent email: " + email)
        request.delete()


@app.task
def email_request_listening():
    logger.info("Processing buffered email request...")
    try:
        request = EmailRequest.objects.latest('pk')
        send_video_email(request.email, request.video)
    except EmailRequest.DoesNotExist:
        logger.info('No buffered email request')
    except Exception as e:
        logger.error(e)
        logger.error("Failed to send email")
    else:
        logger.info("Succeed to sent email: " + request.email)
        request.delete()


@app.task
def folder_listening():
    logger.info("Watching: " + settings.WATCHING_DIR)

    # get all mp4 files in watching folder
    os.chdir(settings.WATCHING_DIR)
    for file_ in glob.glob("*.mp4"):
        # check file's lock status
        if not is_file_locked(os.path.join(settings.WATCHING_DIR, file_), logger):
            filepath = os.path.join(settings.WATCHING_DIR, file_)
            current_change_time = datetime.fromtimestamp(os.path.getctime(filepath))

            # check if the file processed already
            try:
                Video.objects.get(
                    video_path=file_,
                    modified_timestamp=current_change_time
                )
            except Video.DoesNotExist:
                logger.info("Processing %s" % file_)

                # generate a thumbnail for the video and save it to /videos/static/thumbnails/
                try:
                    # delete all files of which names are equal to file_
                    Video.objects.filter(video_path=file_).delete()

                    # insert video path and thumbnail path to videos table
                    Video.objects.create(
                        video_path=file_,
                        thumbnail_path="%s.png" % os.path.splitext(file_)[0],
                        modified_timestamp=current_change_time
                    )

                    clip = VideoFileClip(os.path.join(settings.WATCHING_DIR, file_))
                    start_duration = 0
                    mid_duration = clip.duration / 2
                    delta = clip.duration * 0.1
                    while delta > 10:
                        delta /= 10
                    end_duration = clip.duration - delta
                    sub_clips = []
                    for subclip_start in [start_duration, mid_duration, end_duration]:
                        sub = clip.subclip(
                            subclip_start,
                            subclip_start + delta).resize(0.3)
                        sub_clips.append(sub)
                    subs_concated = concatenate_videoclips(sub_clips)
                    subs_concated.save_frame(os.path.join(
                        settings.THUMBNAIL_DIR,
                        "%s.png" % os.path.splitext(file_)[0]), delta)
                    subs_concated.write_gif(os.path.join(
                        settings.THUMBNAIL_DIR,
                        "%s.gif" % os.path.splitext(file_)[0]))
                except:
                    logger.error("Clip Error: Invalid file %s" % file_)
                    # remove inserted video path
                    Video.objects.get(video_path=file_).delete()
            except Video.MultipleObjectsReturned:
                # detect double processing on a file
                logger.error("Process Error: Duplicated file %s" % file_)
            except Exception as e:
                # detect dabase issue by celery
                logger.error(str(e))
                logger.error("Process Unknown Error" % file_)
