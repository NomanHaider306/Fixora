from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from providers.models import ProviderProfile, PortfolioImage, IdentityDocument
from services.models import ServiceCategory

User = get_user_model()


class ProvidersSprint2Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='electrician@fixora.com',
            email='electrician@fixora.com',
            password='Password123!',
            first_name='Muhammad',
            last_name='Usman',
            role=User.Role.PROVIDER
        )
        self.profile = ProviderProfile.objects.create(
            user=self.user,
            business_name='Usman Electric Solutions',
            hourly_rate=1500.00,
            starting_price=2000.00,
            city='Lahore'
        )
        self.cat1 = ServiceCategory.objects.create(name='Electrical', icon_class='bi-lightning')
        self.cat2 = ServiceCategory.objects.create(name='Handyman', icon_class='bi-tools')

    # US06 & US07: Profile Update and Category Selection
    def test_provider_profile_edit(self):
        self.client.login(username='electrician@fixora.com', password='Password123!')
        response = self.client.post(reverse('providers:profile_edit'), {
            'business_name': 'Usman Master Electric',
            'introduction': 'Certified expert in home rewiring.',
            'skills': 'Wiring, Breakers, EV Chargers',
            'experience_years': 8,
            'categories': [self.cat1.id, self.cat2.id],
            'service_area': 'Lahore Metro',
            'city': 'Lahore',
            'hourly_rate': '1800.00',
            'starting_price': '2200.00',
            'is_online': True
        })
        self.assertRedirects(response, reverse('providers:profile_edit'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.business_name, 'Usman Master Electric')
        self.assertEqual(self.profile.hourly_rate, 1800.00)
        self.assertEqual(self.profile.categories.count(), 2)

    # US08: Portfolio Photos
    def test_portfolio_upload_and_delete(self):
        self.client.login(username='electrician@fixora.com', password='Password123!')
        import io
        from PIL import Image
        img = Image.new('RGB', (10, 10), color='blue')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        dummy_img = SimpleUploadedFile("panel.jpg", buf.getvalue(), content_type="image/jpeg")

        response = self.client.post(reverse('providers:portfolio_manage'), {
            'image': dummy_img,
            'caption': 'Kitchen subpanel replacement'
        })
        self.assertRedirects(response, reverse('providers:portfolio_manage'))
        self.assertEqual(PortfolioImage.objects.filter(provider=self.profile).count(), 1)
        photo = PortfolioImage.objects.filter(provider=self.profile).first()
        self.assertEqual(photo.caption, 'Kitchen subpanel replacement')

        # Test photo deletion
        del_resp = self.client.post(reverse('providers:portfolio_delete', args=[photo.pk]))
        self.assertRedirects(del_resp, reverse('providers:portfolio_manage'))
        self.assertEqual(PortfolioImage.objects.filter(provider=self.profile).count(), 0)

    # US09: Identity Document Submission
    def test_identity_document_submission(self):
        self.client.login(username='electrician@fixora.com', password='Password123!')
        dummy_doc = SimpleUploadedFile("license.pdf", b"fake pdf content", content_type="application/pdf")

        response = self.client.post(reverse('providers:document_submission'), {
            'document_type': IdentityDocument.DocType.LICENSE,
            'document_file': dummy_doc,
            'notes': 'State electrical license #44102'
        })
        self.assertRedirects(response, reverse('providers:document_submission'))
        self.assertEqual(IdentityDocument.objects.filter(provider=self.profile).count(), 1)
        doc = IdentityDocument.objects.filter(provider=self.profile).first()
        self.assertEqual(doc.status, IdentityDocument.Status.SUBMITTED)

    # US10: Customer Provider Profile View
    def test_public_provider_profile_view(self):
        response = self.client.get(reverse('providers:public_profile', args=[self.profile.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usman Electric Solutions')
        self.assertContains(response, 'Ratings & Reviews')
        self.assertContains(response, 'No reviews recorded yet')
