from django.core.management.base import BaseCommand
from tools.models import Tool
from tools.tool_enricher import ToolInfoEnricher, SEOOptimizer, ToolCategoryOptimizer
import json
import csv


class Command(BaseCommand):
    help = 'Import AI tools from CSV or URL with auto-enrichment'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='CSV file path to import from')
        parser.add_argument('--url', type=str, help='Website URL to enrich and add')
        parser.add_argument('--auto-enrich', action='store_true', help='Auto-extract tool information')
        parser.add_argument('--sample', action='store_true', help='Import sample AI tools')

    def handle(self, *args, **options):
        if options['file']:
            self.import_from_csv(options['file'], options['auto_enrich'])
        elif options['url']:
            self.import_single_tool(options['url'], options['auto_enrich'])
        elif options['sample']:
            self.import_sample_tools()
        else:
            self.stdout.write(self.style.ERROR('Use --file, --url, or --sample'))

    def import_from_csv(self, file_path, auto_enrich=False):
        """Import tools from CSV file"""
        enricher = ToolInfoEnricher() if auto_enrich else None
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if self.create_tool_from_row(row, enricher):
                        count += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ Imported {count} tools successfully'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))

    def create_tool_from_row(self, row, enricher=None):
        """Create tool from CSV row"""
        name = row.get('name', '').strip()
        website = row.get('website', '').strip()
        
        if not name:
            return False
        
        tool_data = {
            'name': name,
            'description': row.get('description', '').strip(),
            'website': website,
            'category': row.get('category', 'AI Tools').strip(),
            'tags': row.get('tags', '').strip(),
            'pricing': row.get('pricing', 'Free').strip(),
        }
        
        # Auto-enrich from website
        if enricher and website:
            try:
                enriched = enricher.extract_tool_info(website)
                tool_data.update({
                    'long_description': enriched.get('description', ''),
                    'features': json.dumps(enriched.get('features', [])),
                    'pricing_info': json.dumps(enriched.get('pricing_info', {})),
                    'company_info': json.dumps(enriched.get('company_info', {})),
                    'integrations': ', '.join(enriched.get('integration_links', [])[:5]),
                    'tech_stack': ', '.join(enriched.get('tech_stack', [])[:10]),
                    'social_links': json.dumps(enriched.get('social_links', {})),
                    'success_score': enriched.get('success_score', 0),
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Could not enrich {name}: {str(e)[:50]}'))
        
        # Generate SEO fields
        tool_data.update({
            'slug': SEOOptimizer.generate_slug(name),
            'meta_description': SEOOptimizer.generate_meta_description(
                name, tool_data['category'], json.loads(tool_data.get('features', '[]'))
            ),
            'meta_keywords': SEOOptimizer.generate_keywords(
                name, tool_data['category'], tool_data['tags']
            ),
            'seo_title': f"{name} - {tool_data['category']}"
        })
        
        # Auto-suggest category
        if tool_data['category'] == 'AI Tools' and tool_data['description']:
            suggested = ToolCategoryOptimizer.suggest_categories(tool_data['description'], name)
            if suggested:
                tool_data['category'] = suggested[0]
        
        # Auto-generate tags
        if not tool_data['tags']:
            tool_data['tags'] = ToolCategoryOptimizer.suggest_tags(tool_data['description'], tool_data['category'])
        
        # Save to database
        try:
            tool, created = Tool.objects.update_or_create(
                slug=tool_data['slug'],
                defaults=tool_data
            )
            status = '✓ Created' if created else '◉ Updated'
            self.stdout.write(f'{status}: {name}')
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error saving {name}: {e}'))
            return False

    def import_single_tool(self, url, auto_enrich=False):
        """Import a single tool by URL"""
        enricher = ToolInfoEnricher() if auto_enrich else None
        
        # Create basic tool entry
        name = input('Enter tool name: ').strip()
        
        tool_data = {
            'name': name,
            'website': url,
            'description': input('Enter description: ').strip(),
            'category': input('Enter category (default: AI Tools): ').strip() or 'AI Tools',
            'tags': input('Enter tags (comma-separated): ').strip(),
            'pricing': input('Enter pricing (Free/Premium/Freemium): ').strip() or 'Free',
        }
        
        if enricher:
            try:
                enriched = enricher.extract_tool_info(url)
                tool_data.update({
                    'long_description': enriched.get('description', ''),
                    'features': json.dumps(enriched.get('features', [])),
                    'pricing_info': json.dumps(enriched.get('pricing_info', {})),
                    'company_info': json.dumps(enriched.get('company_info', {})),
                    'integrations': ', '.join(enriched.get('integration_links', [])[:5]),
                    'tech_stack': ', '.join(enriched.get('tech_stack', [])[:10]),
                    'social_links': json.dumps(enriched.get('social_links', {})),
                    'success_score': enriched.get('success_score', 0),
                })
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Enrichment failed: {e}'))
        
        # Generate SEO
        tool_data.update({
            'slug': SEOOptimizer.generate_slug(name),
            'meta_description': SEOOptimizer.generate_meta_description(
                name, tool_data['category'], json.loads(tool_data.get('features', '[]'))
            ),
            'meta_keywords': SEOOptimizer.generate_keywords(
                name, tool_data['category'], tool_data['tags']
            ),
            'seo_title': f"{name} - {tool_data['category']}"
        })
        
        tool, created = Tool.objects.update_or_create(
            slug=tool_data['slug'],
            defaults=tool_data
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Tool saved: {tool.name}'))

    def import_sample_tools(self):
        """Import sample AI tools for demo"""
        samples = [
            {
                'name': 'ChatGPT',
                'description': 'AI chatbot by OpenAI for conversations, writing, coding, and analysis',
                'website': 'https://chat.openai.com',
                'category': 'Generative AI',
                'tags': 'ChatBot, GPT-4, AI Assistant',
                'pricing': 'Freemium'
            },
            {
                'name': 'Midjourney',
                'description': 'AI image generation creating stunning visuals from text prompts',
                'website': 'https://www.midjourney.com',
                'category': 'Image Generation',
                'tags': 'Image Generation, AI Art, Design',
                'pricing': 'Premium'
            },
            {
                'name': 'Notion AI',
                'description': 'Integrated AI within Notion workspace for productivity automation',
                'website': 'https://notion.so',
                'category': 'Productivity',
                'tags': 'Productivity, Note-taking, Database',
                'pricing': 'Freemium'
            },
        ]
        
        for tool_dict in samples:
            tool_data = tool_dict.copy()
            tool_data.update({
                'slug': SEOOptimizer.generate_slug(tool_dict['name']),
                'meta_description': SEOOptimizer.generate_meta_description(
                    tool_dict['name'], tool_dict['category'], []
                ),
                'meta_keywords': SEOOptimizer.generate_keywords(
                    tool_dict['name'], tool_dict['category'], tool_dict['tags']
                ),
                'seo_title': f"{tool_dict['name']} - {tool_dict['category']}"
            })
            
            tool, created = Tool.objects.update_or_create(
                slug=tool_data['slug'],
                defaults=tool_data
            )
            self.stdout.write(f'{"✓ Created" if created else "◉ Updated"}: {tool.name}')
        
        self.stdout.write(self.style.SUCCESS('✓ Sample tools imported'))