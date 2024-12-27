from django.contrib import admin
from django.urls import path, include
from hospital.views import index
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('hospital.urls')),
    path('', include('patients.urls')),
    path('', include('payment.urls')),
    path('', index, name = 'home'),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon/favicon.ico')))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
