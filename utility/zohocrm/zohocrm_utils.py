# Production version

import zcrmsdk
from decouple import config
from zcrmsdk import ZohoOAuth, ZCRMRecord

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


def get_oauth_tokens(config_dict):
    client = zcrmsdk.ZCRMRestClient
    client.initialize(config_dict=config_dict)
    oauth_client = ZohoOAuth.get_client_instance()
    grant_token = "1000.3bfcb8101c87d85775e89ff114f96eb1.a36105cf9f61c367e65876f185c088d9"
    oauth_tokens = oauth_client.generate_access_token(grant_token)
    print(oauth_tokens)
    return oauth_tokens


# refresh_token = oauth_tokens.refreshToken
# user_identifier = "sidhant@halanx.com"
# oauth_tokens = oauth_client.refresh_access_token(refresh_token, user_identifier)
#
def get_records():
    k = ZCRMRecord.get_instance('Leads', 6218000000118116)
    result = k.get()
    return result
