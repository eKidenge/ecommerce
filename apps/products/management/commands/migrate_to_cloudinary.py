import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.products.models import ProductImage
import cloudinary.uploader

class Command(BaseCommand):
    help = 'Migrate existing product images to Cloudinary'

    def handle(self, *args, **kwargs):
        self.stdout.write('Migrating product images to Cloudinary...')
        
        images = ProductImage.objects.all()
        migrated = 0
        
        for img in images:
            # Skip if already a Cloudinary URL
            if img.image.name.startswith('http'):
                self.stdout.write(f'   ⏭️ {img.product.name} already on Cloudinary')
                continue
            
            try:
                # Get the local file path
                file_path = img.image.path
                
                if not os.path.exists(file_path):
                    self.stdout.write(f'   ⚠️ File not found: {file_path}')
                    continue
                
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file_path,
                    folder='products',
                    public_id=img.product.slug,
                    overwrite=True
                )
                
                # Update the image field with Cloudinary URL
                img.image = upload_result['secure_url']
                img.save()
                
                migrated += 1
                self.stdout.write(self.style.SUCCESS(f'   ✅ Migrated: {img.product.name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error for {img.product.name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Migrated {migrated} images to Cloudinary'))