
import praw
import yaml
import requests
import urlparse
import shelve
from datetime import datetime


YOUTUBE_API_URL = ('https://www.googleapis.com/youtube/v3/videos'
                   '?part={parts}&id={video_id}&key={api_key}')

YOUTUBE_VIDEO_URL = 'https://www.youtube.com/watch?v={video_id}&t={seconds}s'

SETTINGS = yaml.load('settings.yaml')



def main():
    user_agent = ('PyWadsworth Bot 0.1')

    r = praw.Reddit(user_agent=user_agent)

    subreddit = r.get_subreddit('videos')

    processed_submissions = shelve.open('processed_submissions.shelve')

    for submission in subreddit.get_hot(limit=16):
        sub_id = str(submission.id)
        if sub_id in processed_submissions:
            print '* {} -> {}'.format(submission.id, processed_submissions[sub_id])
        else:
            new_url = process_submission(submission)
            processed_submissions[sub_id] = new_url
            print '{} -> {}'.format(sub_id, new_url)

    processed_submissions.close()


def process_submission(submission):
    if submission_is_youtube(submission):
        time = get_wadsworth_time(submission.url)
        new_video_url = get_new_url(submission.url, time)
        # print "{} -> {}".format(submission.url, new_video_url)
        return new_video_url
        # post_comment(submission, new_video_url)


def submission_is_youtube(submission):
    """Determines if a given reddit submission is from youtube.com"""
    return 'youtube' in submission.domain


def get_wadsworth_time(link):
    """Gets the wadsworth time (30%) from a youtube link"""
    video_id = _get_video_id_from_link(link)
    total_seconds = _get_video_time(video_id)

    return int(total_seconds * 0.3)


def _get_video_id_from_link(link):
    """Returns the query string video_id from a URL"""
    query_string = urlparse.urlparse(link).query
    qs_params = urlparse.parse_qs(query_string)
    return qs_params['v'][0]


def _get_video_time(video_id):
    """Returns video duration in seconds"""
    result = requests.get(YOUTUBE_API_URL.format(
        parts='contentDetails', video_id=video_id, api_key=SETTINGS['api_key'])
    ).json()

    iso8601_duration = result['items'][0]['contentDetails']['duration']
    datetime_duration = _datetime_from_iso8601(iso8601_duration)
    return (datetime_duration - datetime(1900, 01, 01)).total_seconds()


def _datetime_from_iso8601(iso8601):
    format = 'PT'
    if 'H' in iso8601:
        format += '%HH'
    if 'M' in iso8601:
        format += '%MM'
    if 'S' in iso8601:
        format += '%SS'
    return datetime.strptime(iso8601, format)


def get_new_url(link, time):
    """Creates the new URL of the youtube video"""
    video_id = _get_video_id_from_link(link)
    return YOUTUBE_VIDEO_URL.format(video_id=video_id, seconds=time)


def post_comment(submission, link):
    """Posts a comment to the submission with the link"""
    pass


if __name__ == '__main__':
    main()
