from django.db import models
from django.conf import settings

from .fields import LocalizedBooleanField
from .utils import LANGUAGES, get_language, i18n_field


class TranslatedManager(models.Manager):
    def get_query_set(self):
        return super(TranslatedManager, self).get_query_set().filter(
            **{i18n_field('visible'): True})


class TranslatableModel(models.Model):
    translated_languages = models.CharField('Languages',
        max_length=50, blank=True, default=settings.LANGUAGE_CODE)
    visible = LocalizedBooleanField(verbose_name='Visible', default=False)

    objects = models.Manager()
    local = TranslatedManager()

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
