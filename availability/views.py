from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date, timedelta, time
from .models import WeeklySchedule, BlockedDate
from .forms import BlockedDateForm
from providers.models import ProviderProfile


@login_required
def weekly_schedule_manage(request):
    """
    US15 - Weekly Working Hours
    Manage start/end hours and working days for all 7 days of the week.
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Access restricted to service providers.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)

    # Ensure all 7 days exist for provider
    for day_code, day_name in WeeklySchedule.DAYS_OF_WEEK:
        WeeklySchedule.objects.get_or_create(
            provider=profile,
            day_of_week=day_code,
            defaults={
                'is_working': day_code < 5,  # Mon-Fri default working
                'start_time': time(9, 0),
                'end_time': time(17, 0)
            }
        )

    schedules = profile.weekly_schedules.all().order_by('day_of_week')

    if request.method == 'POST':
        errors = []
        for sched in schedules:
            day_prefix = f"day_{sched.day_of_week}_"
            is_working = request.POST.get(f"{day_prefix}working") == 'on'
            start_str = request.POST.get(f"{day_prefix}start")
            end_str = request.POST.get(f"{day_prefix}end")

            sched.is_working = is_working
            if is_working:
                try:
                    if start_str and end_str:
                        start_t = datetime.strptime(start_str, '%H:%M').time()
                        end_t = datetime.strptime(end_str, '%H:%M').time()
                        if start_t >= end_t:
                            errors.append(f"{sched.get_day_of_week_display()}: Start time must be earlier than end time.")
                        else:
                            sched.start_time = start_t
                            sched.end_time = end_t
                    else:
                        errors.append(f"{sched.get_day_of_week_display()}: Please provide both start and end times.")
                except ValueError:
                    errors.append(f"{sched.get_day_of_week_display()}: Invalid time format.")

            if not errors:
                sched.save()

        if errors:
            for err in errors:
                messages.error(request, err)
        else:
            messages.success(request, "Your weekly working schedule has been saved successfully!")
            return redirect('availability:weekly_schedule_manage')

    return render(request, 'availability/weekly_schedule.html', {
        'profile': profile,
        'schedules': schedules,
    })


@login_required
def blocked_dates_manage(request):
    """
    US16 - Block specific dates
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Access restricted to service providers.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    blocked_dates = profile.blocked_dates.filter(date__gte=date.today()).order_by('date')

    if request.method == 'POST':
        form = BlockedDateForm(request.POST)
        if form.is_valid():
            blocked = form.save(commit=False)
            blocked.provider = profile
            # Check duplicate
            if BlockedDate.objects.filter(provider=profile, date=blocked.date).exists():
                messages.warning(request, f"Date {blocked.date} is already blocked.")
            else:
                blocked.save()
                messages.success(request, f"Date {blocked.date} has been blocked successfully.")
                return redirect('availability:blocked_dates_manage')
        else:
            messages.error(request, "Please check the date provided.")
    else:
        form = BlockedDateForm()

    return render(request, 'availability/blocked_dates.html', {
        'profile': profile,
        'blocked_dates': blocked_dates,
        'form': form,
    })


