from django.conf.urls import url

from lead_managers import views

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^login/$', views.login_view, name='login_page'),
    url(r'^logout/$', views.logout_view, name='logout_view'),
    url(r'^reset_password/$', views.reset_password_view, name='reset_password_view'),
    url(r'^generate_otp/$', views.generate_otp_view, name='generate_otp_view'),
    url(r'^login_otp/$', views.login_otp_view, name='login_otp_view'),

    url(r'^leads/$', views.leads_list_view, name='leads_list_view'),
    url(r'^leads/exists/$', views.lead_exists_view, name='lead_exists_view'),
    url(r'^leads/new/$', views.new_lead_form_view, name='new_lead_form_view'),
    url(r'^leads/manage/$', views.lead_manage_view, name='lead_manage_view'),
    url(r'^leads/edit/$', views.lead_edit_form_view, name='lead_edit_form_view'),
    url(r'^leads/activities/new/$', views.new_lead_activity_form_view, name='new_lead_activity_form_view'),
    url(r'^leads/activities/edit/$', views.lead_activity_form_edit_view, name='lead_activity_form_edit_view'),

    url(r'^leads/add_manager/$', views.add_lead_manager_view, name='add_lead_manager_view'),
]
