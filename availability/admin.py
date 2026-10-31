from django.contrib import admin
from .models import WeeklySchedule, BlockedDate


@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('provider', 'day_of_week', 'is_working', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'is_working')
    search_fields = ('provider__business_name',)


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('provider', 'date', 'reason', 'created_at')
    list_filter = ('date',)
    search_fields = ('provider__business_name', 'reason')
