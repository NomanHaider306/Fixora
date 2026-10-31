from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        PROVIDER = 'provider', 'Service Provider'
        ADMIN = 'admin', 'Administrator'

    email = models.EmailField(unique=True, verbose_name="Email Address")
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name="User Role"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number"
    )

    # Use email or username for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.get_role_display()})" if full_name else self.email

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_provider(self):
        return self.role == self.Role.PROVIDER

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser or self.is_staff


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    city = models.CharField(max_length=100, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer Profile: {self.user.get_full_name() or self.user.email}"
