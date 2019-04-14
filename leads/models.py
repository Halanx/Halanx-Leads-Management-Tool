from django.db import models
from multiselectfield import MultiSelectField

from common.models import AddressDetail
from common.utils import GenderChoices, HouseAccomodationAllowedCategories, HouseSpaceTypeCategories, \
    HouseSpaceSubTypeCategories, HouseTypeCategories, HouseFurnishTypeCategories, HouseCurrentStayStatusCategories


class LeadSource(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeadTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LeadStatusCategory(models.Model):
    name = models.CharField(max_length=255)
    level = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class LeadActivityCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LeadActivity(models.Model):
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class Lead(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=15, blank=True, null=True, choices=GenderChoices)
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class TenantLead(Lead):
    source = models.ForeignKey('LeadSource', null=True, on_delete=models.SET_NULL,
                               related_name='tenant_leads')
    managed_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='managed_tenant_leads', on_delete=models.SET_NULL)
    created_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='created_tenant_leads', on_delete=models.SET_NULL)
    tags = models.ManyToManyField('LeadTag', related_name='tenant_leads', blank=True)
    status = models.ForeignKey('LeadStatusCategory', null=True, on_delete=models.SET_NULL, related_name='tenant_leads')

    expected_rent_min = models.FloatField(blank=True, null=True)
    expected_rent_max = models.FloatField(blank=True, null=True)
    expected_movein_start = models.DateTimeField(blank=True, null=True)
    expected_movein_end = models.DateTimeField(blank=True, null=True)
    accomodation_for = MultiSelectField(max_length=25, max_choices=3, choices=HouseAccomodationAllowedCategories)
    space_type = models.CharField(max_length=20, choices=HouseSpaceTypeCategories)
    space_subtype = models.CharField(max_length=20, choices=HouseSpaceSubTypeCategories)


class TenantLeadPermanentAddress(AddressDetail):
    lead = models.OneToOneField('TenantLead', on_delete=models.CASCADE, related_name='permanent_address')


class TenantLeadPreferredLocationAddress(AddressDetail):
    lead = models.OneToOneField('TenantLead', on_delete=models.CASCADE, related_name='preferred_location')


class TenantLeadActivity(LeadActivity):
    lead = models.ForeignKey('TenantLead', on_delete=models.CASCADE, related_name='activities')
    handled_by = models.ForeignKey('lead_managers.LeadManager', null=True, on_delete=models.SET_NULL,
                                   related_name='tenant_lead_activities')
    category = models.ForeignKey('LeadActivityCategory', null=True, on_delete=models.SET_NULL,
                                 related_name='tenant_lead_activities')


class HouseOwnerLead(Lead):
    source = models.ForeignKey('LeadSource', blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='house_owner_leads')
    managed_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='managed_house_owner_leads', on_delete=models.SET_NULL)
    created_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='created_house_owner_leads', on_delete=models.SET_NULL)
    tags = models.ManyToManyField('LeadTag', related_name='house_owner_leads', blank=True)
    status = models.ForeignKey('LeadStatusCategory', null=True, on_delete=models.SET_NULL,
                               related_name='house_owner_leads')

    house_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseTypeCategories)
    furnish_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseFurnishTypeCategories)
    accomodation_allowed = MultiSelectField(max_length=25, max_choices=3, choices=HouseAccomodationAllowedCategories)
    current_stay_status = models.CharField(max_length=50, blank=True, null=True,
                                           choices=HouseCurrentStayStatusCategories)
    bhk_count = models.PositiveIntegerField(default=1, blank=True, null=True)
    current_rent = models.FloatField(blank=True, null=True)
    current_security_deposit = models.FloatField(blank=True, null=True)
    expected_rent = models.FloatField(blank=True, null=True)
    expected_security_deposit = models.FloatField(blank=True, null=True)

    shared_rooms_count = models.PositiveIntegerField(default=0)
    total_beds_count = models.PositiveIntegerField(default=0)
    private_rooms_count = models.PositiveIntegerField(default=0)
    flats_count = models.PositiveIntegerField(default=0)


class HouseOwnerLeadPermanentAddress(AddressDetail):
    lead = models.OneToOneField('HouseOwnerLead', on_delete=models.CASCADE, related_name='permanent_address')


class HouseOwnerLeadHouseAddress(AddressDetail):
    lead = models.OneToOneField('HouseOwnerLead', on_delete=models.CASCADE, related_name='house_address')


class HouseOwnerLeadActivity(LeadActivity):
    lead = models.ForeignKey('HouseOwnerLead', on_delete=models.CASCADE, related_name='activities')
    handled_by = models.ForeignKey('lead_managers.LeadManager', null=True, on_delete=models.SET_NULL,
                                   related_name='house_owner_lead_activities')
    category = models.ForeignKey('LeadActivityCategory', null=True, on_delete=models.SET_NULL,
                                 related_name='house_owner_lead_activities')
