import oauth2 as oauth
import urllib
import urlparse
import requests
import json


class GithubClient(object):

    def __init__(self, **options):
        self.consumer_key = options.get('consumer_key')
        self.consumer_secret = options.get('consumer_secret')
        default_service_host = 'github.com'
        self.service_host = options.get('service_host', default_service_host)
        self.additional_headers = options.get('additional_headers', {})
        self.token = options.get('token')
        self.secret = options.get('secret')

    def get_authorize_url(self, scope='repo'):
        return '%s?client_id=%s&scope=%s' % (
            self._get_endpoint('login/oauth/authorize'),
            urllib.quote(self.consumer_key),
            urllib.quote(scope)
        )

    def get_access_token(self, code):
        header = {'content-type': 'application/json', 'Accept': 'application/json'}
        resp = requests.post(
            self._get_endpoint('login/oauth/access_token'),
            data=json.dumps({
                'client_id': self.consumer_key,
                'client_secret': self.consumer_secret,
                'code': code
            }),
            headers=header
        )
        access_token = dict(json.loads(resp.content))
        self.token = access_token['access_token']
        return self.token

    def _get_oauth_client(self, token=None):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        if token:
            client = oauth.Client(consumer, token)
        else:
            client = oauth.Client(consumer)
        return client

    def _get_endpoint(self, path=None):
        url = "https://%s" % (self.service_host)
        if path is not None:
            url += "/%s" % path
        return url
