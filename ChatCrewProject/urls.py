from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('ChatCrewApp.urls')),
    path('search/', include('searchapp.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    
handler404 = 'ChatCrewApp.views.handler404'
handler500 = 'ChatCrewApp.views.handler500'
