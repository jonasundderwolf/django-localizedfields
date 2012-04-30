from django.db import models

# import everything from fields, so one can simply import fields from here as well
from .fields import *
from .utils import LANGUAGES, get_language


class TranslateableModel(models.Model):
    translated_languages = models.CharField('Languages',
        max_length=50, blank=True, default='en')
    visible = LocalizedBooleanField(verbose_name='Visible', default=False)

    objects = models.Manager()

    @classmethod
    def translated_fields(cls):
        fields = []
        for field in cls._meta.fields:
            if hasattr(field, 'composite_field'):
                if field.composite_field.field_name not in fields:
                    fields.append(field.composite_field.field_name)
        return fields

    def __unicode__(self, title_attr='title'):
        if hasattr(self, title_attr):
            for lang in [get_language()] + LANGUAGES:
                title = self.get_localized(lang, title_attr)
                if title:
                    return title
        return '<%s: %s>' % (self.__class__.__name__, self.id)

    class Meta:
        abstract = True

