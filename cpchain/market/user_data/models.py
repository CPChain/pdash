from django.db import models
from django.utils.translation import ugettext_lazy as _


class UploadFileInfo(models.Model):
    """
    The UploadFileInfo model.
    """
    public_key = models.CharField(_('publicKey'), max_length=200)

    client_id = models.IntegerField('client id',default=0)
    name = models.CharField('name', max_length=256, null=True)
    hashcode = models.CharField('hashcode', max_length=200, null=True)
    path = models.CharField('path', max_length=1024, null=True)
    size = models.IntegerField('size',default=0)
    remote_type = models.CharField('remote_type', max_length=32, null=True)
    remote_uri = models.CharField('remote_uri', max_length=1024, null=True)
    is_published = models.BooleanField('True:published,False:unpublished')
    aes_key = models.CharField('aes_key', max_length=1024, null=True)
    market_hash = models.CharField('market_hash', max_length=256, null=True)
    created = models.DateTimeField('Created', auto_now_add=True)


class BuyerFileInfo(models.Model):
    """
    The BuyerFileInfo model.
    """
    public_key = models.CharField(_('publicKey'), max_length=200)
    order_id = models.IntegerField('generate by chain', null=True)
    market_hash = models.CharField('market_hash',max_length=256)
    file_uuid = models.CharField('file_uuid', max_length=32)
    file_title = models.CharField('file_title', max_length=256)
    path = models.CharField('path', max_length=256)
    size = models.IntegerField('size(byte)', null=False)
    is_downloaded = models.BooleanField('True:downloaded,False:not downloaded')
    created = models.DateTimeField('Created', auto_now_add=True)

    def __str__(self):
        return self.public_key


class UserInfoVersion(models.Model):
    """
    The user info version model.
    """
    public_key = models.CharField(_("publicKey"), max_length=200, primary_key=True)
    version = models.IntegerField(_("version"), default=0)

    def __str__(self):
        return self.public_key


class ProductTag(models.Model):
    """
    The Product Tag model.
    """
    tag = models.CharField(_("tag"), max_length=20)

    def __str__(self):
        return self.tag


class Bookmark(models.Model):
    """
    The user bookmark model.
    """
    public_key = models.CharField(_("publicKey"), max_length=200)
    market_hash = models.CharField(_("market hash"), max_length=256,null=False)
    name = models.CharField('name', max_length=50)
    created = models.DateTimeField('Created', auto_now_add=True)

    def __str__(self):
        return self.public_key
