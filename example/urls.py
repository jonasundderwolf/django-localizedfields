from django.conf import settings
from django.conf.urls import include, patterns, static, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    "",
    url(r"^admin/", include(admin.site.urls)),
)
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
