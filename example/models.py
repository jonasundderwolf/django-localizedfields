from django.db import models
import i18n
from i18n.models import TranslatableModel


class Document(TranslatableModel):
    untranslated_charfield = models.CharField(max_length=50, blank=True)
    charfield = i18n.LocalizedCharField(max_length=50)
    textfield = i18n.LocalizedTextField(max_length=500, blank=True)
    filefield = i18n.LocalizedFileField(null=True, upload_to='files', blank=True)
    imagefield = i18n.LocalizedImageField(null=True, upload_to='images', blank=True)
    # booleanfield = i18n.LocalizedBooleanField()
    datefield = i18n.LocalizedDateField(blank=True, null=True)
    fkfield = i18n.LocalizedForeignKey('self', null=True, blank=True,
                                       related_name='+')
    urlfied = i18n.LocalizedURLField(null=True, blank=True)
    decimalfield = i18n.LocalizedDecimalField(max_digits=4, decimal_places=2, null=True,
                                              blank=True)
    integerfield = i18n.LocalizedIntegerField(null=True, blank=True)

    def __str__(self):
        return '%d, %s' % (self.pk, self.charfield)

    class Meta:
        app_label = 'example'
