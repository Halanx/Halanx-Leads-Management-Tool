from django.conf import settings
from django.db import models

from lead_managers.utils import get_lead_manager_profile_pic_upload_path


class LeadManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    phone_no = models.CharField(max_length=15)
    address = models.CharField(blank=True, null=True, max_length=300)
    profile_pic = models.ImageField(upload_to=get_lead_manager_profile_pic_upload_path, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.user.get_full_name()
