"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from app.views import SignonView, EvernoteAuthView, GithubAuthView
from app.views import GetNotebooksView, ConsoleView, GetNotesView
from app.views import GetRepoView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^signon/$', SignonView.as_view(), name='signon'),
    url(r'^console/$', ConsoleView.as_view(), name='console'),
    url(r'^evernote-auth/$', EvernoteAuthView.as_view(), name='evernote-auth'),
    url(r'^github-auth/$', GithubAuthView.as_view(), name='github-auth'),
    url(r'^notebooks/$', GetNotebooksView.as_view(), name='notebooks'),
    url(r'^notebooks/(?P<notebook>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/notes/$',
        GetNotesView.as_view(), name='notes'),
    url(r'^github-repo/$', GetRepoView.as_view(), name="github-repo"),
    url(r'^', include('django.contrib.auth.urls'))
]
