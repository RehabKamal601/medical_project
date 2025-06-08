from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    phone = models.CharField(max_length=15, null=True, blank=True)
