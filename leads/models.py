from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField

from common.models import AddressDetail
from common.utils import GenderChoices, HouseAccomodationAllowedCategories, HouseSpaceTypeCategories, \
    HouseSpaceSubTypeCategories, HouseTypeCategories, HouseFurnishTypeCategories, HouseCurrentStayStatusCategories
from leads.utils import ADDED_NEW_LEAD, NEW_LEAD


class LeadSourceCategory(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Lead source categories'

    def __str__(self):
        return self.name


class LeadSource(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return self.category.name + f' ({self.name})' if len(self.name) else ''


class LeadTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LeadStatusCategory(models.Model):
    name = models.CharField(max_length=255)
    level = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = 'Lead status categories'

    def __str__(self):
        return self.name


class LeadActivityCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Lead activity categories'

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
    managed_by = models.ManyToManyField('lead_managers.LeadManager', blank=True,
                                        related_name='managed_tenant_leads')
    created_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='created_tenant_leads', on_delete=models.SET_NULL)
    tags = models.ManyToManyField('LeadTag', related_name='tenant_leads', blank=True)
    status = models.ForeignKey('LeadStatusCategory', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='tenant_leads')

    expected_rent_min = models.FloatField(blank=True, null=True)
    expected_rent_max = models.FloatField(blank=True, null=True)
    expected_movein_start = models.DateTimeField(blank=True, null=True)
    expected_movein_end = models.DateTimeField(blank=True, null=True)
    accomodation_for = MultiSelectField(max_length=25, max_choices=3, choices=HouseAccomodationAllowedCategories,
                                        blank=True, null=True)
    space_type = models.CharField(max_length=20, choices=HouseSpaceTypeCategories, blank=True, null=True)
    space_subtype = models.CharField(max_length=20, choices=HouseSpaceSubTypeCategories, blank=True, null=True)

    @property
    def last_activity(self):
        return TenantLeadActivity.objects.select_related('category').filter(lead=self).last()


class TenantLeadSource(LeadSource):
    lead = models.OneToOneField('TenantLead', on_delete=models.CASCADE, related_name='source')
    category = models.ForeignKey('LeadSourceCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                 related_name='tenant_lead_sources')


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

    class Meta:
        verbose_name_plural = 'Tenant lead activities'


class HouseOwnerLead(Lead):
    managed_by = models.ManyToManyField('lead_managers.LeadManager', blank=True,
                                        related_name='managed_house_owner_leads')
    created_by = models.ForeignKey('lead_managers.LeadManager', null=True,
                                   related_name='created_house_owner_leads', on_delete=models.SET_NULL)
    tags = models.ManyToManyField('LeadTag', related_name='house_owner_leads', blank=True)
    status = models.ForeignKey('LeadStatusCategory', blank=True, null=True, on_delete=models.SET_NULL,
                               related_name='house_owner_leads')

    house_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseTypeCategories)
    furnish_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseFurnishTypeCategories)
    accomodation_allowed = MultiSelectField(max_length=25, max_choices=3, blank=True, null=True,
                                            choices=HouseAccomodationAllowedCategories)
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

    @property
    def last_activity(self):
        return HouseOwnerLeadActivity.objects.select_related('category').filter(lead=self).last()


class HouseOwnerLeadSource(LeadSource):
    lead = models.OneToOneField('HouseOwnerLead', on_delete=models.CASCADE, related_name='source')
    category = models.ForeignKey('LeadSourceCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                 related_name='house_owner_lead_sources')


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


# noinspection PyUnusedLocal
@receiver(post_save, sender=TenantLead)
def tenant_lead_post_save_hook(sender, instance, created, **kwargs):
    if created:
        TenantLeadSource(lead=instance).save()
        TenantLeadPermanentAddress(lead=instance).save()
        TenantLeadPreferredLocationAddress(lead=instance).save()
        lead_activity_category, _ = LeadActivityCategory.objects.get_or_create(name=ADDED_NEW_LEAD)
        TenantLeadActivity(lead=instance, handled_by=instance.created_by, category=lead_activity_category).save()
        instance.status, _ = LeadStatusCategory.objects.get_or_create(name=NEW_LEAD, level=0)
        super(TenantLead, instance).save()


# noinspection PyUnusedLocal
@receiver(post_save, sender=HouseOwnerLead)
def house_owner_lead_post_save_hook(sender, instance, created, **kwargs):
    if created:
        HouseOwnerLeadSource(lead=instance).save()
        HouseOwnerLeadPermanentAddress(lead=instance).save()
        HouseOwnerLeadHouseAddress(lead=instance).save()
        lead_activity_category, _ = LeadActivityCategory.objects.get_or_create(name=ADDED_NEW_LEAD)
        HouseOwnerLeadActivity(lead=instance, handled_by=instance.created_by, category=lead_activity_category).save()
        instance.status, _ = LeadStatusCategory.objects.get_or_create(name=NEW_LEAD, level=0)
        super(HouseOwnerLead, instance).save()
