from rest_framework.decorators import api_view
from rest_framework.response import Response
from zcrmsdk import ZCRMRecord

from common.utils import get_reverse_dictionary_from_list_of_tuples, GenderChoices, HouseSpaceTypeCategories
from lead_managers.models import LeadManager
from leads.models import LeadSourceCategory, TenantLead
from utility.logging_utils import sentry_debug_logger
from utility.response_utils import STATUS, SUCCESS, ERROR


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
    zone = lead_data['Zone']
    street = lead_data['Street']

    accomodation_for = [str(i).lower() for i in lead_data['Accommodation_For']]
    space_type = None
    space_sub_type = lead_data['Space_Sub_Type']

    arguments_create_dict = {}

    # Space Type
    try:
        accomodation_type = lead_data['AccomodationType']
        if accomodation_type:
            space_type = get_reverse_dictionary_from_list_of_tuples(HouseSpaceTypeCategories)[accomodation_type]
    except Exception as E:
        sentry_debug_logger.error(E, exc_info=True)

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

    if space_sub_type:
        arguments_create_dict['space_subtype'] = space_sub_type

    if len(demand):
        try:
            if demand[0]['Move_In_Date']:
                arguments_create_dict['expected_movein_start'] = demand[0]['Move_In_Date']

            if demand[0]['Rental_Budget']:
                arguments_create_dict['expected_rent_min'] = demand[0]['Rental_Budget']

            if demand[0]['Max_Rental_Budget']:
                arguments_create_dict['expected_rent_max'] = demand[0]['Max_Rental_Budget']

            if demand[0]['TO_Move_in_date']:
                arguments_create_dict['expected_movein_end'] = demand[0]['TO_Move_in_date']

        except Exception as E:
            sentry_debug_logger.error(E, exc_info=True)

    category, _ = LeadSourceCategory.objects.get_or_create(name=lead_data['Lead_Source'])
    lead = TenantLead.objects.create(**arguments_create_dict)

    lead.source.category = category
    lead.source.name = ''
    lead.source.save()
    lead.save()

    address_update_condition = zone or street
    if address_update_condition:
        if zone:
            lead.preferred_location.zone = zone
        if street:
            lead.preferred_location.street_address = street

        lead.preferred_location.save()
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
