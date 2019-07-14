from django.conf.urls import url
from leads.api import views

urlpatterns = [

    # New leads from affiliate.halanx.com
    url('tenant/referrals/$', views.tenant_referral_lead_create_view),
    url('owner/referrals/$', views.owner_referral_lead_create_view),
    url('tenant/referrals/bulk/$', views.tenant_csv_referral_lead_create_view),
    url('owner/referrals/bulk/$', views.owner_csv_referral_lead_create_view),

    # leads update
    url('referrals/update/$', views.tenant_booking_and_visit_referrals_status_update_view),
]