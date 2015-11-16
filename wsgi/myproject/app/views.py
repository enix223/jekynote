from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response

from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from app.models import UserProfile
import json
import helper


'''def handler500(request):
    logging.error(request)
    response = render_to_response(
        '500.html', {}, context_instance=RequetContext(request))
    response.status_code = 500
    return response
'''


class JSONResponseMixin(object):
    """A mixin used to render JSON response"""
    def convert_to_json(self, context):
        return json.dumps(context)

    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(
            self.convert_to_json(context),
            content_type='application/json',
            **response_kwargs
        )


class EnSerializeMixin(object):
    """ Evernote serializable mixin """
    def serialize(self, p_dict):
        if type(p_dict) == dict:
            generator = p_dict.items()
        else:
            generator = p_dict.__dict__.iteritems()

        d = {}
        for key, value in generator:
            if key in self.serialize_filter:
                d[key] = value
        return d


class GhSerializeMixin(object):
    """ Github object serializable mixin """
    def serialize(self, p_obj):
        d = {}
        for attr in dir(p_obj):
            if attr in self.serialize_filter:
                d[attr] = getattr(p_obj, attr)
        return d


class UserSignonForm(UserCreationForm):
    """ Using EmailField as the username field """
    username = forms.EmailField()


class SignonView(CreateView):
    """ User registration view """
    template_name = 'registration/signon.html'
    model = User
    form_class = UserSignonForm

    def get_success_url(self):
        return reverse('console')


class ConsoleView(TemplateView):
    """ User console view """
    template_name = 'app/console.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConsoleView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ConsoleView, self).get_context_data(**kwargs)
        context['step'] = 1

        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            profile = None

        callback_url = '{app_protocol}://{app_domain}{app_url}'.format(
            app_protocol=self.request.META['wsgi.url_scheme'],
            app_domain=self.request.META['HTTP_HOST'],
            app_url=reverse('evernote-auth'),
        )

        # Generate Evernote request token url
        client = helper.get_evernote_client()
        req_token = client.get_request_token(callback_url)
        url = client.get_authorize_url(req_token)
        context['en_auth_url'] = url
        self.request.session['en_req_token'] = req_token

        # Generate Github request token url
        client = helper.get_github_client()
        url = client.get_authorize_url()
        context['gh_auth_url'] = url

        context['profile'] = profile
        return context


class EvernoteAuthView(TemplateView):
    """ Evernote authorization callback url """
    template_name = 'app/console.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EvernoteAuthView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the access token from call back url param
        context = super(EvernoteAuthView, self).get_context_data(**kwargs)
        req_token = self.request.session.get('en_req_token', '')
        if req_token:
            client = helper.get_evernote_client()
            access_token = client.get_access_token(
              req_token['oauth_token'],
              req_token['oauth_token_secret'],
              self.request.GET.get('oauth_verifier', '')
            )
            del self.request.session['en_req_token']

        # Save the access token to UserProfile model
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            profile.en_access_token = access_token
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=self.request.user,
                en_access_token=access_token)

        context['profile'] = profile
        context['step'] = 1
        return context


class GithubAuthView(TemplateView):
    """ Github authorization callback url """
    template_name = 'app/console.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GithubAuthView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Get the access token from call back url param
        context = super(GithubAuthView, self).get_context_data(**kwargs)
        client = helper.get_github_client()
        access_token = client.get_access_token(
            self.request.GET.get('code', ''),
            reverse('github-auth')
        )

        # Save the access token to UserProfile model
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            profile.gh_access_token = access_token
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=self.request.user,
                en_access_token=access_token)

        context['profile'] = profile
        context['step'] = 1
        return context


class PublishView(TemplateView):
    """ Pulish evernote to jekyll main control panel """
    template_name = 'app/console.html'

    "Publish console view"
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PublishView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PublishView, self).get_context_data(**kwargs)

        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except Exception:
            profile = None

        if profile and profile.en_access_token:
            context['status'] = 'OK'
        else:
            context['status'] = 'UNAUTHORIZED'

        context['step'] = 2
        return context


class GetNotebooksView(TemplateView, JSONResponseMixin, EnSerializeMixin):
    """ Get all the notebooks """
    template_name = 'app/console.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetNotebooksView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GetNotebooksView, self).get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except Exception:
            profile = None

        if profile and profile.en_access_token:
            access_token = profile.en_access_token
            client = helper.get_evernote_client(access_token)
            note_store = client.get_note_store()
            context['notebooks'] = note_store.listNotebooks()
            context['status'] = 'OK'
        else:
            context['status'] = 'UNAUTHORIZED'

        return context

    def render_to_response(self, context):
        if context['status'] != 'OK':
            raise Exception('user profile not found')

        self.serialize_filter = ['name', 'guid']
        data = map(self.serialize, context['notebooks'])
        return self.render_to_json_response(data)


class GetNotesView(JSONResponseMixin, TemplateView, EnSerializeMixin):
    """ Get notes with specific notebooks """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetNotesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GetNotesView, self).get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except Exception:
            profile = None

        if profile and profile.en_access_token:
            access_token = profile.en_access_token
            client = helper.get_evernote_client(access_token)
            note_store = client.get_note_store()
            notes_meta_list = note_store.findNotesMetadata(
                access_token,
                NoteFilter(notebookGuid=self.kwargs['notebook']),
                0,
                99999,
                NotesMetadataResultSpec(
                    includeTitle=True,
                    includeCreated=True,
                    includeUpdated=True
                )
            )
            context['status'] = 'OK'
            context['notes'] = notes_meta_list.notes
        else:
            context['status'] = 'UNAUTHORIZED'

        return context

    def render_to_response(self, context):
        if context['status'] != 'OK':
            raise Exception('user profile not found')

        self.serialize_filter = ['title', 'updated', 'guid', 'created']
        data = map(self.serialize, context['notes'])
        return self.render_to_json_response(data)


class GetRepoView(JSONResponseMixin, TemplateView, GhSerializeMixin):
    """ Get user's repo from github """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GetRepoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GetRepoView, self).get_context_data(**kwargs)
        try:
            profile = UserProfile.objects.get(user=self.request.user)
        except Exception:
            profile = None

        if profile and profile.en_access_token:
            profile = UserProfile.objects.get(user=self.request.user)
            client = helper.get_github_client(profile.gh_access_token)
            github_store = client.get_github_store()
            self.serialize_filter = ['id', 'name']
            context['repo'] = github_store.get_user().get_repos()
            context['status'] = 'OK'
        else:
            context['status'] = 'UNAUTHORIZED'

        return context

    def render_to_response(self, context):
        if context['status'] != 'OK':
            raise Exception('user profile not found')

        data = map(self.serialize, context['repo'])
        return self.render_to_json_response(data)
