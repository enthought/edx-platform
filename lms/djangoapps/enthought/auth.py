""" Authenticate the user using Enthought credentials. """

# Standard library.
from base64 import b64encode
import os
import requests

# 3rd party library.
from django import forms
from django.contrib.auth.models import User

# edX library.
from student.forms import AccountCreationForm


class EnthoughtAuthBackend(object):
    """ A Django authentication backend that authenticates users via the
    Enthought web API.

    """

    def authenticate(self, username=None, password=None, request=None):
        """
        Try to authenticate a user. This method will try to authenticate the
        user on the Enthought API system and if successful, return a User
        object from the local database.

        If a User object is not found in the local database, it creates one.
        """

        if not username:
            username = request.POST.get('email')

        if not password:
            password = request.POST.get('password')

        authenticated = self._authenticate(username, password)

        if not authenticated:
            return None

        else:
            user_data = self._get_user_data(username)
            try:
                user = User.objects.get(username=username)

            except User.DoesNotExist:
                user = self._create_user(
                    username   = username,
                    password   = password,
                    first_name = user_data['first_name'],
                    last_name  = user_data['last_name'],
                    is_active  = user_data['is_active']
                )

            return user

    def get_user(self, user_id):
        """ Return the User object for a user that has already been
        authenticated by this backend.

        """

        try:
            return User.objects.get(id=user_id)

        except User.DoesNotExist:
            return None

    #### Private protocol #####################################################

    _API_ROOT   = 'http://api.enthought.org'
    _VERIFY_SSL = False

    def _authenticate(self, username, password):
        """ Authenticate the user on api.enthought.com. """

        url  = self._API_ROOT + '/token-auth/'
        data = {'username': username, 'password': password}

        response = requests.post(url, data=data, verify=self._VERIFY_SSL)

        return response.ok

    def _create_user(self, username, password, first_name, last_name, is_active):
        """ Create a user given username, password and other data.

        Note that we have to do a full-fledged account creation with profile
        and registration as well, so a simple `User.objects.create(...)` will
        not work here. Instead, we call the edX supplied method to create an
        account.

        """

        from student.views import _do_create_account

        user, profile, registration = _do_create_account(
            EnthoughtAccountCreationForm(
                data         = {
                    'username': username,
                    'email'   : username,
                    'password': password,
                    'name'    : first_name + ' ' + last_name
                },
                tos_required = False
            )
        )

        if is_active:
            registration.activate()
            registration.save()

        return user

    def _get_user_data(self, username):
        """ Get user data from API. """

        url = self._API_ROOT + '/api/users/%s/' % username
        api_token = os.environ.get('ENTHOUGHT_API_TOKEN')

        if api_token is None:
            raise RuntimeError(
                '$ENTHOUGHT_API_TOKEN environment variable not set.'
            )

        headers = {'Authorization': 'Token ' + api_token}

        response = requests.get(url, headers=headers, verify=self._VERIFY_SSL)

        return response.json()


class EnthoughtAccountCreationForm(AccountCreationForm):

    # Changing the username from SlugField to a CharField since our usernames
    # are same as emails so we need to allow special characters like '.', '@'
    # etc in the username.
    username = forms.CharField(
        min_length     = 2,
        max_length     = 30,
        error_messages = {
            "required"   : "Username too short",
            "min_length" : "Username too short",
            "max_length" : (
                "Username cannot be more than %(limit_value)s characters long"
            )
        }
    )
