from django.db import models
from django.utils import timezone
import datetime


class User(models.Model):
    public_key = models.CharField(max_length=200)
    created_date = models.DateTimeField('created date', default=datetime.datetime.now())
    active_date = models.DateTimeField('active date', default=datetime.datetime.now())
    status = models.IntegerField('0:normal,1:frozen,2:suspend,3.deleted', default=0)

    def __str__(self):
        return self.public_key


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    created_date = models.DateTimeField('date created', default=datetime.datetime.now())
    expired_date = models.DateTimeField('date expired', null=True)
    verify_code = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.title

    def is_expired(self):
        now = timezone.now()
        return self.expired_date <= now

    class Meta:
        ordering = ('created_date',)
