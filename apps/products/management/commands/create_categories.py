from django.core.management.base import BaseCommand
from apps.products.models import Category, Brand

class Command(BaseCommand):
    help = 'Create default product categories and brands'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('  CREATING CATEGORIES AND BRANDS'))
        self.stdout.write(self.style.SUCCESS('='*50))
        
        # Create Categories
        self.stdout.write('\nCreating categories...')
        
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
            'Office Supplies',
            'Handmade & Crafts',
            'Pet Supplies',
            'Baby & Kids',
            'Jewelry & Accessories',
            'Shoes & Footwear',
        ]
        
        created_categories = 0
        for name in categories:
            category, created_flag = Category.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created_flag:
                created_categories += 1
                self.stdout.write(self.style.SUCCESS(f'   Created category: {name}'))
            else:
                self.stdout.write(f'   Category already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n   Created {created_categories} new categories'))
        self.stdout.write(f'   Total categories: {Category.objects.count()}')
        
        # Create Brands
        self.stdout.write('\nCreating brands...')
        
        brands = [
            'Apple',
            'Samsung',
            'Nike',
            'Adidas',
            'Sony',
            'LG',
            'HP',
            'Dell',
            'Canon',
            'KitchenAid',
            'Bose',
            'Panasonic',
            'Philips',
            'Toshiba',
            'Lenovo',
            'Microsoft',
            'Asus',
            'Acer',
            'Google',
            'Amazon',
            'Huawei',
            'Xiaomi',
            'OnePlus',
            'Oppo',
            'Vivo',
            'Realme',
            'Motorola',
            'Nokia',
            'BlackBerry',
            'HTC',
            'Garmin',
            'Fitbit',
            'JBL',
            'Beats',
            'Skullcandy',
            'Plantronics',
            'Logitech',
            'Razer',
            'Corsair',
            'SteelSeries',
        ]
        
        created_brands = 0
        for name in brands:
            brand, created_flag = Brand.objects.get_or_create(
                name=name,
                defaults={'is_active': True}
            )
            if created_flag:
                created_brands += 1
                self.stdout.write(self.style.SUCCESS(f'   Created brand: {name}'))
            else:
                self.stdout.write(f'   Brand already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n   Created {created_brands} new brands'))
        self.stdout.write(f'   Total brands: {Brand.objects.count()}')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('  SEEDING COMPLETE'))
        self.stdout.write('='*50)
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'   Categories: {Category.objects.count()}')
        self.stdout.write(f'   Brands: {Brand.objects.count()}')
        self.stdout.write('\n' + '='*50)