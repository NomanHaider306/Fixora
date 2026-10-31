from django.db import models
from django.conf import settings
from services.models import ServiceCategory


class ProviderProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provider_profile'
    )
    business_name = models.CharField(max_length=150, blank=True, verbose_name="Business / Trade Name")
    introduction = models.TextField(blank=True, verbose_name="Professional Introduction / Bio")
    skills = models.TextField(
        blank=True,
        help_text="List your specific skills (e.g. Circuit wiring, Pipe fitting, Custom cabinets)",
        verbose_name="Skills"
    )
    experience_years = models.PositiveIntegerField(default=1, verbose_name="Years of Experience")
    categories = models.ManyToManyField(
        ServiceCategory,
        related_name='providers',
        blank=True,
        verbose_name="Service Categories"
    )
    service_area = models.CharField(
        max_length=200,
        blank=True,
        help_text="Neighborhoods or regions you cover, e.g. Downtown, North District, 25-mile radius",
        verbose_name="Service Area"
    )
    city = models.CharField(max_length=100, blank=True, default='', verbose_name="City / Location")
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Hourly Rate (PKR)"
    )
    starting_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Starting Price (PKR)"
    )
    profile_picture = models.ImageField(
        upload_to='provider_avatars/',
        blank=True,
        null=True,
        verbose_name="Profile Picture"
    )
    is_verified = models.BooleanField(default=False, verbose_name="Verified Status")
    is_online = models.BooleanField(default=True, verbose_name="Online / Accepting Requests")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, verbose_name="Rating")
    review_count = models.PositiveIntegerField(default=0, verbose_name="Review Count")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider Profile"
        verbose_name_plural = "Provider Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name or self.user.get_full_name() or self.user.email

    @property
    def display_name(self):
        return self.business_name if self.business_name else (self.user.get_full_name() or self.user.username)


class PortfolioImage(models.Model):
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='portfolio_images'
    )
    image = models.ImageField(upload_to='portfolio/', verbose_name="Work Photo")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Caption / Project Description")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Portfolio Image"
        verbose_name_plural = "Portfolio Images"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Portfolio photo for {self.provider.display_name} ({self.caption[:30] if self.caption else 'Untitled'})"


class IdentityDocument(models.Model):
    class DocType(models.TextChoices):
        CNIC = 'CNIC', 'National ID Card'
        PASSPORT = 'PASSPORT', 'Passport'
        LICENSE = 'LICENSE', "Driver's License"
        CERTIFICATION = 'CERTIFICATION', 'Trade / Vocational Certificate'

    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=30, choices=DocType.choices, default=DocType.CNIC)
    document_file = models.FileField(upload_to='id_documents/', verbose_name="Identity Document File")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Additional Notes")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Identity Document"
        verbose_name_plural = "Identity Documents"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.provider.display_name} ({self.get_status_display()})"
