from itertools import groupby
import logging

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey

from course_modes.models import CourseMode

log = logging.getLogger(__name__)


class Course(object):
    id = None
    modes = None

    def __init__(self, id, modes):
        self.id = CourseKey.from_string(unicode(id))
        self.modes = list(modes)

    def save(self, *args, **kwargs):
        for mode in self.modes:
            mode.course_id = self.id
            mode.mode_display_name = mode.mode_slug
            mode.save()

    def update(self, attrs):
        merged_modes = []

        for posted_mode in attrs.get('modes', []):
            merged_mode = None

            for existing_mode in self.modes:
                if existing_mode.mode_slug == posted_mode.mode_slug:
                    merged_mode = existing_mode
                    break

            if not merged_mode:
                merged_mode = CourseMode()

            merged_mode.course_id = self.id
            merged_mode.mode_slug = posted_mode.mode_slug
            merged_mode.mode_display_name = posted_mode.mode_slug
            merged_mode.min_price = posted_mode.min_price
            merged_mode.currency = posted_mode.currency
            merged_mode.sku = posted_mode.sku

            merged_modes.append(merged_mode)

        self.modes = merged_modes

    @classmethod
    def get(cls, course_id):
        """ Retrieve a single course. """
        try:
            course_id = CourseKey.from_string(unicode(course_id))
        except InvalidKeyError:
            log.debug('[%s] is not a valid course key.', course_id)
            raise ValueError

        course_modes = CourseMode.objects.filter(course_id=course_id)

        if course_modes:
            return cls(unicode(course_id), list(course_modes))

        return None

    @classmethod
    def all(cls):
        """ Retrieve all courses/modes. """
        course_modes = CourseMode.objects.order_by('course_id')
        courses = []

        for course_id, modes in groupby(course_modes, lambda o: o.course_id):
            courses.append(cls(course_id, list(modes)))

        return courses
