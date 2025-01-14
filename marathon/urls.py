from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin_panel/', admin.site.urls),
    path('', include('front.urls')),
    path('api/', include('api.urls')),
]

urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
