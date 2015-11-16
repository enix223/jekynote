from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    en_access_token = models.CharField(
        'Evernote access token', max_length=255, null=True, blank=True)
    gh_access_token = models.CharField(
        'Github access token', max_length=255, null=True, blank=True)
