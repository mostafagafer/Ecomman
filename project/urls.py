from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('admin_soft.urls')),
    path('admin/', admin.site.urls),
    path('scrapper/', include('scrapper.urls', namespace='scrapper')),
    path('contact/', include('contact.urls',namespace='contact')),
    path('client_profile/', include('client_profile.urls',namespace='client_profile')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

    path('dashboard/', include('dashboard.urls')),


]


urlpatterns +=  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)