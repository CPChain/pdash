from django.db import models
from django.utils.translation import ugettext_lazy as _


class Comment(models.Model):
    """
    The comment model.
    """
    public_key = models.CharField(_("publicKey"), max_length=200)
    market_hash = models.CharField(_("market hash"), max_length=256,null=False)
    content = models.CharField('comment content', max_length=200)
    rating = models.IntegerField(default=1)
    created = models.DateTimeField('Created', auto_now_add=True)

    def __str__(self):
        return self.public_key
