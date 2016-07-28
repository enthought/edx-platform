""" Authenticate the user using Enthought credentials. """

# Standard library.
from base64 import b64encode
import requests

# 3rd party library.
from django.contrib.auth.models import User

# edX library.
from student.forms import AccountCreationForm
from student.views import _do_create_account


class EnthoughtAuthBackend(object):
    """ A Django authentication backend that authenticates users via the
    Enthought web API.

    """

    def authenticate(self, request=None, **kwargs):
        """
        Try to authenticate a user. This method will try to authenticate the
        user on the Enthought API system and if successful, return a User
        object from the local database.

        If a User object is not found in the local database, it creates one.
        """

        email = request.POST.get('email')
        password = request.POST.get('password')

        import pdb; pdb.set_trace()
        user_data = self._authenticate_on_enthought_api(email, password)

        if user_data is None:
            return None

        else:
            try:
                user = User.objects.get(email=email)

            except User.DoesNotExist:
                user = self._create_user(email, password, user_data)

            return user

    def get_user(self, user_id):
        """
        Return the User object for a user that has already been authenticated
        by this backend.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    #### Private protocol #####################################################

    def _authenticate_on_enthought_api(self, email, password):
        """ Authenticate the user on api.enthought.com. """

        url = 'https://api.enthought.com/accounts/user/info/'

        headers = {
            'Authorization': (
                'Basic ' + b64encode('%s:%s' % (email, password))
            )
        }

        response = requests.post(url, headers=headers)

        if not response.ok:
            return False

        else:
            return response.json()

    def _create_user(self, email, password, user_data):
        """ Create a user given email and password. """

        user, profile, registration = _do_create_account(
            AccountCreationForm(
                data         = {
                    'username': email,
                    'email'   : email,
                    'password': password,
                    'name'    : (
                        user_data['first_name'] + ' ' + user_data['last_name']
                    )
                },
                tos_required = False
            )
        )

        if user_data['is_active']:
            registration.activate()
            registration.save()

        return user
