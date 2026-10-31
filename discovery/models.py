from django.db import models
from django.conf import settings
from providers.models import ProviderProfile


class Favourite(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favourite_providers'
    )
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='favourited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favourite"
        verbose_name_plural = "Favourites"
        unique_together = ('customer', 'provider')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.email} -> {self.provider.display_name}"
