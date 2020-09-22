from composite_field.base import CompositeField
from django.conf import settings
from django.db import models
from django.utils import translation

from .utils import (
    SHORT_LANGUAGES,
    LanguageAwareUploadToDirectory,
    for_all_languages,
    get_language,
    localized_field,
    short_language,
)


def get_localized(self, lang, name):
    lang = lang or get_language() or settings.LANGUAGE_CODE
    try:
        attr = getattr(self, localized_field(name, lang))
    except AttributeError as e:
        raise AttributeError(
            'Either field "%s" does not exist, or language "%s" is not defined '
            "for this model. (%s)" % (name, lang, e)
        )
    return attr


def set_localized(self, lang, name, value):
    lang = lang or get_language() or settings.LANGUAGE_CODE
    try:
        attr = setattr(self, localized_field(name, lang), value)
    except AttributeError as e:
        raise AttributeError(
            'Either field "%s" does not exist, or language "%s" is not defined '
            "for this model. (%s)" % (name, lang, e)
        )
    return attr


def set_all_localized(self, name, func, *args, **kwargs):
    for k, v in for_all_languages(func, *args, **kwargs).items():
        self.set_localized(k, name, v)


class LocalizedField(CompositeField):
    def __init__(self, field_class, *args, **kwargs):
        """
        Adds a model field of type "field_class" with translations for all languages.
        Fallback can have one if these values:
           None (default): an empty field value in an object that's marked as
                           "translated" for that language, will return the empty value.
           True: fallback to the default language in case the field is empty
                 or the fallback is checked in admin (saved in
                 model.translated_languages)

           False: never fallback, even when the object is not translated
        """
        super(LocalizedField, self).__init__()
        self.verbose_name = kwargs.pop("verbose_name", None)
        self.fallback = kwargs.pop("fallback", None)

        # we can't check for blanks, one language might always be blank
        kwargs.pop("blank", False)

        for language in SHORT_LANGUAGES:
            self[language] = field_class(blank=True, *args, **kwargs)

    def contribute_to_class(self, cls, field_name):
        if self.verbose_name is None:
            self.verbose_name = field_name.replace("_", " ").capitalize()

        for language in self:
            self[language].verbose_name = "%s (%s)" % (self.verbose_name, language)
            # Save a reference to the composite field for later use
            self[language].composite_field = self

        super(LocalizedField, self).contribute_to_class(cls, field_name)

        # monkeypatch some helper functions to the class
        cls.get_localized = get_localized
        cls.set_localized = set_localized
        cls.set_all_localized = set_all_localized

    def get(self, model):
        # get current value
        translation = getattr(model, self.prefix + short_language())

        if self.fallback is False:
            # we don't fallback, return the value
            return translation

        translated_languages = getattr(model, "translated_languages", "")
        # only applies to models with translated_languages
        if get_language() is None:
            language = ""
        else:
            language = get_language()
        if translated_languages:
            # fallback to default if language not translated
            if language not in translated_languages:
                return getattr(
                    model, self.prefix + short_language(settings.LANGUAGE_CODE)
                )
        else:
            if language not in getattr(model.parent, "translated_languages", ""):
                return getattr(
                    model, self.prefix + short_language(settings.LANGUAGE_CODE)
                )

        if translation or not self.fallback:
            # show translation only if it exists or we have disabled fallback
            return translation

        # fallback to default language
        return getattr(model, self.prefix + short_language(settings.LANGUAGE_CODE))

    def set(self, model, value):
        from django.utils.functional import Promise

        # XXX is there a better way to detect ugettext_lazy objects?
        if isinstance(value, Promise):
            d = {}
            for language in self:
                with translation.override(language):
                    d[language] = str(value)
            value = d
        return super(LocalizedField, self).set(model, value)


class LocalizedCharField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedCharField, self).__init__(models.CharField, *args, **kwargs)


class LocalizedTextField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedTextField, self).__init__(models.TextField, *args, **kwargs)


class LocalizedFileField(LocalizedField):
    def __init__(self, *args, **kwargs):
        # call the grandparent's init()
        upload_to_params = kwargs.pop("upload_to_params", None)

        super(LocalizedField, self).__init__()
        field_class = kwargs.pop("field_class", models.FileField)
        self.verbose_name = kwargs.pop("verbose_name", None)
        # fallback to english version by default
        self.fallback = kwargs.pop("fallback", True)
        # when we're localized, the field can always be empty in one language
        if "blank" in kwargs:
            del kwargs["blank"]

        # set a higher max length for filenames
        kwargs["max_length"] = 255

        for language in SHORT_LANGUAGES:
            if not upload_to_params:
                upload_to_params = {}
            upload_to_params.update({"language": language})
            kwargs["upload_to"] = LanguageAwareUploadToDirectory(**upload_to_params)

            self[language] = field_class(blank=True, *args, **kwargs)


class LocalizedImageField(LocalizedFileField):
    def __init__(self, *args, **kwargs):
        kwargs["field_class"] = models.ImageField
        super(LocalizedImageField, self).__init__(models.ImageField, *args, **kwargs)


class LocalizedBooleanField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedBooleanField, self).__init__(
            models.BooleanField, *args, **kwargs
        )


class LocalizedDateField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedDateField, self).__init__(models.DateField, *args, **kwargs)


class LocalizedForeignKey(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedForeignKey, self).__init__(models.ForeignKey, *args, **kwargs)


class LocalizedURLField(LocalizedField):
    def __init__(self, *args, **kwargs):
        kwargs["fallback"] = kwargs.get("fallback", True)
        super(LocalizedURLField, self).__init__(models.URLField, *args, **kwargs)


class LocalizedDecimalField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedDecimalField, self).__init__(
            models.DecimalField, *args, **kwargs
        )


class LocalizedIntegerField(LocalizedField):
    def __init__(self, *args, **kwargs):
        super(LocalizedIntegerField, self).__init__(
            models.IntegerField, *args, **kwargs
        )
