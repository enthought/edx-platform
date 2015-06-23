import logging

from django.http import Http404
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from commerce.api.v1.models import Course
from commerce.api.v1.serializers import CourseSerializer
from openedx.core.lib.api.permissions import ApiKeyHeaderPermissionIsAuthenticated

log = logging.getLogger(__name__)


class CourseListView(ListAPIView):
    """ List courses and modes. """
    authentication_classes = (OAuth2Authentication, SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.all()


class CourseRetrieveUpdateView(RetrieveUpdateAPIView):
    """ Retrieve, update, or create courses/modes. """
    lookup_field = 'id'
    lookup_url_kwarg = 'course_id'
    authentication_classes = (OAuth2Authentication, SessionAuthentication,)
    # TODO Setup permissions for non-GET requests
    permission_classes = (ApiKeyHeaderPermissionIsAuthenticated,)
    serializer_class = CourseSerializer

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        course = Course.get(course_id)

        if course:
            return course

        raise Http404
