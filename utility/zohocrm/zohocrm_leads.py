import zcrmsdk
from zcrmsdk import ZohoOAuth, ZCRMRecord


class ZohoCrm:
    grant_token = "1000.775208865a6601dabfcacc58faffa3ea.42430a4b89d13cb2c2902c8a08e76b41"
    userEmail = 'nimish4july1998@gmail.com'

    def __init__(self, configuration_dict):
        self.config_dict = configuration_dict
        self.client = zcrmsdk.ZCRMRestClient
        self.client.initialize(config_dict=configuration_dict)
        self.oauth_client = ZohoOAuth.get_client_instance()
        self.oauth_tokens = self.oauth_client.generate_access_token(self.grant_token)

    def refresh_access_token(self):
        result = self.oauth_client.refresh_access_token(self.oauth_tokens.refreshToken, self.userEmail)
        if result:
            self.oauth_tokens = result

    def get_lead(self, lead_id):
        instance = ZCRMRecord.get_instance('Leads', lead_id)
        return instance
