import i18n
from i18n.models import TranslatableModel


class Document(TranslatableModel):

    charfield = i18n.LocalizedCharField(max_length=50)
    textfield = i18n.LocalizedTextField(max_length=512)
    filefield = i18n.LocalizedFileField(null=True, upload_to='files')
    imagefield = i18n.LocalizedImageField(null=True, upload_to='images')
    booleanfield = i18n.LocalizedBooleanField()
    datefield = i18n.LocalizedDateField()
    fkfield = i18n.LocalizedForeignKey('self', null=True, blank=True,
                                       related_name='+')
    urlfied = i18n.LocalizedURLField()
    decimalfield = i18n.LocalizedDecimalField(max_digits=4, decimal_places=2)
    integerfield = i18n.LocalizedIntegerField()

    def __unicode__(self):
        return '%d, %s' % (self.pk, self.charfield)

    class Meta:
        app_label = 'example'
