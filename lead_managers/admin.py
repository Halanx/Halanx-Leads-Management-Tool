from django.contrib import admin

from lead_managers.models import LeadManager


@admin.register(LeadManager)
class LeadManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_no', 'zoho_id')
    raw_id_fields = ('user',)
