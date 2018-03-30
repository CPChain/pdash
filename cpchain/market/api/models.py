import datetime

from django.contrib.auth.models import (
    AbstractBaseUser
)
from django.db import models
from django.utils import timezone


class WalletUser(models.Model):
    public_key = models.CharField(max_length=200, unique=True)
    created_date = models.DateTimeField('created date', default=timezone.now())
    active_date = models.DateTimeField('active date', default=timezone.now())
    status = models.IntegerField('0:normal,1:frozen,2:suspend,3.deleted', default=0)

    def __str__(self):
        return self.public_key


class Product(models.Model):
    owner = models.ForeignKey(WalletUser, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    created_date = models.DateTimeField('date created', default=timezone.now())
    expired_date = models.DateTimeField('date expired', null=True)
    verify_code = models.CharField(max_length=200, null=True)