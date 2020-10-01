# -*- coding: utf-8 -*-
import pytest
from django.utils.translation import activate, override

from .factories import DocumentFactory


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


@pytest.mark.django_db
def test_set_fields():
    """
    Ensure direct assignment to fields does not throw an error.
    """

    document = DocumentFactory.create(
        charfield="some chars",
        textfield="some text",
        decimalfield=0.0815,
        integerfield=42,
    )

    assert document.charfield == "some chars"
    assert document.textfield == "some text"
    assert document.decimalfield == 0.0815
    assert document.integerfield == 42
