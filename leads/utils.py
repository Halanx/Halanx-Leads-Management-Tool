STATUS_OPEN = "Open"
STATUS_NOT_ATTEMPTED = "Not Attempted"
STATUS_ATTEMPTED = "Attempted"
STATUS_CONTACTED = "Contacted"
STATUS_NEW_OPPORTUNITY = "New Opportunity"
STATUS_CUSTOMER = "Customer"
STATUS_ADDITIONAL_CONTACT = "Additional Contact"
STATUS_DISQUALIFIED = "Disqualified"

LEAD_STATUS_CATEGORIES = (
    (STATUS_OPEN, "black"),
    (STATUS_NOT_ATTEMPTED, "gray"),
    (STATUS_ATTEMPTED, "lightgray"),
    (STATUS_CONTACTED, "yellow"),
    (STATUS_NEW_OPPORTUNITY, "greenyellow"),
    (STATUS_CUSTOMER, "green"),
    (STATUS_ADDITIONAL_CONTACT, "blueviolet"),
    (STATUS_DISQUALIFIED, "red")
)


# predefined lead activity category
ADDED_NEW_LEAD = "Added new lead"
