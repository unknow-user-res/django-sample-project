from django.db import models
from django.conf import settings
from .get_username import get_request

# Create your models here.


class OwnerManager(models.Manager):
    def get_queryset(self):
        request = get_request()
        if request:
            return super().get_queryset().filter(owner=request.user)
        return super().get_queryset()


class CreationModificationDateModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_modified_by",
    )

    objects = models.Manager()
    owner_objects = OwnerManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Update created_by, modified_by
        """
        request = get_request()
        if request:
            user = request.user
            if self.pk is None:
                self.created_by = user
            self.modified_by = user
        super().save(*args, **kwargs)
