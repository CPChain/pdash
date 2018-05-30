import logging

from django.db import models
from cpchain.market.account.models import WalletUser
from cpchain.market.comment.models import SummaryComment
from cpchain.market.transaction.models import ProductSaleStatus
from .search_indexes import ProductIndex
from elasticsearch.helpers import bulk
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


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
    size = models.IntegerField('file size (byte)', null=True, default=0)
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
        logger.debug("index %r" % self)
        ProductIndex.init()
        obj = ProductIndex(
            meta={'id': self.msg_hash},
            title=self.title,
            description=self.description,
            price=self.price,
            tags=self.tags.split(','),
            start_date=self.start_date,
            end_date=self.end_date,
            market_hash=self.msg_hash,
            file_md5=self.file_md5,
            size=self.size,
            status=self.status,
            created=self.created,
            owner_address=self.owner_address,
            signature=self.signature,
        )
        obj = Product.fill_attr(obj)
        from cpchain.market.market.es_client import es_client
        obj.save(using=es_client)
        return obj.to_dict(include_meta=True)

    def fill_attr(item):
        pk = item.owner_address
        try:
            u = WalletUser.objects.get(public_key=pk)
        except:
            logger.error('user %s not found' % pk)
            u = None

        comment, _ = SummaryComment.objects.get_or_create(market_hash=item.market_hash)
        sale_status, _ = ProductSaleStatus.objects.get_or_create(market_hash=item.market_hash)

        item.username = '' if not u else u.username
        item.avg_rating = 1 if not comment else comment.avg_rating
        item.sales_number = 0 if not sale_status else sale_status.sales_number
        return item

    def update_index_status(self):
        prod = ProductIndex.get(id=self.msg_hash, ignore=404)
        if prod:
            prod.update(status=self.status)

        return True

    def __str__(self):
        return self.owner_address + "," + str(self.seq) + "," + self.msg_hash


    @staticmethod
    def bulk_indexing():
        from cpchain.market.market.es_client import es_client
        ProductIndex.init()
        bulk(client=es_client, actions=(p.indexing() for p in Product.objects.all().iterator()))

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


class SalesQuantity(models.Model):
    """
    The SalesQuantity model.
    """
    market_hash = models.CharField(_("market hash"), max_length=256,null=False)
    quantity = models.IntegerField(default=1)
    created = models.DateTimeField('Created', auto_now_add=True)

    def __str__(self):
        return self.public_key


class MyTag(models.Model):
    """
    The FollowingTag model.
    """
    public_key = models.CharField(max_length=200)
    tag = models.CharField(_("Tag"), max_length=40)


class MySeller(models.Model):
    """
    The FollowingSeller model.
    """
    public_key = models.CharField(max_length=200)
    seller_public_key = models.CharField(max_length=200)
