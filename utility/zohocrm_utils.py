def run_crm_code():
    import json

    from zcrmsdk import ZCRMModule, ZCRMException, ZohoOAuth, ZCRMRecord
    #
    #
    # def get_records(self):
    #     try:
    #         module_ins = ZCRMModule.get_instance('Products')
    #         print(dir(module_ins))
    #         resp = module_ins.get_records()
    #     except ZCRMException as ex:
    #         print(ex.status_code)
    #         print(ex.error_message)
    #         print(ex.error_code)
    #         print(ex.error_details)
    #         print(ex.error_content)

    import zcrmsdk

    config_dict = {
        'sandbox': 'False',
        'applicationLogFilePath': './log',
        'client_id': '1000.Q0DSOKM0QOD9086375JMMVXG5BCIBH',
        'client_secret': '7b224cacb9ac4439a89bb3d46940698e1e99447e34',
        'redirect_uri': "http://localhost:8000/some_path",
        'accounts_uri': 'https://accounts.zoho.com',
        'token_persistence_path': '.',
        'currentUserEmail': 'nimish4july1998@gmail.com'
    }

    client = zcrmsdk.ZCRMRestClient
    client.initialize(config_dict=config_dict)
    oauth_client = ZohoOAuth.get_client_instance()
    grant_token = "1000.edae63ad99787b40f563ade97ab830ef.6f1a4b4ec483835bb8536395314e5e2b"
    oauth_tokens = oauth_client.generate_access_token(grant_token)
    print(oauth_tokens)

    k = ZCRMRecord.get_instance('Leads', 4119895000000229431)
    result = k.get()
    print(result.data)
    print(result.data.field_data)

    records_list = ZCRMModule.get_instance('Leads')
    result = records_list.get_records()
    print(result.status_code)
    print(result.data)


zohocrm_keys_to_lead_tool_keys_mapping = {
    'mobile': 'phone_no',
    'gender': 'gender',
    'name': 'name',
    'phone_no': 'phone_no',
    'email': 'email',
    'lead source': 'lead_source',
    'accomodation_type': 'accomodation_type',
}
