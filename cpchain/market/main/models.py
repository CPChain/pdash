from django.db import models

STATUS_CHOICES = ((1, 'Enable'), (0, 'Disable'))

class Carousel(models.Model):

    """
    The Carousel model.
    """
    name = models.CharField("name", max_length=50)
    image = models.CharField("image url", max_length=256)
    link = models.CharField("link address", max_length=256)
    index = models.IntegerField("sort by index", default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return self.name


class HotTag(models.Model):
    """
    The HotTag model.
    """
    image = models.CharField("image url", max_length=256)
    tag = models.CharField("tag", max_length=256)
    index = models.IntegerField("sort by index", default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return self.name


class Promotion(models.Model):

    """
    The Promotion model
    """
    name = models.CharField("name", max_length=50)
    image = models.CharField("image url", max_length=256)
    link = models.CharField("link address", max_length=256)
    index = models.IntegerField("sort by index", default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def __str__(self):
        return self.name
