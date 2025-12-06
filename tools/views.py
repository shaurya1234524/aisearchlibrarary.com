from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import EnhancedSignUpForm, EnhancedLoginForm
from .email_verification import send_verification_email, verify_email_token
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect

from tools.models import Tool, CATEGORY_CHOICES
from .forms import ToolForm

from django.views.generic import ListView, DetailView
# ---------------------------
# Submit a Tool
# ---------------------------
def indexnow(request):
    return render(request,"9f4a2c1e8b7d6f3a2e1b4c9d0f6a7b8c.txt")
def submit_tool(request):
    if request.method == 'POST':
        form = ToolForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('tools:list')  # ✅ must exist in urls.py
    else:
        form = ToolForm()

    return render(request, 'tools/submit_tool.html', {
        'form': form,
    })


# ---------------------------
# Tool List (with filters)
# ---------------------------
class ToolListView(ListView):
    model = Tool
    template_name = 'tools/tool_list.html'
    context_object_name = 'tools'
    paginate_by = 24

    def get_queryset(self):
        qs = Tool.objects.all().select_related().prefetch_related('upvoted_by')
        
        category = self.request.GET.get('category')
        pricing = self.request.GET.get('pricing')
        sort = self.request.GET.get('sort')
        search = self.request.GET.get('search')
        verified = self.request.GET.get('verified')
        min_score = self.request.GET.get('min_score')

        if category:
            qs = qs.filter(category=category)

        if pricing:
            qs = qs.filter(pricing=pricing)
        
        if verified:
            qs = qs.filter(is_verified=True)
        
        if min_score:
            try:
                score = int(min_score)
                qs = qs.filter(success_score__gte=score)
            except (ValueError, TypeError):
                pass

        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(long_description__icontains=search) |
                Q(tags__icontains=search) |
                Q(tech_stack__icontains=search)
            )

        if sort == 'upvotes':
            qs = qs.order_by('-upvotes')
        elif sort == 'created':
            qs = qs.order_by('-created_at')
        elif sort == 'views':
            qs = qs.order_by('-views')
        elif sort == 'verified':
            qs = qs.order_by('-is_verified', '-success_score')
        else:
            qs = qs.order_by('-created_at')

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [c[0] for c in CATEGORY_CHOICES]  
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_pricing'] = self.request.GET.get('pricing', '')
        context['selected_verified'] = self.request.GET.get('verified', '')
        context['selected_sort'] = self.request.GET.get('sort', 'created')
        context['min_score'] = self.request.GET.get('min_score', '')
        
        # Add filtering options
        context['pricing_options'] = ['Free', 'Freemium', 'Premium']
        context['sort_options'] = [
            ('created', '🆕 Newest'),
            ('upvotes', '👍 Most Popular'),
            ('views', '👀 Most Viewed'),
            ('verified', '✓ Verified First'),
        ]
        
        # Add stats
        context['total_tools'] = Tool.objects.count()
        context['verified_tools'] = Tool.objects.filter(is_verified=True).count()
        context['average_score'] = Tool.objects.filter(success_score__gt=0).aggregate(
            avg=__import__('django.db.models', fromlist=['Avg']).Avg('success_score')
        ).get('avg', 0)
        
        return context


# ---------------------------
# Upvote a Tool
# ---------------------------
@require_POST
@login_required
def upvote_tool(request, pk):
    tool = get_object_or_404(Tool, pk=pk)

    if request.user in tool.upvoted_by.all():
        return JsonResponse({'error': 'Already upvoted', 'upvotes': tool.upvotes})

    tool.upvotes += 1
    tool.upvoted_by.add(request.user)
    tool.save()
    return JsonResponse({'upvotes': tool.upvotes})

