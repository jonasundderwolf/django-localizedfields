import re

from django.contrib.admin import SimpleListFilter
from django.conf import settings
from django.forms import widgets
from django.utils.six import string_types

from .fields import LANGUAGES


class TranslationFilter(SimpleListFilter):
    title = 'translated language'
    parameter_name = 'translated'

    def lookups(self, request, model_admin):
        return settings.LANGUAGES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(translated_languages__contains=self.value())
        return queryset


class VisibilityFilter(SimpleListFilter):
    title = 'visibility'
    parameter_name = 'visibility'

    def lookups(self, request, model_admin):
        return settings.LANGUAGES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{'visible_%s' % self.value(): True})
        return queryset


class TranslatedFieldsMixin(object):
    change_form_template = 'admin/localized_change_form.html'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(TranslatedFieldsMixin, self).get_fieldsets(request, obj)

        # group fieldsets by language
        localized_fieldsets = dict([
            (lang, (
                name,
                {
                    'fields': [],
                    'classes': ['language', lang],
                }
            )) for lang, name in settings.LANGUAGES
        ])
        remove_fieldsets = []

        for o, (name, attrs) in enumerate(fieldsets):
            if name == dict(settings.LANGUAGES)[settings.LANGUAGE_CODE]:
                # language fieldsets exist already, skip - we already reworked this form
                return fieldsets
            to_remove = []
            attrs['fields'] = list(attrs['fields'])
            for i, field in enumerate(attrs['fields']):
                if isinstance(field, string_types):
                    match = re.match(r'^(.*)_([a-z]{2})$', field)
                    if match:
                        if match.group(1) == 'visible':
                            if match.group(2) == settings.LANGUAGE_CODE:
                                attrs['fields'][i] = tuple(
                                    ['visible_%s' % lang for lang in LANGUAGES])
                            else:
                                to_remove.append(i)
                        elif match.group(2) == settings.LANGUAGE_CODE:
                            for lang in LANGUAGES:
                                localized_fieldsets[lang][1]['fields'].append(
                                    '%s_%s' % (match.group(1), lang))
                            to_remove.append(i)
                        elif match.group(2) in LANGUAGES:
                            to_remove.append(i)

            for i in reversed(to_remove):
                attrs['fields'].pop(i)
            if not len(attrs['fields']) and name != 'FEINCMS_CONTENT':
                remove_fieldsets.append(o)

        for i in reversed(remove_fieldsets):
            fieldsets.pop(i)

        insert_here = 0
        for i, (name, attrs) in enumerate(fieldsets):
            insert_here = i
            if name == 'FEINCMS_CONTENT':
                break

        for lang, name in settings.LANGUAGES:
            # insert new language fieldsets _before_ feincms content
            if insert_here:
                fieldsets.insert(insert_here, localized_fieldsets[lang])
                insert_here += 1
            else:
                fieldsets.append(localized_fieldsets[lang])

        return fieldsets

    def linked_languages(self, obj):
        s = []
        for lang in LANGUAGES:
            visible = obj.get_localized(lang, 'visible')
            translated = lang in obj.translated_languages
            if visible:
                if translated:
                    s.append('<a href="%s/?lang=%s">%s</a>' % (obj.pk, lang, lang.upper()))
                else:
                    s.append('<span>%s</span>' % lang.upper())

        return ' | '.join(s)
    linked_languages.allow_tags = True
    linked_languages.short_description = 'Languages'

    def render_change_form(self, request, context, **kwargs):
        context.update({
            'DEFAULT_LANGUAGE': settings.LANGUAGE_CODE,
        })
        return super(TranslatedFieldsMixin, self).render_change_form(
            request, context, **kwargs)

    @property
    def media(self):
        css = {'all': ('localizedfields/localizedfields.css',)}
        js = (
            'localizedfields/js.cookie.min.js',
            'localizedfields/localizedfields.js',
        )

        return super(TranslatedFieldsMixin, self).media + widgets.Media(css=css, js=js)


class TranslatableAdminMixin(TranslatedFieldsMixin):
    '''
    Mixin class that allows LocalizedFields in admin fieldsets declaration and
    sets them automatically correctly when necessary.
    '''
    list_display = ['__str__']

    def __init__(self, *args, **kwargs):
        super(TranslatableAdminMixin, self).__init__(*args, **kwargs)
        self.list_filter = list(self.list_filter) + [TranslationFilter, VisibilityFilter]
        if 'linked_languages' not in self.list_display:
            self.list_display = list(self.list_display) + ['linked_languages']
