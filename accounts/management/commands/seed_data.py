from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from services.models import ServiceCategory
from providers.models import ProviderProfile, PortfolioImage, IdentityDocument
from availability.models import WeeklySchedule, BlockedDate
from estimates.models import EstimateRequest, EstimateResponse
from discovery.models import Favourite
from datetime import date, timedelta, time

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial database records for demonstration and testing of Fixora marketplace with local Pakistani context."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Fixora database records (Local Pakistani context)...")

        # 1. Administrator Account
        admin_user, created = User.objects.get_or_create(
            email='admin@fixora.com',
            defaults={
                'username': 'admin@fixora.com',
                'first_name': 'Noman',
                'last_name': 'Haider',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+92 300 1112233'
            }
        )
        admin_user.first_name = 'Noman'
        admin_user.last_name = 'Haider'
        admin_user.phone_number = '+92 300 1112233'
        admin_user.set_password('admin1234')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Configured Admin: Noman Haider (admin@fixora.com / admin1234)"))

        # 2. Service Categories
        categories_data = [
            {
                'name': 'Electrical Services',
                'description': 'Certified electricians for wiring, DB panel dressing, UPS/Solar setup, lighting, and electrical troubleshooting.',
                'icon_class': 'bi-lightning-charge',
            },
            {
                'name': 'Plumbing & Piping',
                'description': 'Emergency leak repairs, sanitary pipe fitting, geyser repair & installation, water pumps, and fixture fitting.',
                'icon_class': 'bi-wrench',
            },
            {
                'name': 'Carpentry & Woodwork',
                'description': 'Custom cabinets, furniture polish & repair, door locks & framing, wooden flooring, and architectural woodwork.',
                'icon_class': 'bi-hammer',
            },
            {
                'name': 'Painting & Wall Finishing',
                'description': 'Interior and exterior painting, weather-sheet, wallpaper installation, drywall repair, and distemper work.',
                'icon_class': 'bi-paint-bucket',
            },
            {
                'name': 'Steel Work & Metal Fabrication',
                'description': 'Main security gates, window safety grills, staircase railings, shed welding, and structural steel fabrication.',
                'icon_class': 'bi-gear-wide-connected',
            },
            {
                'name': 'Home Maintenance & Handyman',
                'description': 'General household fixes, wall mounting, curtain rods, door adjustments, and quick fixes.',
                'icon_class': 'bi-tools',
            },
            {
                'name': 'Appliance Repair',
                'description': 'Fast diagnostic and repair services for refrigerators, ACs, washing machines, microwaves, and water dispensers.',
                'icon_class': 'bi-cpu',
            },
            {
                'name': 'Cleaning Services',
                'description': 'Deep home cleaning, sofa/carpet shampooing, water tank cleaning, and post-renovation cleanup.',
                'icon_class': 'bi-stars',
            },
        ]

        category_objs = {}
        for cat_info in categories_data:
            cat_obj, _ = ServiceCategory.objects.get_or_create(
                name=cat_info['name'],
                defaults={
                    'description': cat_info['description'],
                    'icon_class': cat_info['icon_class'],
                    'is_active': True,
                }
            )
            cat_obj.description = cat_info['description']
            cat_obj.icon_class = cat_info['icon_class']
            cat_obj.save()
            category_objs[cat_info['name']] = cat_obj

        self.stdout.write(self.style.SUCCESS(f"Configured {len(category_objs)} service categories."))

        # 3. Customer Account (Local Pakistani)
        customer_user, created = User.objects.get_or_create(
            email='customer@fixora.com',
            defaults={
                'username': 'customer@fixora.com',
                'first_name': 'Mayeda',
                'last_name': 'Qamar',
                'role': User.Role.CUSTOMER,
                'phone_number': '+92 321 4445566'
            }
        )
        customer_user.first_name = 'Mayeda'
        customer_user.last_name = 'Qamar'
        customer_user.phone_number = '+92 321 4445566'
        customer_user.set_password('customer1234')
        customer_user.save()

        from accounts.models import CustomerProfile
        cust_profile, _ = CustomerProfile.objects.get_or_create(
            user=customer_user,
            defaults={'city': 'Lahore', 'address': 'House 42, Block B, DHA Phase 5, Lahore'}
        )
        cust_profile.city = 'Lahore'
        cust_profile.address = 'House 42, Block B, DHA Phase 5, Lahore'
        cust_profile.save()
        self.stdout.write(self.style.SUCCESS("Configured Customer: Mayeda Qamar (customer@fixora.com / customer1234 - Lahore)"))

        # 4. Service Providers (Local Pakistani names, cities, PKR rates)
        providers_data = [
            {
                'email': 'electrician@fixora.com',
                'first_name': 'Muhammad',
                'last_name': 'Usman',
                'business_name': 'Lahore VoltMaster Electrical Solutions',
                'phone': '+92 300 5556677',
                'city': 'Lahore',
                'service_area': 'DHA, Gulberg, Cantt, Model Town, Johar Town (25-km radius)',
                'hourly_rate': 1500.00,
                'starting_price': 2000.00,
                'experience': 9,
                'skills': 'DB panel upgrades, Inverter/UPS wiring, AC cabling, Short circuit troubleshooting, LED concealed lighting',
                'intro': 'Certified electrical technician with over 9 years of residential experience across Lahore. Specialized in safe home rewiring, UPS/solar connection, and neat DB dressing. Guaranteed quality and electrical safety for your household.',
                'categories': ['Electrical Services', 'Home Maintenance & Handyman'],
                'is_verified': True,
            },
            {
                'email': 'plumber@fixora.com',
                'first_name': 'Bilal',
                'last_name': 'Ahmed',
                'business_name': 'Pak AquaFlow Plumbing & Sanitary Works',
                'phone': '+92 321 6667788',
                'city': 'Lahore',
                'service_area': 'Johar Town, Faisal Town, Wapda Town, Garden Town, Bahria Town',
                'hourly_rate': 1200.00,
                'starting_price': 1500.00,
                'experience': 12,
                'skills': 'Underground leakage detection, PPRC/CPVC piping, Geyser repair & installation, Water pump motor repair, Sanitary fittings',
                'intro': 'Prompt, courteous and reliable plumbing service across Lahore. Specializing in emergency leak fixing, instant gas/electric geysers, and complete bathroom sanitary renovation. Honest upfront pricing with zero hidden charges.',
                'categories': ['Plumbing & Piping', 'Home Maintenance & Handyman'],
                'is_verified': True,
            },
            {
                'email': 'carpenter@fixora.com',
                'first_name': 'Tariq',
                'last_name': 'Mahmood',
                'business_name': 'Heritage Custom Woodcraft & Interiors',
                'phone': '+92 333 7778899',
                'city': 'Rawalpindi',
                'service_area': 'Saddar, Westridge, Bahria Town Rawalpindi/Islamabad, DHA Phase 1 & 2',
                'hourly_rate': 1800.00,
                'starting_price': 3500.00,
                'experience': 14,
                'skills': 'Custom kitchen cabinets, Wardrobes, Solid wood door framing, Furniture repair & polish, Wooden wall paneling',
                'intro': 'Master artisan with 14 years of woodworking craftsmanship in the Twin Cities. We build bespoke modular kitchens, luxury wardrobes, and restore fine antique wooden furniture with durable lacquer polishing.',
                'categories': ['Carpentry & Woodwork'],
                'is_verified': True,
            },
            {
                'email': 'painter@fixora.com',
                'first_name': 'Zainab',
                'last_name': 'Fatima',
                'business_name': 'Al-Rehman Painting & Wall Art Decorators',
                'phone': '+92 312 8889900',
                'city': 'Karachi',
                'service_area': 'Clifton, DHA, Gulshan-e-Iqbal, PECHS, North Nazimabad',
                'hourly_rate': 1000.00,
                'starting_price': 3000.00,
                'experience': 7,
                'skills': 'Interior wall painting, Weather-sheet exterior, Texture painting, Rockwall, Dampness/Seep treatment',
                'intro': 'Professional painting crew in Karachi providing clean, immaculate finishes without paint splatter. Specialists in anti-fungal treatments, dampness proofing, and modern accent walls.',
                'categories': ['Painting & Wall Finishing'],
                'is_verified': False,
            },
            {
                'email': 'steelworker@fixora.com',
                'first_name': 'Kamran',
                'last_name': 'Ali',
                'business_name': 'Ittefaq Metal & Steel Fabrication Works',
                'phone': '+92 345 9990011',
                'city': 'Faisalabad',
                'service_area': 'Peoples Colony, D Ground, Madina Town, Kohinoor City',
                'hourly_rate': 1600.00,
                'starting_price': 5000.00,
                'experience': 11,
                'skills': 'Security gates, Window safety grills, Staircase railings, Laser cut metal panels, TIG/MIG welding',
                'intro': 'Heavy-duty steel fabrication workshop specializing in durable, elegant house gates, security grills, and modern metal railings. Premium rust-proof primer and electrostatic powder coating.',
                'categories': ['Steel Work & Metal Fabrication'],
                'is_verified': True,
            },
        ]

        provider_profiles = []
        for p_data in providers_data:
            user_obj, u_created = User.objects.get_or_create(
                email=p_data['email'],
                defaults={
                    'username': p_data['email'],
                    'first_name': p_data['first_name'],
                    'last_name': p_data['last_name'],
                    'role': User.Role.PROVIDER,
                    'phone_number': p_data['phone']
                }
            )
            user_obj.first_name = p_data['first_name']
            user_obj.last_name = p_data['last_name']
            user_obj.phone_number = p_data['phone']
            user_obj.set_password('provider1234')
            user_obj.save()

            profile, _ = ProviderProfile.objects.get_or_create(
                user=user_obj,
                defaults={
                    'business_name': p_data['business_name'],
                    'city': p_data['city'],
                    'service_area': p_data['service_area'],
                    'hourly_rate': p_data['hourly_rate'],
                    'starting_price': p_data['starting_price'],
                    'experience_years': p_data['experience'],
                    'skills': p_data['skills'],
                    'introduction': p_data['intro'],
                    'is_verified': p_data['is_verified'],
                    'is_online': True,
                    'rating': 4.90,
                    'review_count': 0
                }
            )
            profile.business_name = p_data['business_name']
            profile.city = p_data['city']
            profile.service_area = p_data['service_area']
            profile.hourly_rate = p_data['hourly_rate']
            profile.starting_price = p_data['starting_price']
            profile.experience_years = p_data['experience']
            profile.skills = p_data['skills']
            profile.introduction = p_data['intro']
            profile.is_verified = p_data['is_verified']
            profile.is_online = True
            profile.save()

            profile.categories.clear()
            for cat_name in p_data['categories']:
                if cat_name in category_objs:
                    profile.categories.add(category_objs[cat_name])

            # Populate Weekly Schedules (Mon-Fri 09:00 - 18:00, Sat 10:00 - 16:00, Sun off)
            for day_idx, _ in WeeklySchedule.DAYS_OF_WEEK:
                is_work = (day_idx < 6)
                st = time(9, 0) if day_idx < 5 else time(10, 0)
                et = time(18, 0) if day_idx < 5 else time(16, 0)
                WeeklySchedule.objects.update_or_create(
                    provider=profile,
                    day_of_week=day_idx,
                    defaults={
                        'is_working': is_work,
                        'start_time': st,
                        'end_time': et
                    }
                )

            provider_profiles.append(profile)

        self.stdout.write(self.style.SUCCESS(f"Configured {len(provider_profiles)} local Pakistani provider profiles with schedules."))

        # 5. Customer Favourites (US14)
        if provider_profiles:
            Favourite.objects.get_or_create(customer=customer_user, provider=provider_profiles[0])
            Favourite.objects.get_or_create(customer=customer_user, provider=provider_profiles[1])
            self.stdout.write(self.style.SUCCESS("Configured customer favourites."))

        # 6. Sample Blocked Date (US16)
        if provider_profiles:
            next_tuesday = date.today() + timedelta(days=(1 - date.today().weekday()) % 7 + 7)
            BlockedDate.objects.get_or_create(
                provider=provider_profiles[0],
                date=next_tuesday,
                defaults={'reason': 'Annual Electrical Testing & Calibration'}
            )

        # 7. Sample Estimate Requests and Responses in PKR (US24)
        if provider_profiles:
            # Estimate 1: Responded in PKR
            est1, created1 = EstimateRequest.objects.get_or_create(
                customer=customer_user,
                provider=provider_profiles[0],
                title="Kitchen Recessed LED Lighting & Main DB Board Wiring",
                defaults={
                    'service_category': category_objs.get('Electrical Services'),
                    'description': "We are renovating our kitchen in DHA Phase 5. Need 8 LED concealed ceiling lights wired and installed, plus replacing an old distribution board with modern circuit breakers.",
                    'job_address': "House 42, Block B, DHA Phase 5, Lahore",
                    'preferred_date': date.today() + timedelta(days=5),
                    'status': EstimateRequest.Status.RESPONDED
                }
            )
            est1.title = "Kitchen Recessed LED Lighting & Main DB Board Wiring"
            est1.job_address = "House 42, Block B, DHA Phase 5, Lahore"
            est1.status = EstimateRequest.Status.RESPONDED
            est1.save()

            EstimateResponse.objects.update_or_create(
                request=est1,
                defaults={
                    'estimated_price': 12500.00,
                    'explanation': "Estimated Labor: PKR 7,500 (approx 5 hours work). Main DB board dressing and safety breaker test: PKR 5,000. LED fixtures to be supplied by customer or billed as per market receipt.",
                    'valid_until': date.today() + timedelta(days=20)
                }
            )

            # Estimate 2: Pending in PKR
            est2, _ = EstimateRequest.objects.get_or_create(
                customer=customer_user,
                provider=provider_profiles[1],
                title="Master Bathroom Concealed PPRC Pipe Leak Investigation",
                defaults={
                    'service_category': category_objs.get('Plumbing & Piping'),
                    'description': "Noticed water moisture stains on wall adjacent to bathroom mixer tap. Need pressure test and leak tracing.",
                    'job_address': "House 42, Block B, DHA Phase 5, Lahore",
                    'preferred_date': date.today() + timedelta(days=3),
                    'status': EstimateRequest.Status.PENDING
                }
            )
            est2.job_address = "House 42, Block B, DHA Phase 5, Lahore"
            est2.save()

            self.stdout.write(self.style.SUCCESS("Configured sample PKR estimate requests and response."))

        self.stdout.write(self.style.SUCCESS("Fixora database successfully reseeded with local Pakistani profiles, locations, and PKR prices!"))
