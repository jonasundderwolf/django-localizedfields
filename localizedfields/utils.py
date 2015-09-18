from contextlib import contextmanager
from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.utils.translation import get_language as django_get_language, activate


LANGUAGES = [lang for lang, name in settings.LANGUAGES]


def localized_field_names(field):
    return ['%s_%s' % (field, lang) for lang in LANGUAGES]


def get_language():
    language = django_get_language()
    # no sublanguages
    if language and '-' in language:
        language = language.split('-')[0]

    # return str not unicode so we can use it in a kwargs dictionary
    return str(language)


def localized_field(field):
    return '%s_%s' % (field, get_language())


def first_value(instance, field):
    for lang in LANGUAGES:
        val = instance.get_localized(lang, field)
        if val:
            return val


@contextmanager
def switch_language(language):
    previous = django_get_language()
    activate(language)
    yield
    activate(previous)


def for_all_languages(func, *args, **kwargs):
    results = {}
    for language, __ in settings.LANGUAGES:
        with switch_language(language):
            results[language] = func(*args, **kwargs)
    return results


import os
import datetime
from django.template.defaultfilters import slugify, truncatechars
from django.utils import translation


@deconstructible
class LanguageAwareUploadToDirectory(object):
    def __init__(self, **upload_options):
        self.options = upload_options

    def _generate_path(self, instance, filename, language=None):
        path = self.options.get('path', '')
        if language:
            path = os.path.join(path, language)

        date = datetime.date.today()
        path = os.path.join(path,
                            date.strftime('%Y'),
                            date.strftime('%m'))

        return path

    def _generate_filename(self, instance, filename, language=None):
        basename, extension = os.path.splitext(filename)
        extension = extension.lower()

        slug = ''
        if self.options.get('prefix'):
            slug = slugify(self.options.get('prefix')) + '_'

        # try to use name_attr field for filename
        name_attr = self.options.get('name_attr')
        if name_attr:
            name = getattr(instance, name_attr) or first_value(instance, name_attr)
            if name:
                slug += slugify(truncatechars(name, 130))
            else:
                slug += slugify(basename)
        else:
            slug += slugify(basename)

        return '{0}{1}'.format(slug, extension)

    def __call__(self, instance, filename):
        language = self.options.get('language')
        if language:
            old_lang = get_language()
            translation.activate(language)

        filename = self._generate_filename(instance, filename, language)
        path = self._generate_path(instance, filename, language)

        if language:
            translation.activate(old_lang)

        return os.path.join(path, filename)
