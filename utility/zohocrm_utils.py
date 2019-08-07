import requests
import zcrmsdk
from zcrmsdk import ZohoOAuth
from zcrmsdk import ZCRMModule, ZCRMException, ZohoOAuth, ZCRMRecord


def run_crm_code():
    import json

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
        'client_id': '1000.UYJPCFYBV2OU786465YX3Z93CH9UDV',
        'client_secret': '37dc032989af2ee358a164699908bb70b4ff74221c',
        'redirect_uri': "http://localhost:8000/some_path",
        'accounts_uri': 'https://accounts.zoho.com',
        'token_persistence_path': '.',
        'currentUserEmail': 'sidhant@halanx.com'
    }

    client = zcrmsdk.ZCRMRestClient
    client.initialize(config_dict=config_dict)
    oauth_client = ZohoOAuth.get_client_instance()
    grant_token = "1000.c32a448ce9390aa58f8bbc1326c2d869.3384575f51c8c72270bc12ad09dd4f31"
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


class ZohoCrm:
    grant_token = "1000.775208865a6601dabfcacc58faffa3ea.42430a4b89d13cb2c2902c8a08e76b41"
    refresh_token_url = 'https://accounts.zoho.com/oauth/v2/token?code={grant_token}&redirect_uri={redirect_uri}&client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code'

    def __init__(self, configuration_dict):
        self.config_dict = configuration_dict
        self.client = zcrmsdk.ZCRMRestClient
        self.client.initialize(config_dict=configuration_dict)
        self.oauth_client = ZohoOAuth.get_client_instance()
        self.oauth_tokens = self.oauth_client.generate_access_token(self.grant_token)

    def get_refresh_token(self):
        args = {
            '{grant_token}': self.grant_token,
            '{redirect_uri}': self.config_dict['redirect_uri'],
            '{client_id}': self.config_dict['client_id'],
            '{client_secret}': self.config_dict['client_secret']
        }
        url = self.refresh_token_url.format(**args)
        print(url)
        r = requests.get(url)
        return r


config_dict = {
    'sandbox': 'False',
    'applicationLogFilePath': './log',
    'client_id': '1000.06S4J0VBOROM09200TI1N32R0KCY8V',
    'client_secret': 'a52c0c14566d1d87affceaefc0965e8b39d6e0a36e',
    'redirect_uri': "http://localhost:8000/some_path",
    'accounts_uri': 'https://accounts.zoho.com',
    'token_persistence_path': '.',
    'currentUserEmail': 'sidhant@halanx.com'
}

# x = ZohoCrm(configuration_dict=config_dict)


import json
import zcrmsdk
from zcrmsdk import ZCRMModule, ZCRMException, ZohoOAuth, ZCRMRecord

config_dict = {
    'sandbox': 'False',
    'applicationLogFilePath': './log',
    'client_id': '1000.BFA8RFBJRB6407944FHG5EYIQ8AYAV',
    'client_secret': 'ef3e0ef9bc7ef76ae463c8419b1c9b1bc0dece17c9',
    'redirect_uri': "http://localhost:8000/a",
    'accounts_uri': 'https://accounts.zoho.in',
    'token_persistence_path': '.',
    'currentUserEmail': 'nimish4july1998@gmail.com'
}

client = zcrmsdk.ZCRMRestClient
client.initialize(config_dict=config_dict)
oauth_client = ZohoOAuth.get_client_instance()
grant_token = "1000.f2aa9db834d898a95079abb7003ba70b.4e41b8c215d88a92cfd9b392b75b754b"
oauth_tokens = oauth_client.generate_access_token(grant_token)
print(oauth_tokens)

# Working vesion
import zcrmsdk
import zcrmsdk
from zcrmsdk import ZohoOAuth
from zcrmsdk import ZCRMModule, ZCRMException, ZohoOAuth, ZCRMRecord

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
grant_token = "1000.4b17cdfec048c90ae5c3b7cecef77db6.30c15eaad506a9d15fa1909afdbef6a7"
oauth_tokens = oauth_client.generate_access_token(grant_token)
print(oauth_tokens)

refresh_token = oauth_tokens.refreshToken
user_identifier = "nimish4july1998@gmail.com"
oauth_tokens = oauth_client.refresh_access_token(refresh_token, user_identifier)

k = ZCRMRecord.get_instance('Leads', 4119895000000229431)
result = k.get()
