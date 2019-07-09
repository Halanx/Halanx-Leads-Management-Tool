from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser

from leads.models import TenantLead, HouseOwnerLead
from utility.response_utils import STATUS, SUCCESS, ERROR


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def tenant_referral_lead_create_view(request):
    """It is used to create a lead for each tenant referral"""
    if request.user.is_superuser:
        data = request.data
        print(data, 'hi')
        try:
            TenantLead.objects.create(**data)
            response_json = {STATUS: SUCCESS}
            return JsonResponse(response_json, status=200)
        except Exception as E:
            response_json = {STATUS: ERROR, 'message': str(E)}
            return JsonResponse(response_json, status=400)


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def owner_referral_lead_create_view(request):
    """It is used to create a lead for each owner referral"""
    if request.user.is_superuser:
        data = request.data
        print(data, 'hi')
        try:
            HouseOwnerLead.objects.create(**data)
            response_json = {STATUS: SUCCESS}
            return JsonResponse(response_json, status=200)
        except Exception as E:
            response_json = {STATUS: ERROR, 'message': str(E)}
            return JsonResponse(response_json, status=400)


