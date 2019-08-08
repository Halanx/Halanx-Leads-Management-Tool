from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from utility.environments import DEVELOPMENT
from utility.zohocrm.zohocrm_leads import get_oauthclient_oauth_token_access_token

get_oauthclient_oauth_token_access_token()

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include('lead_managers.urls')),
    url(r'api/leads/', include('leads.api.urls')),  # Tenant, Owner Single/Bulk Referral Lead create View
]

if settings.DEBUG and settings.ENVIRONMENT == DEVELOPMENT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
