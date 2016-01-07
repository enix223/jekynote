from django.utils.timezone import now
from django.conf import settings
from evernote.api.client import EvernoteClient
from githubapi.client import GithubClient
import html2text
from bs4 import BeautifulSoup
import time


def get_github_client(access_token=None):
    if access_token:
        client = GithubClient(token=access_token)
    else:
        client = GithubClient(
          consumer_key=settings.GITHUB_CLIENT_ID,
          consumer_secret=settings.GITHUB_CLIENT_SECRET
        )
    return client


def get_evernote_client(access_token=None):
    ''' Get the evernote client '''
    if access_token:
        client = EvernoteClient(token=access_token, sandbox=settings.DEBUG)
    else:
        client = EvernoteClient(
          consumer_key=settings.EVERNOTE_CUSUMER_KEY,
          consumer_secret=settings.EVERNOTE_CUSUMER_SECRET,
          sandbox=settings.DEBUG
        )
    return client


def get_current_timestamp():
    ''' Get the current timestamp depends on settigs.TIME_ZONE '''
    return int(time.mktime(now().timetuple()))


def enml_to_markdown(content, media_path):
    # Replace image tag to a link
    note = BeautifulSoup(content).select('en-note')[0]
    html = str(note)
    for media in note.select('en-media'):
        name = media.attrs['hash']
        resType = media.attrs['type'].split('/')[1]
        img = '<img alt="{}" src="{}/{}.{}"/>'.format(name, media_path, name, resType)
        html = html.replace(str(media), img)

    return html2text.html2text(html.decode('utf-8'))
