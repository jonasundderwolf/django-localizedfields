from django.contrib import admin

from localizedfields.admin import TranslatableAdminMixin

from .models import Document


class DocumentAdmin(TranslatableAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(Document, DocumentAdmin)
