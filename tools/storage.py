"""
Custom S3 storage backend for handling image uploads to AWS S3 with optimization
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import default_storage
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class MediaStorage(S3Boto3Storage):
    """Custom storage for media files (images, videos, etc.) on S3"""
    location = 'media'
   
    file_overwrite = True
    max_memory_size = 5242880  # 5MB
    
    def get_accessed_time(self, name):
        """Return the total accessed time of the storage if possible."""
        return None
    
    def get_created_time(self, name):
        """Return the creation time of the storage if possible."""
        return None
    
    def get_modified_time(self, name):
        """Return the last modified time of the storage if possible."""
        return None


class OptimizedImageStorage(S3Boto3Storage):
    """
    Custom storage backend that automatically optimizes images before uploading to S3.
    - Compresses images
    - Resizes large images
    - Converts to efficient formats
    """
    location = 'media/images'
   
    file_overwrite = True
    max_memory_size = 5242880  # 5MB
    
    def _open(self, name, mode='rb'):
        """Open file from S3"""
        if mode == 'rb':
            return super()._open(name, mode)
        return super()._open(name, mode)
    
    def save(self, name, content, max_length=None, save=True):
        """
        Save the content to S3, optimizing images on the fly
        """
        # Check if it's an image
        if hasattr(content, 'content_type'):
            if content.content_type.startswith('image/'):
                # Optimize image before saving
                try:
                    content = self._optimize_image(content)
                except Exception as e:
                    print(f"Image optimization failed: {e}. Saving original file.")
        
        # Call parent save method
        return super().save(name, content, max_length, save)
    
    def _optimize_image(self, image_file):
        """
        Optimize image: resize, compress, and convert if needed
        """
        try:
            # Open image
            img = Image.open(image_file)
            
            # Convert RGBA to RGB for JPEG
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if image is too large (max width: 1200px, max height: 800px)
            max_width = 1200
            max_height = 800
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = BytesIO()
            format = 'WebP' if img.format != 'GIF' else 'GIF'
            quality = 80 if format == 'WebP' else None
            
            if format == 'WebP':
                img.save(output, format='WEBP', quality=quality, optimize=True)
            else:
                img.save(output, format=format, optimize=True)
            
            output.seek(0)
            
            # Preserve original filename but update extension if converted
            name = image_file.name
            if format == 'WebP' and not name.lower().endswith('.webp'):
                name = os.path.splitext(name)[0] + '.webp'
            
            return ContentFile(output.getvalue(), name=name)
        except Exception as e:
            print(f"Image optimization error: {e}")
            return image_file


class StaticStorage(S3Boto3Storage):
    """Custom storage for static files on S3"""
    location = 'static'
    
    file_overwrite = False
