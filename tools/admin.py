from django.contrib import admin
from tools.models import Tool
from tools.tool_enricher import ToolInfoEnricher, SEOOptimizer, ToolCategoryOptimizer
import json


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'pricing', 'success_score', 'is_verified', 'views', 'created_at')
    list_filter = ('category', 'pricing', 'is_verified', 'verification_status', 'created_at')
    search_fields = ('name', 'description', 'long_description', 'tags', 'slug')
    readonly_fields = ('slug', 'success_score', 'created_at', 'updated_at', 'last_verified_at', 'views', 'enrichment_status')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug', 'website', 'image')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Pricing & Engagement', {
            'fields': ('pricing', 'views', 'upvotes', 'upvoted_by')
        }),
        ('SEO & Metadata', {
            'fields': ('seo_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Rich Content', {
            'fields': ('long_description', 'features', 'company_info', 'pricing_info', 'integrations', 'tech_stack', 'social_links'),
            'classes': ('collapse',),
            'description': 'Auto-extracted or manually enriched tool information'
        }),
        ('Content Details', {
            'fields': ('use_cases', 'pros', 'cons'),
            'classes': ('collapse',)
        }),
        ('Quality & Verification', {
            'fields': ('success_score', 'is_verified', 'verification_status', 'enrichment_status', 'last_verified_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['enrich_tools', 'verify_tools', 'generate_seo']
    
    def enrichment_status(self, obj):
        """Display enrichment completion status"""
        enriched_fields = sum([
            bool(obj.features),
            bool(obj.company_info),
            bool(obj.pricing_info),
            bool(obj.tech_stack),
        ])
        return f"{enriched_fields}/4 fields enriched"
    enrichment_status.short_description = "Enrichment Status"
    
    def enrich_tools(self, request, queryset):
        """Action to enrich selected tools from their websites"""
        enricher = ToolInfoEnricher()
        count = 0
        
        for tool in queryset:
            if not tool.website:
                continue
            
            try:
                info = enricher.extract_tool_info(tool.website)
                tool.long_description = info.get('description', '')
                tool.features = json.dumps(info.get('features', []))
                tool.pricing_info = json.dumps(info.get('pricing_info', {}))
                tool.company_info = json.dumps(info.get('company_info', {}))
                tool.integrations = ', '.join(info.get('integration_links', [])[:5])
                tool.tech_stack = ', '.join(info.get('tech_stack', [])[:10])
                tool.social_links = json.dumps(info.get('social_links', {}))
                tool.success_score = info.get('success_score', 0)
                tool.save()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error enriching {tool.name}: {e}', level='warning')
        
        self.message_user(request, f'✓ Enriched {count} tools')
    enrich_tools.short_description = "🔄 Enrich selected tools from their websites"
    
    def verify_tools(self, request, queryset):
        """Action to mark tools as verified"""
        updated = queryset.update(is_verified=True, verification_status='verified')
        self.message_user(request, f'✓ Verified {updated} tools')
    verify_tools.short_description = "✓ Mark selected as verified"
    
    def generate_seo(self, request, queryset):
        """Action to regenerate SEO fields"""
        count = 0
        
        for tool in queryset:
            try:
                tool.seo_title = f"{tool.name} - {tool.category}"
                tool.meta_description = SEOOptimizer.generate_meta_description(
                    tool.name, tool.category, json.loads(tool.features or '[]')
                )
                tool.meta_keywords = SEOOptimizer.generate_keywords(
                    tool.name, tool.category, tool.tags
                )
                tool.save()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error generating SEO for {tool.name}: {e}', level='warning')
        
        self.message_user(request, f'✓ Updated SEO for {count} tools')
    generate_seo.short_description = "📊 Regenerate SEO fields"