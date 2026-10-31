from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from services.models import ServiceCategory

User = get_user_model()


class ServicesSprint2AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin@fixora.com',
            email='admin@fixora.com',
            password='AdminPassword123!',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.customer = User.objects.create_user(
            username='cust@fixora.com',
            email='cust@fixora.com',
            password='Password123!',
            role=User.Role.CUSTOMER
        )
        self.category = ServiceCategory.objects.create(
            name='Electrical Services',
            description='Electrical installations and repairs',
            icon_class='bi-lightning-charge',
            is_active=True
        )

    # US41: Administrator Service Category Management
    def test_admin_category_list_authenticated(self):
        self.client.login(username='admin@fixora.com', password='AdminPassword123!')
        response = self.client.get(reverse('services:category_list_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electrical Services')

    def test_customer_cannot_access_category_management(self):
        self.client.login(username='cust@fixora.com', password='Password123!')
        response = self.client.get(reverse('services:category_list_admin'))
        # Customer redirected
        self.assertEqual(response.status_code, 302)

    def test_admin_create_category(self):
        self.client.login(username='admin@fixora.com', password='AdminPassword123!')
        response = self.client.post(reverse('services:category_create_admin'), {
            'name': 'Plumbing Services',
            'description': 'Pipes, sinks, and drainage solutions',
            'icon_class': 'bi-wrench',
            'is_active': True,
        })
        self.assertRedirects(response, reverse('services:category_list_admin'))
        self.assertTrue(ServiceCategory.objects.filter(name='Plumbing Services').exists())

    def test_admin_update_category(self):
        self.client.login(username='admin@fixora.com', password='AdminPassword123!')
        response = self.client.post(reverse('services:category_update_admin', args=[self.category.pk]), {
            'name': 'Electrical & Wiring Services',
            'description': 'Updated description',
            'icon_class': 'bi-lightning',
            'is_active': True,
        })
        self.assertRedirects(response, reverse('services:category_list_admin'))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Electrical & Wiring Services')

    def test_admin_toggle_category_status(self):
        self.client.login(username='admin@fixora.com', password='AdminPassword123!')
        self.assertTrue(self.category.is_active)
        response = self.client.get(reverse('services:category_toggle_admin', args=[self.category.pk]))
        self.assertRedirects(response, reverse('services:category_list_admin'))
        self.category.refresh_from_db()
        self.assertFalse(self.category.is_active)