@login_required
def blocked_date_delete(request, pk):
    """
    US16 - Unblock a date
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Unauthorized.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    blocked = get_object_or_404(BlockedDate, pk=pk, provider=profile)
    if request.method == 'POST':
        date_str = blocked.date
        blocked.delete()
        messages.success(request, f"Date {date_str} unblocked.")
    return redirect('availability:blocked_dates_manage')


@login_required
def toggle_online_status(request):
    """
    US16 - Toggle Online / Offline Status
    """
    if not request.user.is_provider and not request.user.is_administrator:
        messages.error(request, "Unauthorized.")
        return redirect('accounts:dashboard_redirect')

    profile = get_object_or_404(ProviderProfile, user=request.user)
    profile.is_online = not profile.is_online
    profile.save()

    status_label = "Online (Accepting Requests)" if profile.is_online else "Offline (Not Accepting Requests)"
    messages.success(request, f"Your status is now {status_label}.")
    return redirect(request.META.get('HTTP_REFERER') or 'accounts:provider_dashboard')


def get_available_slots(request, provider_id):
    """
    US17 - Calculate available time slots for a given provider and date.
    Returns JSON response.
    """
    provider = get_object_or_404(ProviderProfile, pk=provider_id)
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'status': 'error', 'message': 'Date parameter is required (YYYY-MM-DD).'}, status=400)

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid date format.'}, status=400)

    # Check 1: Provider online/offline status
    if not provider.is_online:
        return JsonResponse({
            'status': 'offline',
            'available': False,
            'message': 'This service provider is currently offline and not accepting bookings.',
            'slots': []
        })

    # Check 2: Blocked dates
    if provider.blocked_dates.filter(date=selected_date).exists():
        blocked_entry = provider.blocked_dates.get(date=selected_date)
        reason_text = f" ({blocked_entry.reason})" if blocked_entry.reason else ""
        return JsonResponse({
            'status': 'blocked',
            'available': False,
            'message': f'Provider has marked this date as unavailable{reason_text}.',
            'slots': []
        })

    # Check 3: Weekly working hours
    # Python weekday(): Monday is 0, Sunday is 6
    day_of_week = selected_date.weekday()
    try:
        schedule = provider.weekly_schedules.get(day_of_week=day_of_week)
    except WeeklySchedule.DoesNotExist:
        schedule = None

    if not schedule or not schedule.is_working:
        day_name = selected_date.strftime('%A')
        return JsonResponse({
            'status': 'not_working_day',
            'available': False,
            'message': f'Provider does not work on {day_name}s.',
            'slots': []
        })

    # Calculate 1-hour slots
    slots = []
    current_dt = datetime.combine(selected_date, schedule.start_time)
    end_dt = datetime.combine(selected_date, schedule.end_time)

    while current_dt + timedelta(hours=1) <= end_dt:
        slot_start = current_dt.strftime('%I:%M %p')
        slot_end = (current_dt + timedelta(hours=1)).strftime('%I:%M %p')
        slots.append({
            'start': slot_start,
            'end': slot_end,
            'display': f"{slot_start} - {slot_end}"
        })
        current_dt += timedelta(hours=1)

    return JsonResponse({
        'status': 'available',
        'available': True,
        'date': selected_date.strftime('%Y-%m-%d'),
        'day_name': selected_date.strftime('%A'),
        'working_hours': f"{schedule.start_time.strftime('%I:%M %p')} - {schedule.end_time.strftime('%I:%M %p')}",
        'slots': slots,
        'message': f"{len(slots)} available time slots found." if slots else "No full hour slots available."
    })


def provider_calendar_view(request, provider_id):
    """
    US17 - Dedicated Interactive Availability View for Customers.
    """
    provider = get_object_or_404(
        ProviderProfile.objects.select_related('user').prefetch_related('weekly_schedules'),
        pk=provider_id
    )

    schedules = provider.weekly_schedules.all().order_by('day_of_week')
    schedule_map = {s.day_of_week: s for s in schedules}
    days_data = []
    for day_idx, day_name in WeeklySchedule.DAYS_OF_WEEK:
        sched = schedule_map.get(day_idx)
        days_data.append({
            'day_name': day_name,
            'is_working': sched.is_working if sched else False,
            'start_time': sched.start_time.strftime('%I:%M %p') if sched and sched.is_working else None,
            'end_time': sched.end_time.strftime('%I:%M %p') if sched and sched.is_working else None,
        })

    blocked_dates = list(provider.blocked_dates.filter(date__gte=date.today()).values_list('date', flat=True))
    blocked_dates_json = [d.strftime('%Y-%m-%d') for d in blocked_dates]

    context = {
        'provider': provider,
        'days_data': days_data,
        'blocked_dates_json': blocked_dates_json,
        'today': date.today(),
        'min_date': date.today().strftime('%Y-%m-%d'),
        'max_date': (date.today() + timedelta(days=60)).strftime('%Y-%m-%d'),
    }
    return render(request, 'availability/calendar.html', context)
