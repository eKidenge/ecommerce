from django.core.management.base import BaseCommand
from apps.products.models import Category

class Command(BaseCommand):
    help = 'Create default product categories'

    def handle(self, *args, **kwargs):
        categories = [
            'Electronics',
            'Clothing & Fashion',
            'Books & Media',
            'Home & Garden',
            'Beauty & Health',
            'Sports & Outdoors',
            'Toys & Games',
            'Automotive',
            'Food & Grocery',
            'Office Supplies'
        ]
        
        created = 0
        for name in categories:
            category, created_flag = Category.objects.get_or_create(name=name)
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Created category: {name}'))
            else:
                self.stdout.write(f'⏭️ Category already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {created} new categories'))
        self.stdout.write(f'📊 Total categories: {Category.objects.count()}')