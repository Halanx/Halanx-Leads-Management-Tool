import json

import requests
from decouple import config

from affiliate_lead.utils import TENANT_LEAD_REFERRAL_UPDATE_URL
from leads.api.serializers import TenantLeadActivitySerializer
from leads.utils import DATA, TASK_TYPE, UPDATE_TENANT_LEAD_ACTIVITY_STATUS, STATUS_DISQUALIFIED, CANCELLED, PENDING, \
    STATUS_CONVERTED, STATUS_VISIT_SCHEDULED, METADATA
from utility.logging_utils import sentry_debug_logger
from utility.response_utils import STATUS, SUCCESS


def get_appropriate_status_of_lead_activity_for_affiliate_tool(lead_activity):
    try:
        if lead_activity.post_status.name in [STATUS_DISQUALIFIED, ]:
            return CANCELLED

        elif lead_activity.post_status.name in [STATUS_CONVERTED, STATUS_VISIT_SCHEDULED]:
            return SUCCESS

        else:
            return PENDING

    except Exception as E:
        print(E)
        sentry_debug_logger.debug("error due to " + str(E))
        return PENDING


def update_tenant_lead_activity_status_in_affiliate_tool(tenant_lead_activity):
    request_data = {
        TASK_TYPE: UPDATE_TENANT_LEAD_ACTIVITY_STATUS,
        DATA: TenantLeadActivitySerializer(tenant_lead_activity).data,
        METADATA: {'referral_status': get_appropriate_status_of_lead_activity_for_affiliate_tool(
            lead_activity=tenant_lead_activity)}
    }

    sentry_debug_logger.debug('data is ' + str(request_data))
    print(request_data, 'updating tenant lead activity status')

    tenant_referral_id = None
    if tenant_lead_activity.lead.referral_id:
        tenant_referral_id = tenant_lead_activity.lead.referral_id

    if tenant_referral_id:
        req = requests.patch(TENANT_LEAD_REFERRAL_UPDATE_URL.format(**{'pk': tenant_referral_id}),
                             data=json.dumps(request_data),
                             headers={'Content-type': 'application/json'},
                             timeout=10,
                             auth=(config('AFFILIATE_TOOL_ADMIN_USERNAME'), config('AFFILIATE_TOOL_ADMIN_PASSWORD')))

        print(req.status_code)
        print(str(req.content))

        if req.status_code == 200:
            if req.json()[STATUS] == SUCCESS:
                tenant_lead_activity.acknowledged_by_affiliate = True
                tenant_lead_activity.save()
