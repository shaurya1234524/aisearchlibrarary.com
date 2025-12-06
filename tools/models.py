from django.db import models
from django.contrib.auth.models import User
from tools.storage import MediaStorage
import os
from django.urls import reverse
PRICING_CHOICES = (
    ('Free', 'Free'),
    ('Premium', 'Premium'),
    ('Freemium', 'Freemium'),
)

CATEGORY_CHOICES = (
    ('AI Art', 'AI Art'),
    ('AI Tools', 'AI Tools'),
    ('App Development', 'App Development'),
    ('Automation', 'Automation'),
    ('Blockchain', 'Blockchain'),
    ('Career', 'Career'),
    ('Cloud Computing', 'Cloud Computing'),
    ('Copywriting', 'Copywriting'),
    ('Cryptocurrency', 'Cryptocurrency'),
    ('Customer Support', 'Customer Support'),
    ('Cybersecurity', 'Cybersecurity'),
    ('Data Analysis', 'Data Analysis'),
    ('Deep Learning', 'Deep Learning'),
    ('Design', 'Design'),
    ('E-commerce', 'E-commerce'),
    ('Education', 'Education'),
    ('Entrepreneurship', 'Entrepreneurship'),
    ('Fitness', 'Fitness'),
    ('Food & Beverages', 'Food & Beverages'),
    ('Gaming', 'Gaming'),
    ('Generative AI', 'Generative AI'),
    ('Health', 'Health'),
    ('HR', 'HR'),
    ('Image Generation', 'Image Generation'),
    ('Investing', 'Investing'),
    ('IoT', 'IoT'),
    ('Legal', 'Legal'),
    ('Lifestyle', 'Lifestyle'),
    ('Machine Learning', 'Machine Learning'),
    ('Marketing', 'Marketing'),
    ('Mental Health', 'Mental Health'),
    ('Music', 'Music'),
    ('Networking', 'Networking'),
    ('News', 'News'),
    ('Personal Finance', 'Personal Finance'),
    ('Photography', 'Photography'),
    ('Product Management', 'Product Management'),
    ('Productivity', 'Productivity'),
    ('Real Estate', 'Real Estate'),
    ('Robotics', 'Robotics'),
    ('SEO', 'SEO'),
    ('Social Media', 'Social Media'),
    ('Sports', 'Sports'),
    ('Startups', 'Startups'),
    ('Travel', 'Travel'),
    ('UI/UX', 'UI/UX'),
    ('Video Editing', 'Video Editing'),
    ('Video Generation', 'Video Generation'),
    ('VR/AR', 'VR/AR'),
    ('Web Development', 'Web Development'),
    ('Writing', 'Writing'),
)



class Tool(models.Model):
    # Core Information
    name = models.CharField(max_length=200)
    description = models.TextField()
    # Use S3-backed MediaStorage only when USE_S3=1 is set in the environment.
    # In development (no USE_S3) the field will use Django's default storage
    # which is set to FileSystemStorage in DEBUG in settings.py.
    _use_s3 = os.getenv('USE_S3', '0') == '1'
    _storage_instance = MediaStorage() if _use_s3 else None
    image = models.ImageField(
        upload_to='tools/%Y/%m/',
        blank=True,
        null=True,
        storage=_storage_instance,
        help_text='Upload tool icon/logo (JPG, PNG, GIF). Max 5MB. Automatically optimized.'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='AI Tools')
    tags = models.CharField(max_length=200, blank=True)
    pricing = models.CharField(max_length=10, choices=PRICING_CHOICES, default='Free')
    website = models.URLField(blank=True, null=True)
    
    # Engagement Metrics
    upvotes = models.PositiveIntegerField(default=0)
    upvoted_by = models.ManyToManyField(User, blank=True, related_name='upvoted_tools')
    views = models.PositiveIntegerField(default=0)
    
    # SEO Fields
    slug = models.SlugField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    seo_title = models.CharField(max_length=60, blank=True)
    
    # Rich Information
    features = models.TextField(blank=True, help_text="JSON formatted features list")
    company_info = models.TextField(blank=True, help_text="JSON formatted company info")
    pricing_info = models.TextField(blank=True, help_text="JSON formatted pricing details")
    integrations = models.TextField(blank=True, help_text="Comma-separated integrations")
    tech_stack = models.CharField(max_length=200, blank=True, help_text="Technologies used")
    social_links = models.TextField(blank=True, help_text="JSON formatted social links")
    
    # Quality Metrics
    success_score = models.PositiveIntegerField(default=0, help_text="0-100 tool quality score")
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')],
        default='pending'
    )
    
    # Content
    long_description = models.TextField(blank=True, help_text="Extended description for SEO")
    use_cases = models.TextField(blank=True, help_text="Typical use cases")
    pros = models.TextField(blank=True, help_text="Comma-separated pros")
    cons = models.TextField(blank=True, help_text="Comma-separated cons")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-upvotes', '-created_at']
        indexes = [
            models.Index(fields=['category', '-upvotes']),
            models.Index(fields=['pricing', '-views']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse("tools:detail", args=[self.id])


