from django.utils.timezone import now
from django.conf import settings
from evernote.api.client import EvernoteClient
from githubapi.client import GithubClient
import html2text
import time


def get_github_client(access_token=None):
    if access_token:
        client = GithubClient(access_token)
    else:
        client = GithubClient(
          consumer_key=settings.GITHUB_CLIENT_ID,
          consumer_secret=settings.GITHUB_CLIENT_SECRET
        )
    return client


def get_evernote_client(access_token=None):
    ''' Get the evernote client '''
    if access_token:
        client = EvernoteClient(token=access_token)
    else:
        client = EvernoteClient(
          consumer_key=settings.EVERNOTE_CUSUMER_KEY,
          consumer_secret=settings.EVERNOTE_CUSUMER_SECRET,
          sandbox=True
        )
    return client


def get_current_timestamp():
    ''' Get the current timestamp depends on settigs.TIME_ZONE '''
    return int(time.mktime(now().timetuple()))


class ENMLParser(object):
    def enml_to_markdown(content):
        content = content.replace(
            r'<\?xml[^>]*>', ''
          ).replace(
            r'<!(--)?\[CDATA[^>]*>', ''
          ).replace(
            r'<!DOCTYPE[^>]*>', ''
          ).replace(
            r'<en-note[^>]*>'
          ).replace(
            r'<\/en-note>', ''
          ).replace(
            r']](--)?>'
          )
