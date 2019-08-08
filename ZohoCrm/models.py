from django.db import models


# Create your models here.
class ZohoConstant(models.Model):
    name = models.CharField(max_length=200, unique=True)
    value = models.CharField(max_length=200)
