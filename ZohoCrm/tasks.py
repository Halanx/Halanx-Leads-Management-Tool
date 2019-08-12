import traceback

import time
from celery import shared_task
from zcrmsdk import ZCRMRecord, ZCRMUser, ZCRMException, ZCRMModule

from leads.models import TenantLead
from utility.logging_utils import sentry_debug_logger
from utility.response_utils import SUCCESS


@shared_task
def zoho_lead_from_tenant_lead_create_task(tenant_lead_id):
    time.sleep(1)
    # added sleep so that related objects data is also received
    tenant_lead = TenantLead.objects.get(id=tenant_lead_id)
    if not tenant_lead.zoho_id:  # send record only if it does not have zoho id initally
        try:
            tenant_lead = TenantLead.objects.get(id=tenant_lead.id)  # updated instance
            print(tenant_lead.preferred_location)
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

