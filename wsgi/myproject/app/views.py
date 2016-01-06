from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from app.models import UserProfile
import json
import helper
import yaml


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

    def get(self, request, *args, **kwargs):
        # Get the access token from call back url param
        req_token = request.session.get('en_req_token', '')
        if req_token:
            client = helper.get_evernote_client()
            access_token = client.get_access_token(
              req_token['oauth_token'],
              req_token['oauth_token_secret'],
              request.GET.get('oauth_verifier', '')
            )
            del request.session['en_req_token']

        # Save the access token to UserProfile model
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.en_access_token = access_token
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=request.user,
                en_access_token=access_token)

        return redirect('console')


class GithubAuthView(TemplateView):
    """ Github authorization callback url """
    template_name = 'app/console.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GithubAuthView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Get the access token from call back url param
        callback_url = '{app_protocol}://{app_domain}{app_url}'.format(
            app_protocol=request.META['wsgi.url_scheme'],
            app_domain=request.META['HTTP_HOST'],
            app_url=reverse('github-auth'),
        )

        client = helper.get_github_client()
        access_token = client.get_access_token(
            request.GET.get('code', ''),
            callback_url
        )

        # Save the access token to UserProfile model
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.gh_access_token = access_token
            profile.save()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=request.user,
                gh_access_token=access_token)

        return redirect('console')


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


class SyncForm(forms.Form):
    note_guid = forms.CharField()
    title = forms.CharField()
    repo = forms.CharField()
    message = forms.CharField()


class SyncView(JSONResponseMixin, TemplateView):
    """Synchornize the Evernote notes to Github repo"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SyncView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = SyncForm(request.POST)
        if form.is_valid():
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return self.render_to_json_response(
                    {'rc': -2, 'message': 'User profile not exist'})

            if not profile.en_access_token:
                return self.render_to_json_response(
                    {'rc': -3, 'message': 'Evernote access token not exist'})

            if not profile.gh_access_token:
                return self.render_to_json_response(
                    {'rc': -4, 'message': 'Github access token not exist'})

            # step. 0 Read the config.yml file to get the post path and media path
            gh_client = helper.get_github_client(profile.gh_access_token)
            gh_store = gh_client.get_github_store()
            repo = gh_store.get_user().get_repo(form.cleaned_data['repo'])

            import pdb
            pdb.set_trace()

            try:
                _config = yaml.load(repo.get_contents('_config.yml').decoded_content)
                post_path = _config['prose']['rooturl']
                media_path = _config['prose']['media']
                category, layout = (None, None)
                for item in _config['prose']['metadata']['_posts']:
                    if item['name'] == 'categories':
                        category = item['field']['value']
                    if item['name'] == 'layout':
                        layout = item['field']['value']

                if not category or not layout:
                    return self.render_to_json_response({
                        'rc': -6,
                        'message': '_config.yml did not contain layout or categories'}
                    )
            except:
                return self.render_to_json_response({
                    'rc': -5,
                    'message': '_config.yml not found or not correct.'}
                )

            # step.1 Get the note from API
            try:
                note_guid = form.cleaned_data['note_guid']
                client = helper.get_evernote_client(
                    profile.en_access_token)
                note_store = client.get_note_store()
                note = note_store.getNote(
                    profile.en_access_token,  # authenticationToken
                    note_guid,                # guid
                    True,                     # withContent
                    True,                     # withResourcesData
                    True,                     # withResourcesRecognition
                    True,                     # withResourcesAlternateData
                )
            except Exception, e:
                return self.render_to_json_response(
                    {'rc': -4, 'message': str(e)})

            # Create a jekyll header
            header = '---'
            header += '\nlayout: {}'.format(layout)
            header += '\ncategories: {}'.format(category)
            header += '\npublished: true'
            header += '\ntitle: {}'.format(note.title)
            header += '\n---'

            # step.2 Commit the data to Github repo
            md = helper.enml_to_markdown(note.content, media_path)

            # Insert the header before the content
            md = header + md

            # TODO Commit the file to the specify repo (create or update)
            # TODO Use config.yaml settings to locate what is the post path
            path = '/{}/{}'.format(post_path, form.cleaned_data['title'])

            try:
                content = repo.get_contents(path)
                # File exist, so replace it
                repo.update_file(
                    path,
                    form.cleaned_data['message'],
                    bytes(md.encode('utf-8')),
                    content.sha
                )
            except:
                # File not exist, so create it
                repo.create_file(
                    path,
                    form.cleaned_data['message'],
                    bytes(md.encode('utf-8'))
                )

            # step.3 Commit the resources to Github repo
            if note.resources:
                for resource in note.resources:
                    # TODO Use config.yaml settings to find out the media path
                    path = '/{}/{}.{}'.format(
                        media_path,
                        resource.guid,
                        resource.mime.split('/')[1]
                    )

                    try:
                        content = repo.get_contents(path)
                        # File exist, so update it
                        repo.update_file(
                            path, form.cleaned_data['message'],
                            resource.data, content.sha)
                    except:
                        # File not exist, so create it
                        repo.create_file(
                            path, form.cleaned_data['message'],
                            resource.data
                        )
        else:
            return self.render_to_json_response({
                'rc': -1, 'message': 'Submit form not valid'})

        return self.render_to_json_response({'rc': 0, 'message': 'OK'})
