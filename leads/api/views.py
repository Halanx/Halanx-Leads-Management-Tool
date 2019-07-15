from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser

from affiliates.models import Affiliate
from leads.models import TenantLead, HouseOwnerLead, LeadSourceCategory, TenantLeadActivity, LeadActivityCategory
from leads.utils import DATA, SOURCE_NAME, AFFILIATE, METADATA, TASK_TYPE, UPDATE_LEAD_REFERRAL_STATUS, SUB_TASK, \
    BOOKING, BOOKING_COMPLETE, ADDED_NEW_LEAD, BOOKED_HOUSE, STATUS_HOME_BOOKED
from referrals.models import TenantReferral
from utility.logging_utils import sentry_debug_logger
from utility.response_utils import STATUS, SUCCESS, ERROR, MESSAGE


def update_lead_referral_status(lead, source_name):
    lead.source.category, _ = LeadSourceCategory.objects.get_or_create(name=AFFILIATE)
    lead.source.name = source_name
    lead.source.save()
    lead.save()


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def tenant_referral_lead_create_view(request):
    """It is used to create a lead for each tenant referral"""
    if request.user.is_superuser:
        data = request.data[DATA]

        source_name = request.data[SOURCE_NAME]
        metadata = data.pop(METADATA, {})
        try:
            data['referral_id'] = metadata.get('referral_id', None)
            lead = TenantLead.objects.create(**data)
            response_json = {STATUS: SUCCESS}
            update_lead_referral_status(lead, source_name)
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
        data = request.data[DATA]
        source_name = request.data[SOURCE_NAME]
        metadata = data.pop(METADATA, {})
        try:
            data['referral_id'] = metadata.get('referral_id', None)
            lead = HouseOwnerLead.objects.create(**data)
            update_lead_referral_status(lead, source_name)
            response_json = {STATUS: SUCCESS}
            return JsonResponse(response_json, status=200)
        except Exception as E:
            response_json = {STATUS: ERROR, 'message': str(E)}
            return JsonResponse(response_json, status=400)


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def tenant_csv_referral_lead_create_view(request):
    """It is used to create leads for all referrals in csv"""
    if request.user.is_superuser:
        source_name = request.data[SOURCE_NAME]
        status_response_list = []
        data_list = request.data[DATA]  # List of referrals
        for data in data_list:
            metadata = data.pop(METADATA, {})
            try:
                data['referral_id'] = metadata.get('referral_id', None)
                lead = TenantLead.objects.create(**data)
                update_lead_referral_status(lead, source_name)
                response_json = {STATUS: SUCCESS}
                status_response_list.append(response_json)
            except Exception as E:
                response_json = {STATUS: ERROR, 'message': str(E)}
                status_response_list.append(response_json)

        return JsonResponse(status_response_list, safe=False)


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def owner_csv_referral_lead_create_view(request):
    """It is used to create leads for all referrals in csv"""
    if request.user.is_superuser:
        source_name = request.data[SOURCE_NAME]
        status_response_list = []
        data_list = request.data[DATA]  # List of referrals
        for data in data_list:
            metadata = data.pop(METADATA, {})
            try:
                data['referral_id'] = metadata.get('referral_id', None)
                lead = HouseOwnerLead.objects.create(**data)
                update_lead_referral_status(lead, source_name)
                response_json = {STATUS: SUCCESS}
                status_response_list.append(response_json)
            except Exception as E:
                response_json = {STATUS: ERROR}
                status_response_list.append(response_json)

        print(status_response_list)
        return JsonResponse(status_response_list, safe=False)


@api_view(('POST',))
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAdminUser,))
def tenant_booking_and_visit_referrals_status_update_view(request):
    sentry_debug_logger.debug('request received', exc_info=True)
    task_type = request.data[TASK_TYPE]

    # Different tasks to be performed from Halanx App

    if task_type == UPDATE_LEAD_REFERRAL_STATUS:

        if request.data[SUB_TASK] == BOOKING:
            if request.data[STATUS] == BOOKING_COMPLETE:
                ref_id = request.data[DATA]['affiliate_code']
                phone_no = request.data[DATA]['phone_no']

                affiliate = Affiliate.objects.using(settings.AFFILIATE_DB).filter(unique_code=ref_id)
                if affiliate:
                    # Search the corresponding lead to add new lead activity

                    # Getting the Tenant Referral
                    tenant_referral = TenantReferral.objects.using(settings.AFFILIATE_DB).filter(
                        affiliate=affiliate, phone_no=phone_no).first()

                    if tenant_referral:
                        # Getting the tenant lead from tenant referral id
                        tenant_lead = TenantLead.objects.filter(referral_id=tenant_referral.id).first()

                        if tenant_lead:
                            # Creating Tenant Lead Activity
                            lead_activity_category, _ = LeadActivityCategory.objects.get_or_create(name=BOOKED_HOUSE)
                            TenantLeadActivity.objects.create(
                                lead=tenant_lead,
                                category=lead_activity_category,
                                post_status=STATUS_HOME_BOOKED,
                                remarks="Booking Completed by tenant registered via affiliate")

                            return JsonResponse({STATUS: SUCCESS})

    else:
        return JsonResponse({STATUS: ERROR, MESSAGE: 'No suitable task type provided'})
