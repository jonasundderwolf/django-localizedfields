from django.db import models

from localizedfields import fields
from localizedfields.models import TranslatableModel


class Document(TranslatableModel):
    untranslated_charfield = models.CharField(max_length=50, blank=True)
    charfield = fields.LocalizedCharField(max_length=50)
    textfield = fields.LocalizedTextField(max_length=500, blank=True)
    filefield = fields.LocalizedFileField(null=True, upload_to="files", blank=True)
    imagefield = fields.LocalizedImageField(null=True, upload_to="images", blank=True)
    # booleanfield = fields.LocalizedBooleanField()
    datefield = fields.LocalizedDateField(blank=True, null=True)
    fkfield = fields.LocalizedForeignKey(
        "self", null=True, blank=True, related_name="+", on_delete=models.CASCADE
    )
    urlfied = fields.LocalizedURLField(null=True, blank=True)
    decimalfield = fields.LocalizedDecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    integerfield = fields.LocalizedIntegerField(null=True, blank=True)

    def __str__(self):
        return "%d, %s" % (self.pk, self.charfield)

    class Meta:
        app_label = "example"
