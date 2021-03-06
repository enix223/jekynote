#!/usr/bin/env python

from setuptools import setup

setup(
    # GETTING-STARTED: set your app name:
    name='jekynote',
    # GETTING-STARTED: set your app version:
    version='1.1.0',
    # GETTING-STARTED: set your app description:
    description='Integrate Evernote with jekyll blog site',
    # GETTING-STARTED: set author name (your name):
    author='Enix Yu',
    # GETTING-STARTED: set author email (your email):
    author_email='enix223@163.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires=[
        'Django==1.6',
        'beautifulsoup4',
        'evernote',
        'html2text',
        'MySQL-python==1.2.5',
        'oauth2==1.9.0.post1',
        'requests==2.8.1',
        'six==1.10.0',
        'South',
        'PyYAML==3.11'
    ],
    dependency_links=[
        'https://pypi.python.org/simple/django/',
        'https://github.com/enix223/PyGithub',
    ],
)
