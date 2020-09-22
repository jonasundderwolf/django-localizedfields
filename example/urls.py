from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.urls import path

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
]
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
