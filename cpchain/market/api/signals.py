from cpchain.market.market.es_client import es_client
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from cpchain.market.api.models import Product
from .serializers import ElasticProductSerializer


@receiver(pre_save, sender=Product, dispatch_uid="update_record")
def update_es_record(sender, instance, **kwargs):
    obj = ElasticProductSerializer(instance)
    obj.save(using=es_client)


@receiver(post_delete, sender=Product, dispatch_uid="delete_record")
def delete_es_record(sender, instance, *args, **kwargs):
    obj = ElasticProductSerializer(instance)
    obj.delete(using=es_client, ignore=404)
