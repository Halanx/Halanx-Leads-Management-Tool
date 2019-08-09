from utility.logging_utils import sentry_debug_logger
from utility.zohocrm.zohocrm_leads import get_oauthclient_oauth_token_access_token
try:
    get_oauthclient_oauth_token_access_token()
except Exception as E:
    sentry_debug_logger.error(E, exc_info=True)
