Jekynote
========

[Jekynote](https://jekynote.cloudesk.top) is developed by django + Evernote API + PyGithub. And now Jekynote is hosted on Openshift, one of the most famous free web hosting platform. 

Why do I create such repo
-------------------------

I am an evernote loyal user, and Jekyll loyal user. When I working on my desktop, and encountered some issues, and fixed it later, I alwasy use the evernote desktop app to write down the issues and solution, and sometimes, I will keep some record about how to do something. But after I have wrote a long article, I want to publish this ariticle to my blog (my blog is build upon Jekyll + Github page). And I have no choice but using prose.io to retype my works in the web browser again, and upload the images manually. It is not efficiency. And I start to think, can I integrate my evernote with my jekyll blog?

The answer is YES.

Evernote provide some awesome API for developer to create app to access user's notes and note books. And offcause, on github, we have many open source repo to access Github API. So I decide to create Jekynote (name is short for Jekyll + Evernote).

Why I choose python
-------------------

Python is really good at doing integration. And bot evernote and github provide API access lib in python language. And the most important reason is, I can build a web app base on Django which is also written in python. So it will be more easy to integrate the API with the web app.


How to use Jekynote?
--------------------

First, you need to register an jekynote account with your email. Then you can login with your account, and choose the `Authroization` tab on the left hand side of the panel.

And then getting oauth token for evernote and github.

The last step, is selecting `Publish` tab on the panel, and select your note books, and github jekyll repo.

Now, you can publish the notes easily to jekyll repo, and most important, the images will be uploaded to jekyll repo automatically. Cool.. right?

So no more hastiate, try to use Jekynote to simplify your life now...

Have fun, and happy coding. :)

