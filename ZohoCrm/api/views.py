import traceback

from rest_framework.decorators import api_view
from rest_framework.response import Response
from zcrmsdk import ZCRMRecord, ZCRMUser, ZCRMModule, ZCRMException

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


# execute copy paste command exec('\n'.join(list(map(lambda x: x[8:], pyperclip.paste().split("\n")))))

def create_zoho_lead_from_tenant_lead_data(tenant_lead):
    if not tenant_lead.zoho_id:  # send record only if it does not have zoho id initally
        try:
            record_ins_list = list()
            record = ZCRMRecord.get_instance('Leads')
            full_name = tenant_lead.name
            last_name = str(full_name)
            if full_name:
                last_name = full_name.split()[-1]
            record.set_field_value('Last_Name', last_name)
            record.set_field_value('Lead_Type', 'Tenant')

            if tenant_lead.name:
                record.set_field_value('Name1', tenant_lead.name)

            if tenant_lead.gender:
                record.set_field_value('Gender', tenant_lead.gender)

            if tenant_lead.phone_no:
                record.set_field_value('Mobile', tenant_lead.phone_no)

            if tenant_lead.email:
                record.set_field_value('Email', tenant_lead.email)

            if tenant_lead.description:
                record.set_field_value('Description', tenant_lead.description)

            if tenant_lead.space_type:
                record.set_field_value('AccomodationType', tenant_lead.space_type)

            if tenant_lead.space_subtype:
                record.set_field_value('Space_Sub_Type', tenant_lead.space_subtype)

            if tenant_lead.accomodation_for:
                record.set_field_value('Accommodation_For', tenant_lead.accomodation_for)

            if tenant_lead.preferred_location:
                if tenant_lead.preferred_location.street_address:
                    record.set_field_value('Street', tenant_lead.preferred_location.street_address)

                if tenant_lead.preferred_location.zone:
                    record.set_field_value('Zone', tenant_lead.preferred_location.zone)

            if tenant_lead.created_by.zoho_id:
                user = ZCRMUser.get_instance(tenant_lead.created_by.zoho_id)
                record.set_field_value('Owner', user)

            # Demand Data

            demand_data = {}

            if tenant_lead.expected_rent_min:
                demand_data['Rental_Budget'] = int(tenant_lead.expected_rent_min)
            if tenant_lead.expected_rent_max:
                demand_data['Max_Rental_Budget'] = int(tenant_lead.expected_rent_max)
            if tenant_lead.expected_movein_start:
                demand_data['Move_In_Date'] = tenant_lead.expected_movein_start.strftime("%Y-%m-%d")
            if tenant_lead.expected_movein_end:
                demand_data['TO_Move_in_date'] = tenant_lead.expected_movein_end.strftime("%Y-%m-%d")

            if demand_data:
                record.set_field_value('Demand', [demand_data])

            record_ins_list.append(record)

            resp = ZCRMModule.get_instance('Leads').create_records(record_ins_list)
            bulk_entity_response, bulk_status_code = resp.bulk_entity_response, resp.status_code
            single_record_data = bulk_entity_response[0]

            if bulk_status_code == 201:
                if single_record_data.status == SUCCESS:
                    tenant_lead.zoho_id = single_record_data.response_json['details']['id']
                    tenant_lead.save()

                else:
                    sentry_debug_logger.debug('status code for single record is' + str(single_record_data.status) +
                                              'and message is' + str(single_record_data.message))
            else:
                print(single_record_data.details)
                sentry_debug_logger.debug('status code for bulk record is' + str(resp.status_code) +
                                          'and message is' + str(resp.message) + "error due to" + str(
                    single_record_data.details))

            # print(resp.status_code)
            # entity_responses = resp.bulk_entity_response
            # for entity_response in entity_responses:
            #     print(entity_response.details)
            #     print(entity_response.status)
            #     print(entity_response.message)
        except ZCRMException as ex:
            # print(ex.status_code)
            # print(ex.error_message)
            # print(ex.error_code)
            # print(ex.error_details)
            # print(ex.error_content)
            print(traceback.format_exc())
            sentry_debug_logger.error(ex, exc_info=True)

        except Exception as E:
            print(traceback.format_exc())
            sentry_debug_logger.error(E, exc_info=True)


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
