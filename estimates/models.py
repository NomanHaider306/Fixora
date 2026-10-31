from django.db import models
from django.conf import settings
from providers.models import ProviderProfile
from services.models import ServiceCategory


class EstimateRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RESPONDED = 'responded', 'Responded'
        CANCELLED = 'cancelled', 'Cancelled'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='estimate_requests'
    )
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='received_estimate_requests'
    )
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estimate_requests',
        verbose_name="Service Category"
    )
    title = models.CharField(max_length=200, verbose_name="Job Title / Summary")
    description = models.TextField(verbose_name="Job Description & Details")
    job_address = models.CharField(max_length=255, blank=True, verbose_name="Service Location / Address")
    preferred_date = models.DateField(null=True, blank=True, verbose_name="Preferred Date of Service")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estimate Request"
        verbose_name_plural = "Estimate Requests"
        ordering = ['-created_at']

    def __str__(self):
        return f"Estimate #{self.id}: {self.title} by {self.customer.get_full_name() or self.customer.email}"


class EstimateResponse(models.Model):
    request = models.OneToOneField(
        EstimateRequest,
        on_delete=models.CASCADE,
        related_name='response'
    )
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Estimated Price (PKR)"
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="Estimate Explanation / Cost Breakdown"
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Estimate Valid Until"
    )
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Estimate Response"
        verbose_name_plural = "Estimate Responses"
        ordering = ['-responded_at']

    def __str__(self):
        return f"Estimate Response for Request #{self.request.id} - PKR {self.estimated_price}"
