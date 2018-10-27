from django.db import models

class Record(models.Model):
    txhash = models.CharField(max_length=200)
    block = models.IntegerField()
    date = models.DateTimeField()
    frm = models.CharField(max_length=200, null=True, blank=True)
    to = models.CharField(max_length=200, null=True, blank=True)
    value = models.FloatField()
    txfee = models.FloatField()

class Config(models.Model):
    block_at = models.IntegerField()
    trans_cnt = models.IntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()
