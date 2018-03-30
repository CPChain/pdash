import datetime

from django.contrib.auth.models import (
    AbstractBaseUser
)
from django.db import models


class WalletUser(models.Model):
    public_key = models.CharField(max_length=200, unique=True)
    created = models.DateTimeField('created', auto_now_add=True)
    active_date = models.DateTimeField('active date', auto_now_add=True)
    status = models.IntegerField('0:normal,1:frozen,2:suspend,3.deleted', default=0)

    USERNAME_FIELD = 'public_key'
    REQUIRED_FIELDS = ['public_key']

    def __str__(self):
        return self.public_key


class Product(models.Model):
    owner = models.ForeignKey(WalletUser, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    created = models.DateTimeField('Created', auto_now_add=True)
    expired_date = models.DateTimeField('date expired', null=True)
    verify_code = models.CharField(max_length=200, null=True)