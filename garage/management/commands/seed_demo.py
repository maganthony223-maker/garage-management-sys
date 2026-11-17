from django.core.management.base import BaseCommand

from garage.models import Service, Mechanic

SERVICES = [('Repair', 50000, 3), ('Cleaning', 20000, 1), ('Maintenance', 80000, 2),
            ('Painting', 150000, 8), ('Tyre changing', 30000, 1), ('Changing oil', 40000, 1)]


class Command(BaseCommand):
    help = 'Load demo services and mechanics'

    def handle(self, *args, **opts):
        for n, p, d in SERVICES:
            Service.objects.get_or_create(name=n, defaults={'price': p, 'duration_hours': d})
        Mechanic.objects.get_or_create(name='Demo Mechanic', defaults={'speciality': 'General'})
        self.stdout.write(self.style.SUCCESS('Demo data loaded.'))
