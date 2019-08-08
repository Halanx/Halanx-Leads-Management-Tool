import zcrmsdk
from decouple import config
from zcrmsdk import ZohoOAuth, ZCRMRecord, ZohoOAuthTokens, ZohoOAuthClient
import pickle

from zcrmsdk.Persistence import ZohoOAuthPersistenceFileHandler

from zcrmsdk.OAuthUtility import ZohoOAuthException


def load_oauth_token_and_access_token_from_pickle(oauth_client):
    try:
        x = open("zcrm_oauthtokens.pkl", "rb")
        oauth_tokens = pickle.load(x)
        refresh_token = oauth_tokens.refreshToken
        user_email = config('ZOHO_CURRENT_USER_EMAIL')

        try:
            access_token = oauth_tokens.get_access_token()
            return oauth_tokens, access_token

        except ZohoOAuthException as err:
            if err.message == 'Access token got expired!':
                print("refreshing token")
                oauth_client.refresh_access_token(refresh_token, user_email)
                access_token = oauth_tokens.get_access_token()
                return oauth_tokens, access_token

            else:
                print("error due to", err)

    except FileNotFoundError:
        print("grant token not exists file not found")


def get_oauth_client():
    config_dict = {
        'sandbox': 'False',
        'applicationLogFilePath': './log',
        'client_id': config('ZOHO_CLIENT_ID'),
        'client_secret': config('ZOHO_CLIENT_SECRET'),
        'redirect_uri': config('ZOHO_REDIRECT_URI'),
        'accounts_url': config('ZOHO_ACCOUNTS_URL'),
        'currentUserEmail': config('ZOHO_CURRENT_USER_EMAIL'),
        'apiBaseUrl': config('ZOHO_API_BASE_URL'),
        'token_persistence_path': '.',
    }

    client = zcrmsdk.ZCRMRestClient
    client.initialize(config_dict=config_dict)
    oauth_client = ZohoOAuth.get_client_instance()
    return oauth_client


def get_oauthclient_oauth_token_access_token():
    oauth_client = get_oauth_client()
    oauth_token, access_token = load_oauth_token_and_access_token_from_pickle(oauth_client)
    return oauth_client, oauth_token, access_token


class ZohoCrm:
    grant_token = "1000.775208865a6601dabfcacc58faffa3ea.42430a4b89d13cb2c2902c8a08e76b41"
    userEmail = config('ZOHO_CURRENT_USER_EMAIL')

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
