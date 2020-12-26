from django.db import models
from django.contrib.auth.models import AbstractUser


class SmsAuthAbstractUser(AbstractUser):
    short_code = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=22, blank=False, null=True)

    class Meta:
        abstract = True

