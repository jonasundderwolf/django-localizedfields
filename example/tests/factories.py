# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import factory
from ..models import Document


class DocumentFactory(factory.Factory):

    class Meta:
        model = Document

    charfield_en = "Name"
    charfield_ru = "назва́ние"
    untranslated_charfield = "Untranslated field"