class ToolDetailView(DetailView):
    model = Tool
    template_name = 'tools/tool_detail.html'
    context_object_name = 'tool'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        """Add enriched data to context"""
        context = super().get_context_data(**kwargs)
        tool = self.get_object()
        
        # Parse JSON fields for template rendering
        import json
        
        context['features'] = []
        if tool.features:
            try:
                context['features'] = json.loads(tool.features)
            except (json.JSONDecodeError, TypeError):
                context['features'] = []
        
        context['company_info'] = {}
        if tool.company_info:
            try:
                context['company_info'] = json.loads(tool.company_info)
            except (json.JSONDecodeError, TypeError):
                context['company_info'] = {}
        
        context['pricing_info'] = {}
        if tool.pricing_info:
            try:
                context['pricing_info'] = json.loads(tool.pricing_info)
            except (json.JSONDecodeError, TypeError):
                context['pricing_info'] = {}
        
        context['social_links'] = {}
        if tool.social_links:
            try:
                context['social_links'] = json.loads(tool.social_links)
            except (json.JSONDecodeError, TypeError):
                context['social_links'] = {}
        
        # Split comma-separated fields
        context['integrations_list'] = [i.strip() for i in tool.integrations.split(',') if i.strip()] if tool.integrations else []
        context['tech_stack_list'] = [t.strip() for t in tool.tech_stack.split(',') if t.strip()] if tool.tech_stack else []
        context['tags_list'] = [tag.strip() for tag in tool.tags.split(',') if tag.strip()] if tool.tags else []
        
        # Split content fields
        context['use_cases_list'] = [u.strip() for u in tool.use_cases.split(',') if u.strip()] if tool.use_cases else []
        context['pros_list'] = [p.strip() for p in tool.pros.split(',') if p.strip()] if tool.pros else []
        context['cons_list'] = [c.strip() for c in tool.cons.split(',') if c.strip()] if tool.cons else []
        
        # Add verification badge info
        context['verification_badge'] = {
            'pending': {'color': 'warning', 'icon': '⏳', 'text': 'Pending Verification'},
            'verified': {'color': 'success', 'icon': '✓', 'text': 'Verified'},
            'rejected': {'color': 'danger', 'icon': '✗', 'text': 'Not Verified'},
        }.get(tool.verification_status, {'color': 'secondary', 'icon': '?', 'text': 'Unknown'})
        
        # Add schema markup for SEO
        context['schema_markup'] = self.generate_schema_markup(tool, context)
        
        # Track view count
        tool.views += 1
        tool.save(update_fields=['views'])
        
        return context
    
    def generate_schema_markup(self, tool, context):
        """Generate JSON-LD schema markup for Google"""
        import json
        from django.templatetags.static import static
        from django.urls import reverse
        from django.contrib.sites.shortcuts import get_current_site
        
        site = get_current_site(self.request)
        domain = f"https://{site.domain}"
        
        # Build software application schema
        schema = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": tool.name,
            "description": tool.meta_description or tool.description,
            "url": f"{domain}{tool.get_absolute_url()}",
            "image": f"{domain}{tool.image.url}" if tool.image else None,
            "applicationCategory": f"https://schema.org/{tool.category.replace(' ', '')}",
            "ratingValue": min(5, (tool.success_score or 0) / 20),
            "ratingCount": max(1, tool.upvotes),
            "operatingSystem": "Web, iOS, Android",
        }
        
        # Add offer if pricing info available
        if context.get('pricing_info'):
            pricing = context['pricing_info']
            if isinstance(pricing, dict):
                offers = []
                for tier, price in pricing.items():
                    offers.append({
                        "@type": "Offer",
                        "name": tier,
                        "price": price if isinstance(price, str) else "Contact for pricing",
                        "url": tool.website
                    })
                if offers:
                    schema["offers"] = offers
        
        # Add creator/provider
        if context.get('company_info'):
            company = context['company_info']
            if isinstance(company, dict):
                schema["creator"] = {
                    "@type": "Organization",
                    "name": company.get('name', ''),
                }
        
        return json.dumps(schema)
# ---------------------------
# Signup View
# ---------------------------
from .forms import EnhancedSignUpForm, EnhancedLoginForm
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def signup_view(request):
    """Enhanced signup view with email verification and auto-login"""
    if request.user.is_authenticated:
        return redirect('tools:list')
    
    if request.method == 'POST':
        form = EnhancedSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 
                f'Welcome {username}! Your account has been created successfully.')
            # Auto-login user after signup
            user = authenticate(username=user.username, password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
                return redirect('tools:list')
            return redirect('login')
        else:
            # Add form errors as messages for better UX
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = EnhancedSignUpForm()
    
    return render(request, 'signup.html', {'form': form})


# ---------------------------
# Email Verification View
# ---------------------------
def verify_email(request, uidb64, token):
    """Verify email with token from email link"""
    user = verify_email_token(uidb64, token)
    
    if user is not None:
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 
                'Email verified successfully! Your account is now active. Please login.')
        else:
            messages.info(request, 'Your email was already verified.')
        return redirect('login')
    else:
        messages.error(request, 
            'Email verification link is invalid or has expired. Please try signing up again.')
        return redirect('signup')


# ---------------------------
# Resend Verification Email
# ---------------------------
def resend_verification_email(request):
    """Allow user to resend verification email"""
    if request.user.is_authenticated:
        return redirect('tools:list')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(email=email)
                if not user.is_active:
                    if send_verification_email(user, request):
                        messages.success(request, 
                            'Verification email has been sent. Please check your inbox.')
                    else:
                        messages.error(request, 
                            'Failed to send verification email. Please try again later.')
                else:
                    messages.info(request, 
                        'This email is already verified. Please login instead.')
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                messages.info(request, 
                    'If an unverified account exists with this email, a verification link has been sent.')
        else:
            messages.error(request, 'Please enter your email address.')
    
    return render(request, 'resend_verification.html')



# ---------------------------
# About Us Page
# ---------------------------
def aboutus(request):
    return render(request, "about.html")
