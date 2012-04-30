from django.conf import settings
from django.db import models

from composite_field.base import CompositeField
from .utils import LANGUAGES, get_language


def get_localized(self, lang, name):
    try:
        attr = getattr(self, '%s_%s' % (name, lang))
    except AttributeError,  e:
        raise AttributeError(
            'Either field "%s" does not exist, or language "%s" is not defined for this model. (%s)' % \
                (name, lang, e)
        )
    return attr

def set_localized(self, lang, name, value):
    try:
        attr = setattr(self, '%s_%s' % (name, lang), value)
    except AttributeError, e:
        raise AttributeError(
            'Either field "%s" does not exist, or language "%s" is not defined for this model. (%s)' % \
                (name, lang, e)
        )
    return attr


class LocalizedField(CompositeField):
    def __init__(self, field_class, *args, **kwargs):
        '''
        Adds a model field of type "field_class" with translations for all languages.
        Fallback can have one if these values:
           None (default): an empty field value in an object that's marked as
                           "translated" for that language, will return the empty value.
           True: always fallback to the default language in case the field is empty
           False: never fallback, even when the object is not translated
        '''
        super(LocalizedField, self).__init__()
        self.verbose_name = kwargs.pop('verbose_name', None)
        self.fallback = kwargs.pop('fallback', None)

        # we can't check for blanks, one language might always be blank
        kwargs.pop('blank', False)

        for language in LANGUAGES:
            self[language] = field_class(blank=True, *args, **kwargs)

    def contribute_to_class(self, cls, field_name):
        if self.verbose_name is None:
            self.verbose_name = field_name.replace('_', ' ').capitalize()

        for language in self:
            self[language].verbose_name = u'%s (%s)' % (self.verbose_name, language)
            # Save a reference to the composite field for later use
            self[language].composite_field = self

        super(LocalizedField, self).contribute_to_class(cls, field_name)

        # monkeypatch some helper functions to the class
        cls.get_localized = get_localized
        cls.set_localized = set_localized

    def get(self, model):
        # get current value
        translation = getattr(model, self.prefix + get_language())

        if self.fallback == False:
            # we don't fallback, return the value
            return translation

        if translation or not self.fallback:
            # show translation only if it exists or we have disabled fallback
            return translation

        # fallback to default language
        return getattr(model, self.prefix + settings.LANGUAGE_CODE)

    def set(self, model, value):
        setattr(model, self.prefix + get_language(), value)


class LocalizedCharField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedCharField, self).__init__(models.CharField, *args, **kwargs)

class LocalizedTextField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedTextField, self).__init__(models.TextField, *args, **kwargs)

class LocalizedFileField(LocalizedField):
    def __init__(self, *args, **kwargs):
        # call the grandparent's init()
        upload_to_params = kwargs.pop('upload_to_params', None)

        super(LocalizedField, self).__init__()
        field_class = kwargs.pop('field_class', models.FileField)
        self.verbose_name = kwargs.pop('verbose_name', None)
        # always fallback to english version
        self.fallback = True
        # when we're localized, the field can always be empty in one language
        if 'blank' in kwargs:
            del kwargs['blank']

        # set a higher max length for filenames
        kwargs['max_length'] = 255

        for language in LANGUAGES:
            if upload_to_params:
                from southstream.utils.storage import upload_to
                kwargs['upload_to'] = upload_to(
                    upload_to_params[0],
                    upload_to_params[1],
                    *upload_to_params[2:],
                    language=language
                )

            self[language] = field_class(blank=True, *args, **kwargs)

class LocalizedImageField(LocalizedFileField):
    def __init__(self, *args, **kwargs):
        kwargs['field_class'] = models.ImageField
        super(LocalizedImageField, self).__init__(models.ImageField, *args, **kwargs)

class LocalizedBooleanField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedBooleanField, self).__init__(models.BooleanField, *args, **kwargs)

class LocalizedDateField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedDateField, self).__init__(models.DateField, *args, **kwargs)

class LocalizedForeignKey(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedForeignKey, self).__init__(models.ForeignKey, *args, **kwargs)

class LocalizedURLField(LocalizedField):
    def __init__(self, *args, **kwargs):
        kwargs['fallback'] = kwargs.get('fallback', True)
        super(LocalizedURLField, self).__init__(models.URLField, *args, **kwargs)
