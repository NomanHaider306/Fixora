from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta, time
from providers.models import ProviderProfile
from availability.models import WeeklySchedule, BlockedDate

User = get_user_model()


class AvailabilitySprint4Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='pro_avail@fixora.com',
            email='pro_avail@fixora.com',
            password='Password123!',
            role=User.Role.PROVIDER
        )
        self.profile = ProviderProfile.objects.create(
            user=self.user,
            business_name='Reliable Electric',
            is_online=True
        )

        # Set up a working schedule for Mondays (day 0) 09:00 - 12:00 (3 hours = 3 slots)
        WeeklySchedule.objects.create(
            provider=self.profile,
            day_of_week=0,  # Monday
            is_working=True,
            start_time=time(9, 0),
            end_time=time(12, 0)
        )
        # Tuesday (day 1) - Not working
        WeeklySchedule.objects.create(
            provider=self.profile,
            day_of_week=1,
            is_working=False,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

    # US15: Weekly Working Hours
    def test_weekly_schedule_view_and_save(self):
        self.client.login(username='pro_avail@fixora.com', password='Password123!')
        response = self.client.get(reverse('availability:weekly_schedule_manage'))
        self.assertEqual(response.status_code, 200)

        # Save schedule for Wednesday (day 2)
        post_data = {
            'day_0_working': 'on',
            'day_0_start': '08:00',
            'day_0_end': '16:00',
        }
        res_post = self.client.post(reverse('availability:weekly_schedule_manage'), post_data)
        self.assertRedirects(res_post, reverse('availability:weekly_schedule_manage'))
        mon_sched = WeeklySchedule.objects.get(provider=self.profile, day_of_week=0)
        self.assertEqual(mon_sched.start_time, time(8, 0))
        self.assertEqual(mon_sched.end_time, time(16, 0))

    # US16: Block Dates & Online/Offline Status
    def test_block_date_and_delete(self):
        self.client.login(username='pro_avail@fixora.com', password='Password123!')
        target_date = date.today() + timedelta(days=10)
        response = self.client.post(reverse('availability:blocked_dates_manage'), {
            'date': target_date.strftime('%Y-%m-%d'),
            'reason': 'Personal Leave'
        })
        self.assertRedirects(response, reverse('availability:blocked_dates_manage'))
        self.assertTrue(BlockedDate.objects.filter(provider=self.profile, date=target_date).exists())

        # Unblock
        entry = BlockedDate.objects.get(provider=self.profile, date=target_date)
        del_resp = self.client.post(reverse('availability:blocked_date_delete', args=[entry.pk]))
        self.assertRedirects(del_resp, reverse('availability:blocked_dates_manage'))
        self.assertFalse(BlockedDate.objects.filter(provider=self.profile, date=target_date).exists())

    def test_toggle_online_status(self):
        self.client.login(username='pro_avail@fixora.com', password='Password123!')
        self.assertTrue(self.profile.is_online)
        self.client.post(reverse('availability:toggle_online_status'))
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_online)

    # US17: Dynamic Availability Slots Calculation
    def test_slots_on_working_day(self):
        # Find next Monday
        days_ahead = (0 - date.today().weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_monday = date.today() + timedelta(days=days_ahead)

        url = reverse('availability:get_available_slots', args=[self.profile.pk]) + f"?date={next_monday.strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['available'])
        # 09:00 - 12:00 yields 3 one-hour slots
        self.assertEqual(len(data['slots']), 3)

    def test_slots_on_non_working_day(self):
        # Next Tuesday
        days_ahead = (1 - date.today().weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_tuesday = date.today() + timedelta(days=days_ahead)

        url = reverse('availability:get_available_slots', args=[self.profile.pk]) + f"?date={next_tuesday.strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data['available'])
        self.assertEqual(data['status'], 'not_working_day')

    def test_slots_on_blocked_date(self):
        days_ahead = (0 - date.today().weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_monday = date.today() + timedelta(days=days_ahead)

        # Block this Monday
        BlockedDate.objects.create(provider=self.profile, date=next_monday, reason='Sick')

        url = reverse('availability:get_available_slots', args=[self.profile.pk]) + f"?date={next_monday.strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data['available'])
        self.assertEqual(data['status'], 'blocked')

    def test_slots_when_provider_is_offline(self):
        self.profile.is_online = False
        self.profile.save()

        next_date = date.today() + timedelta(days=1)
        url = reverse('availability:get_available_slots', args=[self.profile.pk]) + f"?date={next_date.strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data['available'])
        self.assertEqual(data['status'], 'offline')
