from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from multiselectfield import MultiSelectField

from common.models import AddressDetail
from common.utils import GenderChoices, HouseAccomodationAllowedCategories, HouseSpaceTypeCategories, \
    HouseSpaceSubTypeCategories, HouseTypeCategories, HouseFurnishTypeCategories, HouseCurrentStayStatusCategories
from leads.utils import STATUS_NOT_ATTEMPTED, ADDED_NEW_LEAD, STATUS_OPEN, AFFILIATE


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
        try:
            return self.category.name + f' ({self.name})' if len(self.name) else ''
        except:
            return str(self.id)


class LeadTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class LeadStatusCategory(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Lead status categories'

    def __str__(self):
        return self.name

    def get_color_display(self):
        return format_html(
            '<span style="background-color: {0}; color: white;">&nbsp;{0}&nbsp;</span>'.format(self.color))

    get_color_display.short_description = 'Color'
    get_color_display.allow_tags = True


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
    is_deleted = models.BooleanField(default=False)

    acknowledged_by_affiliate = models.BooleanField(default=False)

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
    description = models.TextField(null=True, blank=True)

    zoho_id = models.BigIntegerField(null=True, blank=True, unique=True)

    # It is TenantReferral id in case of TenantLead and OwnerReferral id in case of Owner Lead
    referral_id = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.name)


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
        return TenantLeadActivity.objects.select_related('category').filter(lead=self, is_deleted=False).last()


class TenantLeadSource(LeadSource):
    lead = models.OneToOneField('TenantLead', on_delete=models.CASCADE, related_name='source')
    category = models.ForeignKey('LeadSourceCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                 related_name='tenant_lead_sources')

    def __str__(self):
        if not self.name:
            try:
                return str(self.category.name)
            except:
                return str(self.id)

        else:
            return super(TenantLeadSource, self).__str__()


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
    pre_status = models.ForeignKey('LeadStatusCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='pre_status_tenant_lead_activities')
    post_status = models.ForeignKey('LeadStatusCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='post_status_tenant_lead_activities')

    class Meta:
        verbose_name_plural = 'Tenant lead activities'

    def save(self, *args, **kwargs):
        if not self.pk and not self.pre_status:
            self.pre_status = self.lead.status
        super(TenantLeadActivity, self).save(*args, **kwargs)


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
        return HouseOwnerLeadActivity.objects.select_related('category').filter(lead=self, is_deleted=False).last()


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
    pre_status = models.ForeignKey('LeadStatusCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name='pre_status_house_owner_lead_activities')
    post_status = models.ForeignKey('LeadStatusCategory', blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name='post_status_house_owner_lead_activities')

    def save(self, *args, **kwargs):
        if not self.pk and not self.pre_status:
            self.pre_status = self.lead.status
        super(HouseOwnerLeadActivity, self).save(*args, **kwargs)


# noinspection PyUnusedLocal
@receiver(post_save, sender=TenantLead)
def tenant_lead_post_save_hook(sender, instance, created, **kwargs):
    if created:
        TenantLeadSource(lead=instance).save()
        TenantLeadPermanentAddress(lead=instance).save()
        TenantLeadPreferredLocationAddress(lead=instance).save()
        lead_activity_category, _ = LeadActivityCategory.objects.get_or_create(name=ADDED_NEW_LEAD)
        pre_status = LeadStatusCategory.objects.get(name=STATUS_OPEN)
        post_status = LeadStatusCategory.objects.get(name=STATUS_NOT_ATTEMPTED)
        TenantLeadActivity(lead=instance, handled_by=instance.created_by, category=lead_activity_category,
                           pre_status=pre_status, post_status=post_status).save()

        # Create Zoho Lead
        from ZohoCrm.api.views import create_zoho_lead_from_tenant_lead_data
        super(TenantLead, instance).save()
        create_zoho_lead_from_tenant_lead_data(instance)


# noinspection PyUnusedLocal
@receiver(post_save, sender=HouseOwnerLead)
def house_owner_lead_post_save_hook(sender, instance, created, **kwargs):
    if created:
        HouseOwnerLeadSource(lead=instance).save()
        HouseOwnerLeadPermanentAddress(lead=instance).save()
        HouseOwnerLeadHouseAddress(lead=instance).save()
        lead_activity_category, _ = LeadActivityCategory.objects.get_or_create(name=ADDED_NEW_LEAD)
        pre_status = LeadStatusCategory.objects.get(name=STATUS_OPEN)
        post_status = LeadStatusCategory.objects.get(name=STATUS_NOT_ATTEMPTED)
        HouseOwnerLeadActivity(lead=instance, handled_by=instance.created_by, category=lead_activity_category,
                               pre_status=pre_status, post_status=post_status).save()
        super(HouseOwnerLead, instance).save()


# noinspection PyUnusedLocal
@receiver(post_save, sender=TenantLeadActivity)
def tenant_lead_activity_post_save_hook(sender, instance, created, **kwargs):
    from affiliate_lead.tasks.sending_tasks import update_tenant_lead_activity_status_in_affiliate_tool

    latest_lead_activity = instance.lead.activities.filter(is_deleted=False).last()
    if latest_lead_activity and latest_lead_activity.post_status:
        instance.lead.status = latest_lead_activity.post_status
        instance.lead.save()

    if created:
        if instance.lead.source == TenantLeadSource.objects.filter(name=AFFILIATE).first():
            try:
                update_tenant_lead_activity_status_in_affiliate_tool(instance)
            except Exception as E:
                print("error in updating lead activity status due to ", str(E))


# noinspection PyUnusedLocal
@receiver(post_save, sender=HouseOwnerLeadActivity)
def house_owner_lead_activity_post_save_hook(sender, instance, created, **kwargs):
    latest_lead_activity = instance.lead.activities.filter(is_deleted=False).last()
    if latest_lead_activity and latest_lead_activity.post_status:
        instance.lead.status = latest_lead_activity.post_status
        instance.lead.save()

    if created:
        if instance.lead.source == HouseOwnerLeadSource.objects.filter(name=AFFILIATE).first():
            try:
                print("updating lead activity status ")
                from affiliate_lead.tasks.sending_tasks import update_owner_lead_activity_status_in_affiliate_tool
                update_owner_lead_activity_status_in_affiliate_tool(instance)
            except Exception as E:
                print("error in updating lead activity status due to ", str(E))
