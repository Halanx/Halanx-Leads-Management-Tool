from rest_framework import serializers

from leads.models import TenantLeadActivity, HouseOwnerLeadActivity


class TenantLeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantLeadActivity
        fields = '__all__'


class HouseOwnerLeadActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseOwnerLeadActivity
        fields = '__all__'
