
import requests
import urlparse
from datetime import datetime


API_URL = ('https://www.googleapis.com/youtube/v3/videos'
           '?part={parts}&id={video_id}&key={api_key}')


def cached(fn):
    def wrapped(self, submission):
        id = str(submission.id)
        if id in self.cache:
            return self.cache[id]
        else:
            result = fn(self, submission)
            self.cache[id] = result
            return result
    return wrapped


def get_video_id_from_link(link):
    """Returns the query string video_id from a URL"""
    query_string = urlparse.urlparse(link).query
    qs_params = urlparse.parse_qs(query_string)
    return qs_params['v'][0]


def get_video_time(video_id, api_key=None):
    """Returns video duration in seconds"""
    result = requests.get(API_URL.format(
        parts='contentDetails', video_id=video_id, api_key=api_key)
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
