from django.conf import settings
from django.utils.deconstruct import deconstructible
from django.utils.translation import get_language, override


def short_language(language=None):
    if not language:
        language = get_language()

    if not language:
        language = settings.LANGUAGE_CODE

    # no sublanguages
    if "-" in language:
        language = language.split("-")[0]

    # return str not unicode so we can use it in a kwargs dictionary
    return str(language)


sorted_set = (
    set()
)  # If we just cast the normal list to a set the order of entries will be randomised.
SHORT_LANGUAGES = [
    short_language(lang)
    for lang, name in settings.LANGUAGES
    if not (lang in sorted_set or sorted_set.add(lang))
]


def localized_field_names(field):
    return [localized_field(field, lang) for lang in SHORT_LANGUAGES]


def localized_field(field, lang=None):
    return "%s_%s" % (field, lang or short_language())


def first_value(instance, field):
    for lang in SHORT_LANGUAGES:
        val = instance.get_localized(lang, field)
        if val:
            return val


def for_all_languages(func, *args, **kwargs):
    results = {}
    for language in SHORT_LANGUAGES:
        with override(language):
            results[language] = func(*args, **kwargs)
    return results


import datetime
import os

from django.template.defaultfilters import truncatechars
from django.utils import translation
from django.utils.text import slugify


@deconstructible
class LanguageAwareUploadToDirectory(object):
    def __init__(self, **upload_options):
        self.options = upload_options

    def _generate_path(self, instance, filename, language=None):
        path = self.options.get("path", "")
        if language:
            path = os.path.join(path, language)

        date = datetime.date.today()
        path = os.path.join(path, date.strftime("%Y"), date.strftime("%m"))

        return path

    def _generate_filename(self, instance, filename, language=None):
        basename, extension = os.path.splitext(filename)
        extension = extension.lower()

        slug = ""
        if self.options.get("prefix"):
            slug = slugify(self.options.get("prefix")) + "_"

        # try to use name_attr field for filename
        name_attr = self.options.get("name_attr")
        if name_attr:
            name = getattr(instance, name_attr) or first_value(instance, name_attr)
            if name:
                slug += slugify(truncatechars(name, 130))
            else:
                slug += slugify(basename)
        else:
            slug += slugify(basename)

        return "{0}{1}".format(slug, extension)

    def __call__(self, instance, filename):
        language = self.options.get("language")
        if language:
            old_lang = short_language()
            translation.activate(language)

        filename = self._generate_filename(instance, filename, language)
        path = self._generate_path(instance, filename, language)

        if language:
            translation.activate(old_lang)

        return os.path.join(path, filename)
