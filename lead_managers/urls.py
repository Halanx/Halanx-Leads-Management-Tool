from django.conf.urls import url

from lead_managers import views

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^login/$', views.login_view, name='login_page'),
    url(r'^logout/$', views.logout_view, name='logout_view'),

    url(r'^leads/new/$', views.new_lead_form_view, name='new_lead_form_view'),

    url(r'^leads/$', views.leads_list_view, name='leads_list_view'),
]
