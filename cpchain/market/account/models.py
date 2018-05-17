import os
import binascii
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import datetime


class WalletUser(models.Model):
    """
    The wallet user model.
    """
    public_key = models.CharField(max_length=200, unique=True)
    username = models.CharField(max_length=50, null=True)
    created = models.DateTimeField('created', auto_now_add=True)
    active_date = models.DateTimeField('active date', auto_now_add=True)
    status = models.IntegerField('0:normal,1:frozen,2:suspend,3.deleted', default=0)
    address = models.CharField(max_length=50,null=True)
    avatar = models.CharField(max_length=50,null=True)
    email = models.CharField(max_length=50,null=True)
    gender = models.IntegerField('0:unknown,1:male,2:female', default=0)
    mobile = models.CharField(max_length=50,null=True)
    product_number = models.IntegerField(null=True)

    USERNAME_FIELD = 'public_key'
    REQUIRED_FIELDS = ['public_key']

    class Meta:
        ordering = ('created', 'public_key')

    def __str__(self):
        return self.public_key


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        WalletUser, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("WalletUser")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    public_key = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def is_expired(self):
        now = timezone.now()
        return now + datetime.timedelta(minutes=-30) > self.created

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
