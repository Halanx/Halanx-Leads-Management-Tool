STATUS_OPEN = "Open"
STATUS_NOT_ATTEMPTED = "Not Attempted"
STATUS_ATTEMPTED = "Attempted"
STATUS_CONTACTED = "Contacted"
STATUS_NEW_OPPORTUNITY = "New Opportunity"
STATUS_CUSTOMER = "Customer"
STATUS_ADDITIONAL_CONTACT = "Additional Contact"
STATUS_DISQUALIFIED = "Disqualified"

# New categories
STATUS_FOLLOW_UP = "Follow Up"
STATUS_NOT_INTERESTED = "Not Interested"
STATUS_CONVERTED = "Converted"
STATUS_VISIT_SCHEDULED = "Scheduled Visit"

LEAD_STATUS_CATEGORIES = (
    (STATUS_OPEN, "black"),
    (STATUS_NOT_ATTEMPTED, "gray"),
    (STATUS_ATTEMPTED, "lightgray"),
    (STATUS_CONTACTED, "orange"),
    (STATUS_NEW_OPPORTUNITY, "greenyellow"),
    (STATUS_CUSTOMER, "green"),
    (STATUS_ADDITIONAL_CONTACT, "blueviolet"),
    (STATUS_DISQUALIFIED, "red"),

    # New Categories
    (STATUS_FOLLOW_UP, 'teal'),
    (STATUS_NOT_INTERESTED, 'maroon'),
    (STATUS_CONVERTED, 'olive'),
    (STATUS_VISIT_SCHEDULED, 'aqua'),

)

# predefined lead activity category
ADDED_NEW_LEAD = "Added new lead"

OWNER_LEAD_STATUS_CATEGORIES = (STATUS_OPEN, STATUS_NOT_ATTEMPTED, STATUS_CONTACTED, STATUS_FOLLOW_UP,
                                STATUS_NOT_INTERESTED, STATUS_CONVERTED)

TENANT_LEAD_STATUS_CATEGORIES = (STATUS_OPEN, STATUS_NOT_ATTEMPTED, STATUS_CONTACTED, STATUS_FOLLOW_UP,
                                 STATUS_VISIT_SCHEDULED, STATUS_NOT_INTERESTED, STATUS_CONVERTED)

DATA = 'data'
SOURCE_NAME = 'source_name'
REFERRAL = 'Referral'
AFFILIATE = 'Affiliate'
TASK_TYPE = 'task_type'

UPDATE_TENANT_LEAD_ACTIVITY_STATUS = 'update_tenant_lead_activity_status'
UPDATE_HOUSE_OWNER_LEAD_ACTIVITY_STATUS = 'update_house_owner_lead_activity_status'


# Affiliate Constants
PENDING = 'pending'
SUCCESS = 'success'
CANCELLED = 'cancelled'

METADATA = 'metadata'