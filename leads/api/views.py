from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from zcrmsdk import ZCRMRecord

from affiliates.models import Affiliate
from common.utils import get_reverse_dictionary_from_list_of_tuples, HouseAccomodationAllowedCategories, GenderChoices, \
    HouseSpaceTypeCategories
from lead_managers.models import LeadManager
from leads.models import TenantLead, HouseOwnerLead, LeadSourceCategory, TenantLeadActivity, LeadActivityCategory, \
    TenantLeadSource
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


def create_tenant_lead_data_from_zoho_lead_data(lead_data):
    assert (lead_data['Lead_Type'] == 'Tenant')

    name = lead_data['Name1']
    gender = lead_data['Gender']
    phone_no = lead_data['Mobile']
    email = lead_data['Email']
    description = lead_data['Description']
    zoho_id = lead_data['id']
    created_by = lead_data['Created_By']
    demand = lead_data['Demand']

    accomodation_for = [str(i).lower() for i in lead_data['Accommodation_For']]
    space_type = None

    # Space Type
    try:
        space_type = get_reverse_dictionary_from_list_of_tuples(HouseSpaceTypeCategories)[lead_data['AccomodationType']]
    except Exception as E:
        sentry_debug_logger.error(E, exc_info=True)

    arguments_create_dict = {}
    if name:
        arguments_create_dict['name'] = name

    if gender:
        try:
            arguments_create_dict['gender'] = get_reverse_dictionary_from_list_of_tuples(GenderChoices)[gender]
        except Exception as E:
            sentry_debug_logger.error(E, exc_info=True)

    if phone_no:
        arguments_create_dict['phone_no'] = phone_no

    if email:
        arguments_create_dict['email'] = email

    if description:
        arguments_create_dict['description'] = description

    if zoho_id:
        arguments_create_dict['zoho_id'] = zoho_id

    if space_type:
        arguments_create_dict['space_type'] = space_type

    if accomodation_for:
        arguments_create_dict['accomodation_for'] = accomodation_for

    if created_by:
        lead_manager = LeadManager.objects.filter(zoho_id=created_by['id']).first()
        if lead_manager:
            arguments_create_dict['created_by'] = lead_manager

    if len(demand):
        try:
            arguments_create_dict['expected_movein_start'] = demand[0]['Move_In_Date']
            arguments_create_dict['expected_rent_min'] = demand[0]['Rental_Budget']
            arguments_create_dict['expected_rent_max'] = demand[0]['Max_Rental_Budget']
            arguments_create_dict['expected_movein_end'] = demand[0]['TO_Move_in_date']
        except Exception as E:
            sentry_debug_logger.error(E, exc_info=True)

    category, _ = LeadSourceCategory.objects.get_or_create(name=lead_data['Lead_Source'])
    lead = TenantLead.objects.create(**arguments_create_dict)

    lead.source.category = category
    lead.source.name = ''
    lead.source.save()
    lead.save()


@api_view(('POST',))
def new_lead_from_zoho_lead(request):
    # lead_id = request.query_params['lead_id']
    lead_id = request.data['lead_id']
    instance = ZCRMRecord.get_instance('Leads', lead_id)
    try:
        result = instance.get()
        lead_data = result.response_json['data'][0]
        create_tenant_lead_data_from_zoho_lead_data(lead_data)
        return Response({STATUS: SUCCESS})
    except Exception as E:
        sentry_debug_logger.error(E, exc_info=True)
        return Response({STATUS: ERROR, "message": 'Some Error Occured'})
