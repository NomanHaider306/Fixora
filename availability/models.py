from django.db import models
from providers.models import ProviderProfile
from django.core.exceptions import ValidationError


class WeeklySchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='weekly_schedules'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name="Day of the Week")
    is_working = models.BooleanField(default=True, verbose_name="Available for Work")
    start_time = models.TimeField(default="09:00:00", verbose_name="Start Time")
    end_time = models.TimeField(default="17:00:00", verbose_name="End Time")

    class Meta:
        verbose_name = "Weekly Schedule"
        verbose_name_plural = "Weekly Schedules"
        unique_together = ('provider', 'day_of_week')
        ordering = ['day_of_week']

    def clean(self):
        if self.is_working and self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Start time must be earlier than end time.")

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK).get(self.day_of_week, f"Day {self.day_of_week}")
        if self.is_working:
            return f"{self.provider.display_name}: {day_name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
        return f"{self.provider.display_name}: {day_name} (Unavailable)"


class BlockedDate(models.Model):
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name='blocked_dates'
    )
    date = models.DateField(verbose_name="Blocked Date")
    reason = models.CharField(max_length=200, blank=True, verbose_name="Reason for Absence")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blocked Date"
        verbose_name_plural = "Blocked Dates"
        unique_together = ('provider', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.provider.display_name} - Blocked: {self.date} ({self.reason or 'No reason specified'})"
