from rest_framework import serializers

from leads.models import TenantLeadActivity


class TenantLeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLeadActivity
        fields = '__all__'
