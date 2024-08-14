from django.db import models
from django.core.files.storage import default_storage

# Create your models here.
class Watch(models.Model):
    name = models.CharField(max_length=500)
    price = models.IntegerField()
    year = models.IntegerField()
    image = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now_add=True)

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