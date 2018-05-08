from django.db import models

# Create your models here.
from cpchain.market.account.models import WalletUser
from .search_indexes import ProductIndex
from django.utils.translation import ugettext_lazy as _


class Product(models.Model):
    """
    The product model.
    """
    owner = models.ForeignKey(WalletUser, on_delete=models.CASCADE)
    owner_address = models.CharField(max_length=200)
    title = models.CharField(max_length=100)
    description = models.TextField()
    tags = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    created = models.DateTimeField('Created', auto_now_add=True)
    start_date = models.DateTimeField('Start time', null=True)
    end_date = models.DateTimeField('End time', null=True)
    status = models.IntegerField('0:normal,1:frozen', default=0)
    seq = models.IntegerField('Sequence increase')
    file_md5 = models.CharField(max_length=32, null=True)
    # verify wallet hash(title,description,expired_date,price,tags)
    signature = models.CharField('Signature created by client', max_length=200, null=True)
    msg_hash = models.CharField('Msg hash(owner_address,title,description,price,created,expired)'
                                , max_length=256, null=True)

    def get_signature_source(self):
        ss = self.owner_address + self.title + str(self.description[0]) + str(self.price[0]) \
             + self.start_date + self.end_date + str(self.file_md5)
        return ss

    def get_msg_hash_source(self):
        return self.get_signature_source() + str(self.seq) + self.signature

    def indexing(self):
        ProductIndex.init()
        obj = ProductIndex(
            meta={'id': self.msg_hash},
            title=self.title,
            description=self.description,
            price=self.price,
            tags=self.tags,
            start_date=self.start_date,
            end_date=self.end_date,
            market_hash=self.msg_hash,
            file_md5=self.file_md5,
            status=self.status,
            created=self.created,
            owner_address=self.owner_address,
            signature=self.signature,
        )
        from cpchain.market.market.es_client import es_client
        obj.save(using=es_client)
        return obj.to_dict(include_meta=True)


class WalletMsgSequence(models.Model):
    """
    The wallet message sequence model.
    """
    public_key = models.CharField(_("PublicKey"), max_length=200, primary_key=True)
    user = models.OneToOneField(
        WalletUser, related_name='wallet_msg_sequence',
        on_delete=models.CASCADE, verbose_name=_("WalletUser")
    )
    seq = models.IntegerField(_("seq"), default=0)

    class Meta:
        verbose_name = _("WalletUserSequence")
        verbose_name_plural = _("WalletUserSequences")

    def save(self, *args, **kwargs):
        return super(WalletMsgSequence, self).save(*args, **kwargs)

    def __str__(self):
        return self.public_key
