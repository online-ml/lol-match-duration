from django.conf import settings
from django.contrib import auth
from django.core.management import base


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        user_model = auth.get_user_model()

        for full_name, email in settings.ADMINS:
            first_name, last_name = full_name.split(' ')

            if user_model.objects.filter(email=email).exists():
                print(f'Admin account for {first_name} {last_name} ({email}) already exists')
                continue
            print(f'Creating admin account for {first_name} {last_name} ({email})')

            user_model.objects.create_superuser(
                email=email,
                username=email,
                password=settings.ADMIN_PASSWORD,
            )
