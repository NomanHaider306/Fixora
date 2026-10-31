from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from providers.models import ProviderProfile
from services.models import ServiceCategory
from discovery.models import Favourite

User = get_user_model()


class DiscoverySprint3Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_elec = ServiceCategory.objects.create(name='Electrical', slug='electrical', icon_class='bi-lightning')
        self.cat_plumb = ServiceCategory.objects.create(name='Plumbing', slug='plumbing', icon_class='bi-wrench')

        # Provider 1: Lahore Electrician
        user1 = User.objects.create_user(username='p1@fixora.com', email='p1@fixora.com', password='Password123!', role=User.Role.PROVIDER)
        self.p1 = ProviderProfile.objects.create(
            user=user1,
            business_name='Lahore Volt Pro',
            city='Lahore',
            service_area='DHA & Gulberg',
            skills='Wiring, Breakers',
            hourly_rate=1500.00,
            starting_price=2000.00,
            rating=4.90,
            is_online=True
        )
        self.p1.categories.add(self.cat_elec)

        # Provider 2: Karachi Plumber
        user2 = User.objects.create_user(username='p2@fixora.com', email='p2@fixora.com', password='Password123!', role=User.Role.PROVIDER)
        self.p2 = ProviderProfile.objects.create(
            user=user2,
            business_name='Karachi Master Plumbers',
            city='Karachi',
            service_area='Clifton & DHA',
            skills='Pipes, Leaks',
            hourly_rate=1000.00,
            starting_price=1500.00,
            rating=4.20,
            is_online=False
        )
        self.p2.categories.add(self.cat_plumb)

        # Customer
        self.customer = User.objects.create_user(username='cust@fixora.com', email='cust@fixora.com', password='Password123!', role=User.Role.CUSTOMER)

    # US11: Browse Services by Category
    def test_explore_services_page(self):
        response = self.client.get(reverse('discovery:explore'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electrical')
        self.assertContains(response, 'Plumbing')

    def test_category_providers_view(self):
        response = self.client.get(reverse('discovery:category_providers', args=[self.cat_elec.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lahore Volt Pro')
        self.assertNotContains(response, 'Karachi Master Plumbers')

    # US12: Location-Based Provider Search
    def test_search_by_location(self):
        # Case-insensitive search for 'lahore'
        response = self.client.get(reverse('discovery:search') + '?location=lahore')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lahore Volt Pro')
        self.assertNotContains(response, 'Karachi Master Plumbers')

    def test_search_by_keyword(self):
        response = self.client.get(reverse('discovery:search') + '?q=wiring')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lahore Volt Pro')

    # US13: Filtering and Sorting
    def test_filter_by_rating(self):
        # Minimum rating 4.5 should only return Lahore Volt Pro (4.90), not Karachi Master Plumbers (4.20)
        response = self.client.get(reverse('discovery:search') + '?rating=4.5')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lahore Volt Pro')
        self.assertNotContains(response, 'Karachi Master Plumbers')

    def test_filter_by_online_availability(self):
        response = self.client.get(reverse('discovery:search') + '?availability=online')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lahore Volt Pro')
        self.assertNotContains(response, 'Karachi Master Plumbers')

    def test_sorting_by_price_ascending(self):
        response = self.client.get(reverse('discovery:search') + '?sort=price_asc')
        self.assertEqual(response.status_code, 200)
        # Karachi Plumber (PKR 1000/hr) should appear before Lahore Volt Pro (PKR 1500/hr)
        content = response.content.decode('utf-8')
        pos_karachi = content.find('Karachi Master Plumbers')
        pos_lahore = content.find('Lahore Volt Pro')
        self.assertTrue(pos_karachi < pos_lahore)

    # US14: Customer Favourites
    def test_customer_toggle_favourite(self):
        self.client.login(username='cust@fixora.com', password='Password123!')
        # 1. Add favourite
        response = self.client.get(reverse('discovery:toggle_favourite', args=[self.p1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favourite.objects.filter(customer=self.customer, provider=self.p1).exists())

        # 2. Check dedicated favourites page
        fav_page = self.client.get(reverse('discovery:favourites_list'))
        self.assertEqual(fav_page.status_code, 200)
        self.assertContains(fav_page, 'Lahore Volt Pro')

        # 3. Toggle off
        self.client.get(reverse('discovery:toggle_favourite', args=[self.p1.pk]))
        self.assertFalse(Favourite.objects.filter(customer=self.customer, provider=self.p1).exists())
