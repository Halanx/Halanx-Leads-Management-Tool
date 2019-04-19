from leads.models import LeadStatusCategory
from leads.utils import LEAD_STATUS_CATEGORIES


def load_status_categories():
    for status_category in LEAD_STATUS_CATEGORIES:
        LeadStatusCategory.objects.create(name=status_category[0], color=status_category[1])
