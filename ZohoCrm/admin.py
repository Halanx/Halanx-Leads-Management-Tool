from django.contrib import admin

# Register your models here.
from ZohoCrm.models import ZohoConstant


@admin.register(ZohoConstant)
class ZohoConstantModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
