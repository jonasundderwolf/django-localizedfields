from django.conf import settings
from django.utils.translation import get_language as django_get_language


LANGUAGES = [lang for lang, name in settings.LANGUAGES]

def localized_field_names(field):
    return ['%s_%s' % (field, lang) for lang in LANGUAGES]


def get_language():
    language = django_get_language()
    # no sublanguages
    if '-' in language:
        language = language.split('-')[0]

    # return str not unicode so we can use it in a kwargs dictionary
    return str(language)


def i18n_field(field):
    return '%s_%s' % (field, get_language())
