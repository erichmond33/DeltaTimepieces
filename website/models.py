from typing import Any
from django.db import models
from django.core.files.storage import default_storage
from django.db import transaction

# Create your models here.
class Watch(models.Model):
    name = models.CharField(max_length=500)
    price = models.IntegerField()
    year = models.IntegerField()
    condition = models.TextField(null=True, blank=True)
    contents = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    our_pick = models.BooleanField(default=False)
    date_added_to_our_pick = models.DateTimeField(null=True, blank=True)
    timeless = models.BooleanField(default=False)
    date_added_to_timeless = models.DateTimeField(null=True, blank=True)
    rare_and_iconic = models.BooleanField(default=False)
    date_added_to_rare_and_iconic = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            # Get the old instance
            old_instance = Watch.objects.get(pk=self.pk)
            # Delete the old image
            if old_instance.image and old_instance.image != self.image:
                default_storage.delete(old_instance.image.path)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/watch/{self.pk}'

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Delete secondary images
        for secondary_image in self.secondary_images.all():
            secondary_image.delete()
        
        # Delete the main image
        if self.image:
            default_storage.delete(self.image.path)
        
        super().delete(*args, **kwargs)

class WatchSecondaryImage(models.Model):
    watch = models.ForeignKey(Watch, related_name='secondary_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    def save(self, *args, **kwargs):
        if self.pk:
            # Get the old instance
            old_instance = WatchSecondaryImage.objects.get(pk=self.pk)
            # Delete the old image
            if old_instance.image and old_instance.image != self.image:
                default_storage.delete(old_instance.image.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)