from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import CustomerProfile

User = get_user_model()


class AuthenticationSprint1Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            username='testcust@fixora.com',
            email='testcust@fixora.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            role=User.Role.CUSTOMER
        )
        CustomerProfile.objects.create(user=self.customer, city='Lahore')

        self.provider = User.objects.create_user(
            username='testpro@fixora.com',
            email='testpro@fixora.com',
            password='Password123!',
            first_name='Bilal',
            last_name='Ahmed',
            role=User.Role.PROVIDER
        )
        from providers.models import ProviderProfile
        ProviderProfile.objects.create(user=self.provider, business_name='Ahmed Sanitary & Repairs')

        self.admin = User.objects.create_user(
            username='testadmin@fixora.com',
            email='testadmin@fixora.com',
            password='Password123!',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

    # US01: User Registration
    def test_customer_registration_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'role': User.Role.CUSTOMER,
            'first_name': 'Jane',
            'last_name': 'Eyre',
            'email': 'jane.eyre@example.com',
            'phone_number': '1234567890',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email='jane.eyre@example.com')
        self.assertEqual(new_user.role, User.Role.CUSTOMER)
        self.assertTrue(CustomerProfile.objects.filter(user=new_user).exists())

    def test_provider_registration_success(self):
        response = self.client.post(reverse('accounts:register'), {
            'role': User.Role.PROVIDER,
            'first_name': 'Bob',
            'last_name': 'Builder',
            'email': 'bob.builder@example.com',
            'phone_number': '1234567890',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email='bob.builder@example.com')
        self.assertEqual(new_user.role, User.Role.PROVIDER)
        from providers.models import ProviderProfile
        self.assertTrue(ProviderProfile.objects.filter(user=new_user).exists())

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'role': User.Role.CUSTOMER,
            'first_name': 'Fail',
            'last_name': 'Test',
            'email': 'fail@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='fail@example.com').exists())

    def test_registration_duplicate_email(self):
        response = self.client.post(reverse('accounts:register'), {
            'role': User.Role.CUSTOMER,
            'first_name': 'Duplicate',
            'last_name': 'User',
            'email': 'testcust@fixora.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)

    # US02: User Login
    def test_customer_login_redirect(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'testcust@fixora.com',
            'password': 'Password123!',
            'remember_me': True
        })
        self.assertEqual(response.status_code, 302)
        # Follow to dashboard redirect
        redirect_response = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(redirect_response, reverse('accounts:customer_dashboard'))

    def test_provider_login_redirect(self):
        self.client.post(reverse('accounts:login'), {
            'email': 'testpro@fixora.com',
            'password': 'Password123!',
        })
        redirect_response = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(redirect_response, reverse('accounts:provider_dashboard'))

    def test_admin_login_redirect(self):
        self.client.post(reverse('accounts:login'), {
            'email': 'testadmin@fixora.com',
            'password': 'Password123!',
        })
        redirect_response = self.client.get(reverse('accounts:dashboard_redirect'))
        self.assertRedirects(redirect_response, reverse('accounts:admin_dashboard'))

    def test_invalid_login_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'testcust@fixora.com',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email address or password")

    # US03: User Logout
    def test_user_logout(self):
        self.client.login(username='testcust@fixora.com', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('discovery:home'))

    # US04: Password Reset Flow
    def test_password_reset_views(self):
        # 1. Form view
        resp1 = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(resp1.status_code, 200)
        # 2. Post email
        resp2 = self.client.post(reverse('accounts:password_reset'), {'email': 'testcust@fixora.com'})
        self.assertRedirects(resp2, reverse('accounts:password_reset_done'))

    # US05: Account Details Update
    def test_account_settings_update(self):
        self.client.login(username='testcust@fixora.com', password='Password123!')
        response = self.client.post(reverse('accounts:account_settings'), {
            'first_name': 'Johnny',
            'last_name': 'Doeman',
            'email': 'testcust@fixora.com',
            'phone_number': '+923001234567',
            'city': 'Islamabad',
            'address': 'Street 10, Sector F-7/2'
        })
        self.assertEqual(response.status_code, 302)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Johnny')
        self.assertEqual(self.customer.phone_number, '+923001234567')
        self.customer.customer_profile.refresh_from_db()
        self.assertEqual(self.customer.customer_profile.city, 'Islamabad')
