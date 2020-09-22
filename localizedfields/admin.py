import json
import re

from django.conf import global_settings, settings
from django.conf.urls import url
from django.contrib.admin import SimpleListFilter
from django.forms import widgets
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from .utils import SHORT_LANGUAGES, localized_field, short_language

LANGUAGE_NAMES = dict(global_settings.LANGUAGES)


class TranslationFilter(SimpleListFilter):
    title = "translated language"
    parameter_name = "translated"

    def lookups(self, request, model_admin):
        return [(l, LANGUAGE_NAMES.get(l, l)) for l in SHORT_LANGUAGES]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(translated_languages__contains=self.value())
        return queryset


class VisibilityFilter(SimpleListFilter):
    title = "visibility"
    parameter_name = "visibility"

    def lookups(self, request, model_admin):
        return [(l, LANGUAGE_NAMES.get(l, l)) for l in SHORT_LANGUAGES]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{"visible_%s" % self.value(): True})
        return queryset


class TranslatedFieldsMixin(object):
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(TranslatedFieldsMixin, self).get_fieldsets(request, obj)

        # group fieldsets by language
        localized_fieldsets = dict(
            [
                (
                    lang,
                    (
                        _(LANGUAGE_NAMES.get(lang, lang)),
                        {
                            "fields": [],
                            "classes": ["language", lang],
                        },
                    ),
                )
                for lang in SHORT_LANGUAGES
            ]
        )
        remove_fieldsets = []

        for o, (name, attrs) in enumerate(fieldsets):
            if "language" in attrs.get("classes", {}):
                # language fieldsets exist already, skip - we already reworked this form
                return fieldsets
            to_remove = []
            attrs["fields"] = list(attrs["fields"])
            rex = re.compile(r"(.*)_(%s)$" % "|".join(SHORT_LANGUAGES))
            for i, field in enumerate(attrs["fields"]):
                if isinstance(field, str):
                    match = rex.match(field)
                    if match:
                        if match.group(1) == "visible":
                            if match.group(2) == short_language(settings.LANGUAGE_CODE):
                                attrs["fields"][i] = tuple(
                                    ["visible_%s" % lang for lang in SHORT_LANGUAGES]
                                )
                            else:
                                to_remove.append(i)
                        elif match.group(2) == short_language(settings.LANGUAGE_CODE):
                            for lang in SHORT_LANGUAGES:
                                localized_fieldsets[lang][1]["fields"].append(
                                    localized_field(match.group(1), lang)
                                )
                            to_remove.append(i)
                        else:
                            to_remove.append(i)

            for i in reversed(to_remove):
                attrs["fields"].pop(i)
            if not len(attrs["fields"]) and name != "FEINCMS_CONTENT":
                remove_fieldsets.append(o)

        for i in reversed(remove_fieldsets):
            fieldsets.pop(i)

        insert_here = 0
        for i, (name, attrs) in enumerate(fieldsets):
            insert_here = i
            if name == "FEINCMS_CONTENT":
                break

        for lang in SHORT_LANGUAGES:
            # insert new language fieldsets _before_ feincms content
            if insert_here:
                fieldsets.insert(insert_here, localized_fieldsets[lang])
                insert_here += 1
            else:
                fieldsets.append(localized_fieldsets[lang])

        return fieldsets

    def linked_languages(self, obj):
        s = []
        for lang in SHORT_LANGUAGES:
            visible = obj.get_localized(lang, "visible")
            translated = lang in obj.translated_languages
            if visible:
                if translated:
                    s.append(
                        '<a href="%s/?lang=%s">%s</a>' % (obj.pk, lang, lang.upper())
                    )
                else:
                    s.append("<span>%s</span>" % lang.upper())

        return format_html(" | ".join(s))

    linked_languages.allow_tags = True
    linked_languages.short_description = "Languages"

    def export_js_variables(self, request):
        return HttpResponse(
            json.dumps(
                {
                    "languages": [(k, force_text(v)) for k, v in settings.LANGUAGES],
                    "default_language": short_language(settings.LANGUAGE_CODE),
                    "translation_label": _("Show translations for"),
                    "fallback_label": _("Fallback to %(language)s")
                    % {"language": dict(settings.LANGUAGES)[settings.LANGUAGE_CODE]},
                }
            ),
            content_type="application/json",
        )

    def get_urls(self):
        urls = super(TranslatedFieldsMixin, self).get_urls()
        return [
            url(r"^localizedfields/", self.export_js_variables),
        ] + urls

    @property
    def media(self):
        css = {"all": ("localizedfields/localizedfields.css",)}
        js = (
            "localizedfields/js.cookie.min.js",
            "localizedfields/localizedfields.js",
        )

        return super(TranslatedFieldsMixin, self).media + widgets.Media(css=css, js=js)


class TranslatableAdminMixin(TranslatedFieldsMixin):
    """
    Mixin class that allows LocalizedFields in admin fieldsets declaration and
    sets them automatically correctly when necessary.
    """

    list_display = ["__str__"]

    def __init__(self, *args, **kwargs):
        super(TranslatableAdminMixin, self).__init__(*args, **kwargs)
        self.list_filter = list(self.list_filter) + [
            TranslationFilter,
            VisibilityFilter,
        ]
        if "linked_languages" not in self.list_display:
            self.list_display = list(self.list_display) + ["linked_languages"]
