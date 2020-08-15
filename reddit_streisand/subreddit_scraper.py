import praw
import os
import sys
from datetime import date
import shutil 
import requests 
import mimetypes
import logging
import pprint

from redvid import Downloader


logger = logging.getLogger(__name__)

class SubredditScraper():
    def __init__(self, subreddit, output, batch_size=10):
        mimetypes.init()
        self.subreddit = subreddit
        self.batch_size = batch_size
        self.output = output


    def scrape(self):
        for submission in self.subreddit.new(limit=self.batch_size):
            self.process_submission(submission, self.output)

    def download_media(self, media_path, media_metadata):
        for media_id, item in media_metadata.items():
            if item.get("e") == "Image":    
                image_url = item.get("s").get("u")
                filename = os.path.join(media_path, media_id + mimetypes.guess_extension(item.get("m"), strict=False))

                if os.path.exists(filename):
                    continue

                r = requests.get(image_url, stream = True)
                if r.status_code == 200:
                    r.raw.decode_content = True
                    with open(filename,'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            else:
                logger.warn(f"unhandled media type in media_metadata: {item.get('e')}")

    def download_image(self, media_path, url):
        filename = os.path.join(media_path, url.split("/")[-1])

        if os.path.exists(filename):
            return

        r = requests.get(url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def download_gifv(self, media_path, url):
        src_file_name =  url.split("/")[-1]
        file_id = os.path.splitext(src_file_name)[0]
        download_url = f"https://imgur.com/download/{file_id}"
        filename = os.path.join(media_path, file_id+".mp4")
        
        if os.path.exists(filename):
            return

        r = requests.get(download_url, stream = True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename,'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def download_video(self, media_path, media, url):
        for media_type, item in media.items():
            if media_type == "reddit_video":    

                if item.get("transcoding_status") != "completed":
                    continue

                Downloader(url=url, path = os.path.abspath(media_path), max_q=True).download()
            else:
                logger.warn(f"unhandled media type in media_metadata: {media_type}")


    def process_submission(self, submission, scraping_path):
        
        submission_path = os.path.join(scraping_path, submission.subreddit.display_name) 

        if not os.path.exists(submission_path):
            os.mkdir(submission_path)

        submission_path = os.path.join(submission_path, submission.id) 

        if not os.path.exists(submission_path):
            logger.debug(f"new submission {submission.id} found: {submission.title}")
            os.mkdir(submission_path)
    
        # if submission.media:
        submission_media_path = os.path.join(submission_path, "media") 

        if hasattr(submission,"media_metadata"):
            if not os.path.exists(submission_media_path):
                os.mkdir(submission_media_path)
            self.download_media(submission_media_path, submission.media_metadata)

        elif submission.is_video:
            if not os.path.exists(submission_media_path):
                os.mkdir(submission_media_path)
            self.download_video(submission_media_path, submission.media,submission.url)

        elif submission.url.endswith(".gifv"):
            if not os.path.exists(submission_media_path):
                os.mkdir(submission_media_path)
            self.download_gifv(submission_media_path, submission.url)

        elif submission.url.endswith(".jpg") or submission.url.endswith(".png") or submission.url.endswith(".jpeg"):
            if not os.path.exists(submission_media_path):
                os.mkdir(submission_media_path)
            self.download_image(submission_media_path, submission.url)
        else:
            logger.warn(f"could not process {submission.permlink}")
