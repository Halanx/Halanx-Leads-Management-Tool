from django.conf.urls import url
from leads.api import views

urlpatterns = [
    url('tenant/referrals', views.tenant_referral_lead_create_view),
    url('owner/referrals', views.owner_referral_lead_create_view),
]