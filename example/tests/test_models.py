# -*- coding: utf-8 -*-
import pytest
from django.utils.translation import activate, override


@pytest.mark.django_db
def test_simple_language_switch(document):
    document.save()
    activate("en")
    assert document.charfield == "Name"
    with override("ru"):
        assert document.charfield == "назва́ние"
    activate("ru")
    assert document.charfield == "назва́ние"


@pytest.mark.django_db
def test_translated_fields(document):
    document.save()
    assert document.translated_fields() == [
        "visible",
        "charfield",
        "textfield",
        "filefield",
        "imagefield",
        "datefield",
        "fkfield",
        "urlfied",
        "decimalfield",
        "integerfield",
    ]
