from django.conf.urls import url
from ZohoCrm.api import views

urlpatterns = [

    # lead from zoho
    url('new_lead/', views.new_lead_from_zoho_lead),
]