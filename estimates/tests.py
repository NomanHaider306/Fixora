from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from providers.models import ProviderProfile
from services.models import ServiceCategory
from estimates.models import EstimateRequest, EstimateResponse

User = get_user_model()


class EstimatesSprint4Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(name='Carpentry', slug='carpentry')

        # Customer
        self.customer = User.objects.create_user(
            username='cust_est@fixora.com',
            email='cust_est@fixora.com',
            password='Password123!',
            role=User.Role.CUSTOMER
        )

        # Provider
        self.pro_user = User.objects.create_user(
            username='pro_est@fixora.com',
            email='pro_est@fixora.com',
            password='Password123!',
            role=User.Role.PROVIDER
        )
        self.provider = ProviderProfile.objects.create(
            user=self.pro_user,
            business_name='Solid Oak Carpentry',
            city='Lahore'
        )
        self.provider.categories.add(self.category)

    # US24: Customer Preliminary Price Estimates
    def test_customer_submits_estimate_request(self):
        self.client.login(username='cust_est@fixora.com', password='Password123!')
        target_date = date.today() + timedelta(days=5)

        response = self.client.post(reverse('estimates:request_create', args=[self.provider.pk]), {
            'title': 'Build Bookshelf',
            'service_category': self.category.pk,
            'description': 'Need a custom 6-foot oak bookshelf built in living room.',
            'job_address': 'House 14, Block C, Gulberg 3, Lahore',
            'preferred_date': target_date.strftime('%Y-%m-%d')
        })
        self.assertRedirects(response, reverse('estimates:customer_list'))

        self.assertEqual(EstimateRequest.objects.count(), 1)
        est = EstimateRequest.objects.first()
        self.assertEqual(est.title, 'Build Bookshelf')
        self.assertEqual(est.status, EstimateRequest.Status.PENDING)
        self.assertEqual(est.customer, self.customer)
        self.assertEqual(est.provider, self.provider)

    def test_provider_responds_to_estimate(self):
        # Create pending request
        est = EstimateRequest.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_category=self.category,
            title='Kitchen Island Framing',
            description='Framing only, lumber on site.',
            status=EstimateRequest.Status.PENDING
        )

        self.client.login(username='pro_est@fixora.com', password='Password123!')
        valid_date = date.today() + timedelta(days=15)

        response = self.client.post(reverse('estimates:respond', args=[est.pk]), {
            'estimated_price': '4500.00',
            'explanation': 'Estimated 5 hours of work at PKR 900/hr.',
            'valid_until': valid_date.strftime('%Y-%m-%d')
        })
        self.assertRedirects(response, reverse('estimates:detail', args=[est.pk]))

        est.refresh_from_db()
        self.assertEqual(est.status, EstimateRequest.Status.RESPONDED)
        self.assertTrue(hasattr(est, 'response'))
        self.assertEqual(est.response.estimated_price, 4500.00)

    def test_customer_cancels_pending_estimate(self):
        est = EstimateRequest.objects.create(
            customer=self.customer,
            provider=self.provider,
            service_category=self.category,
            title='Window Repair',
            description='Sash cord broken.',
            status=EstimateRequest.Status.PENDING
        )

        self.client.login(username='cust_est@fixora.com', password='Password123!')
        response = self.client.post(reverse('estimates:request_cancel', args=[est.pk]))
        self.assertRedirects(response, reverse('estimates:customer_list'))

        est.refresh_from_db()
        self.assertEqual(est.status, EstimateRequest.Status.CANCELLED)

    def test_unauthorized_user_cannot_view_estimate(self):
        other_user = User.objects.create_user(
            username='stranger@fixora.com',
            email='stranger@fixora.com',
            password='Password123!',
            role=User.Role.CUSTOMER
        )
        est = EstimateRequest.objects.create(
            customer=self.customer,
            provider=self.provider,
            title='Private Job',
            description='Secret repair'
        )

        self.client.login(username='stranger@fixora.com', password='Password123!')
        response = self.client.get(reverse('estimates:detail', args=[est.pk]))
        self.assertEqual(response.status_code, 302)
