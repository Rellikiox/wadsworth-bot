
import praw
import yaml
import shelve

import utils


CONFIG = yaml.load(open('config.yaml'))

USER_AGENT = ('PyWadsworth Bot 0.1')

VIDEO_URL = 'https://www.youtube.com/watch?v={video_id}&t={seconds}s'


class WadsworthBot(object):
    def __init__(self):
        self.r = praw.Reddit(user_agent=USER_AGENT)
        self.r.login(CONFIG['reddit']['username'], CONFIG['reddit']['password'])

    def run(self):
        self.cache = shelve.open('videos_posted.shelve')

        subreddit = self.r.get_subreddit('bottesting')

        for submission in subreddit.get_new(limit=16):
            new_url = self.process_submission(submission)
            print '{} -> {}'.format(submission.id, new_url)

        self.cache.close()

    @utils.cached
    def process_submission(self, submission):
        if self.submission_is_youtube(submission):
            time = self.get_wadsworth_time(submission.url)
            new_video_url = self.get_new_url(submission.url, time)
            # self.post_comment(submission, new_video_url)
            return new_video_url

    def submission_is_youtube(self, submission):
        """Determines if a given reddit submission is from youtube.com"""
        return 'youtube' in submission.domain

    def get_wadsworth_time(self, link):
        """Gets the wadsworth time (30%) from a youtube link"""
        video_id = utils.get_video_id_from_link(link)
        total_seconds = utils.get_video_time(video_id, api_key=CONFIG['api_key'])

        return int(total_seconds * 0.3)

    def get_new_url(self, link, time):
        """Creates the new URL of the youtube video"""
        video_id = self._get_video_id_from_link(link)
        return VIDEO_URL.format(video_id=video_id, seconds=time)

    def post_comment(self, submission, link):
        """Posts a comment to the submission with the link"""
        submission.add_comment(link)
