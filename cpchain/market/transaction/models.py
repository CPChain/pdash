from django.db import models
from django.utils.translation import ugettext_lazy as _


class TransactionDetail(models.Model):
    """
    The ProductTransaction model.We can know who has buy which product.
    read Transaction info from chain,write into db
    """
    seller_address = models.CharField(_("seller_address"), max_length=200, null=True)
    market_hash = models.CharField(_("market hash"), max_length=256,null=True)
    buyer_address = models.CharField(_("buyer_address"), max_length=200, null=True)
    created = models.DateTimeField('Created', auto_now_add=True)

    def __str__(self):
        return self.public_key


class ProductSaleStatus(models.Model):
    """
    The ProductSaleStatus model.
    read sales_number from chain,write into db
    """
    market_hash = models.CharField("market hash", max_length=256,null=False)
    sales_number = models.IntegerField("Sales number", default=0)
    updated = models.DateTimeField('Updated', auto_now=True)

    def __str__(self):
        return self.market_hash