from django.shortcuts import render, get_object_or_404
from .models import Tool, CATEGORY_CHOICES
from django.utils.text import slugify
from django.http import Http404

# ---------------------------
# Individual Category Pages
# ---------------------------
def productivity_tools(request):
    """Productivity Tools Category Page"""
    return category_page_view(request, 'Productivity', 'productivity-tools.html')

def marketing_tools(request):
    """Marketing Tools Category Page"""
    return category_page_view(request, 'Marketing', 'marketing-tools.html')

def generative_ai(request):
    """Design Tools Category Page"""
    return category_page_view(request, 'Generative AI', 'generative_ai.html')

def image_generation(request):
    """AI Art Tools Category Page"""
    return category_page_view(request, 'Image Generation', 'image_generation.html')

def web_development_tools(request):
    """Web Development Tools Category Page"""
    return category_page_view(request, 'Web Development', 'web-development-tools.html')

def video_generation(request):
    """Writing Tools Category Page"""
    return category_page_view(request, 'Video Generation', 'video_generation.html')

def education_tools(request):
    """Education Tools Category Page"""
    return category_page_view(request, 'Education', 'education-tools.html')

def data_analysis_tools(request):
    """Data Analysis Tools Category Page"""
    return category_page_view(request, 'Data Analysis', 'data-analysis-tools.html')

def automation_tools(request):
    """Automation Tools Category Page"""
    return category_page_view(request, 'Automation', 'automation-tools.html')

def ai_chatbots(request):
    """Cybersecurity Tools Category Page"""
    return category_page_view(request, 'AI Tools', 'ai_chatbots.html')
def privacy_policy(request):
    return render(request,"privacy_policy.html")
def terms_of_Service(request):
    return render (request,'terms_of_service.html')
# views.py
from django.shortcuts import render

def cookie_policy(request):
    return render(request, "cookie_policy.html")

def category_page_view(request, category_name, template_name):
    """Generic function to handle individual category pages"""
    # Check if category exists in choices
    valid_categories = [choice[0] for choice in CATEGORY_CHOICES]
    if category_name not in valid_categories:
        raise Http404("Category not found")
    
    # Get tools for this category
    tools = Tool.objects.filter(category=category_name)
    
    # Add filtering options
    pricing = request.GET.get('pricing')
    sort = request.GET.get('sort')
    search = request.GET.get('search')

    if pricing:
        tools = tools.filter(pricing=pricing)

    if search:
        tools = tools.filter(name__icontains=search) | tools.filter(description__icontains=search)

    if sort == 'upvotes':
        tools = tools.order_by('-upvotes')
    elif sort == 'created':
        tools = tools.order_by('-created_at')
    else:
        tools = tools.order_by('-upvotes')  # Default sort by upvotes

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(tools, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get related categories
    related_categories = []
    for choice in CATEGORY_CHOICES:
        if choice[0] != category_name and Tool.objects.filter(category=choice[0]).exists():
            related_categories.append({
                'name': choice[0],
                'count': Tool.objects.filter(category=choice[0]).count()
            })
    
    # Get category stats
    total_tools = Tool.objects.filter(category=category_name).count()
    free_tools = Tool.objects.filter(category=category_name, pricing='Free').count()
    premium_tools = Tool.objects.filter(category=category_name, pricing='Premium').count()
    freemium_tools = Tool.objects.filter(category=category_name, pricing='Freemium').count()
    
    context = {
        'category_name': category_name,
        'tools': page_obj,
        'page_obj': page_obj,
        'categories': [c[0] for c in CATEGORY_CHOICES],
        'search_query': request.GET.get('search', ''),
        'selected_pricing': request.GET.get('pricing', ''),
        'selected_sort': request.GET.get('sort', 'upvotes'),
        'related_categories': related_categories[:6],
        'total_tools': total_tools,
        'free_tools': free_tools,
        'premium_tools': premium_tools,
        'freemium_tools': freemium_tools,
    }
    
    return render(request, f'categories/{template_name}', context)


class CategoryListView(ListView):
    model = Tool
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Get all categories with tool counts
        categories_with_counts = []
        for choice in CATEGORY_CHOICES:
            category_name = choice[0]
            tool_count = Tool.objects.filter(category=category_name).count()
            if tool_count > 0:  # Only show categories that have tools
                categories_with_counts.append({
                    'name': category_name,
                    'count': tool_count,
                    'slug': category_name.lower().replace(' ', '-').replace('/', '-')
                })
        
        # Sort by tool count (most popular first)
        return sorted(categories_with_counts, key=lambda x: x['count'], reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_categories'] = len(self.get_queryset())
        return context


# Logout is already handled by Django's auth_views.LogoutView in urls.py
# No need to define a custom logout view here


def sitemap(request):
    return render(request,"sitemap.xml")


def robots(request):
    return render(request,"robots.txt")

