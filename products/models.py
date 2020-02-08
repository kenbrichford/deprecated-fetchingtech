import os

from django.db import models
from django.utils.text import slugify
from django.utils.deconstruct import deconstructible

from mptt.models import MPTTModel, TreeForeignKey

@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '%s.%s' % (instance.slug, ext)
        return os.path.join(self.path, filename)

class Category(MPTTModel):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        upload_to=PathAndRename('categories/'), blank=True, null=True
    )
    parent = TreeForeignKey(
        'self', blank=True, null=True, related_name='children',
        db_index=True, on_delete=models.CASCADE
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if self.parent:
            self.slug = '%s-%s' % (self.parent.slug, slugify(self.name))
        else:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Manufacturer, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=255, unique=True)
    rank = models.PositiveIntegerField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    search = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['manufacturer', 'name']

    def save(self, *args, **kwargs):
        self.slug = '%s-%s' % (
            self.manufacturer.slug, slugify(self.name.replace('+', ' plus'))
        )
        self.search = []
        self.search.extend(self.category.slug.split('-'))
        self.search.extend(self.slug.split('-'))
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.manufacturer.name, self.name)

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    model = models.CharField(max_length=50, blank=True)
    upc = models.CharField(max_length=12, blank=True)
    ean = models.CharField(max_length=13, blank=True)
    msrp = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    image = models.URLField(max_length=255, blank=True, null=True)
    rank = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['product', 'name']
        unique_together = ('product', 'name')

    def save(self, *args, **kwargs):
        if self.rank:
            rank = Variant.objects.filter(
                product=self.product
            ).aggregate(models.Min('rank'))
            self.product.rank = rank['rank__min']
            self.product.save()
        self.slug = slugify(self.name.replace('+', ' plus'))
        super(Variant, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s: %s' % (
            self.product.manufacturer.name, self.product.name, self.name
        )
