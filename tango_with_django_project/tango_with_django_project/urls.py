from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView


urlpatterns = [
    path(r'', include('rango.urls')),
    path('admin/', admin.site.urls),
    path('rango/', include('rango.urls')),
    path(r'accounts/', include('registration.backends.simple.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

