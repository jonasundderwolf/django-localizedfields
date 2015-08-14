from django.utils.translation import activate
import pytest


@pytest.mark.django_db
def test_simple_language_switch(document):
    document.save()
    activate('en')
    assert document.charfield == "Name"
    activate('ru')
    assert document.charfield == "назва́ние"
