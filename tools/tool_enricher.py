"""
AI Tool Information Auto-Detection & Enrichment System
Automatically gathers and enriches tool information for better SEO and user experience
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import re
from typing import Dict, List, Optional


class ToolInfoEnricher:
    """Automatically enriches tool information from URLs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_tool_info(self, url: str) -> Dict:
        """
        Extract comprehensive tool information from URL
        Returns dict with: description, features, pricing_details, etc.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            info = {
                'description': self._get_description(soup),
                'features': self._get_features(soup),
                'pricing_info': self._get_pricing(soup),
                'company_info': self._get_company_info(soup),
                'tech_stack': self._get_tech_stack(soup),
                'integration_links': self._get_integrations(soup),
                'social_links': self._get_social_links(soup),
                'success_score': self._calculate_success_score(soup),
            }
            return info
        except Exception as e:
            print(f"Error extracting info from {url}: {e}")
            return {}
    
    def _get_description(self, soup) -> str:
        """Extract primary description"""
        descriptions = []
        
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            descriptions.append(meta_desc['content'])
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            descriptions.append(og_desc['content'])
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            descriptions.append(first_p.get_text().strip())
        
        # Return longest description
        return max(descriptions, key=len) if descriptions else ""
    
    def _get_features(self, soup) -> List[str]:
        """Extract key features"""
        features = []
        
        # Look for common feature indicators
        feature_keywords = [
            'Features', 'Capabilities', 'Benefits', 'What You Can Do',
            'How It Works', 'Features & Benefits'
        ]
        
        for keyword in feature_keywords:
            section = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if section:
                parent = section.parent
                # Get list items after this section
                lists = parent.find_all(['ul', 'ol'], limit=2)
                for ul in lists:
                    items = ul.find_all('li')
                    for li in items[:5]:  # Max 5 features
                        text = li.get_text().strip()
                        if text and len(text) < 100:
                            features.append(text)
        
        return features[:5]
    
    def _get_pricing(self, soup) -> Dict:
        """Extract pricing information"""
        pricing_info = {
            'has_free_tier': False,
            'has_premium': False,
            'has_enterprise': False,
            'pricing_range': None,
        }
        
        page_text = soup.get_text().lower()
        
        if 'free' in page_text:
            pricing_info['has_free_tier'] = True
        if 'premium' in page_text or 'pro' in page_text:
            pricing_info['has_premium'] = True
        if 'enterprise' in page_text or 'business' in page_text:
            pricing_info['has_enterprise'] = True
        
        # Extract price ranges if found
        prices = re.findall(r'\$[\d,]+(?:\.\d{2})?(?:/\w+)?', page_text)
        if prices:
            pricing_info['pricing_range'] = prices[0]
        
        return pricing_info
    
    def _get_company_info(self, soup) -> Dict:
        """Extract company information"""
        company_info = {
            'name': '',
            'founded': '',
            'location': '',
            'team_size': '',
        }
        
        # Try to get company name from title or header
        title = soup.find('title')
        if title:
            company_info['name'] = title.get_text().strip()
        
        # Look for company details in common locations
        about_section = soup.find(string=re.compile('About', re.IGNORECASE))
        if about_section:
            text = about_section.parent.get_text()
            
            # Look for founded year
            founded_match = re.search(r'founded (\d{4})', text, re.IGNORECASE)
            if founded_match:
                company_info['founded'] = founded_match.group(1)
            
            # Look for location
            location_match = re.search(r'(?:based in|located in|from) ([^,\n]+)', text, re.IGNORECASE)
            if location_match:
                company_info['location'] = location_match.group(1).strip()
        
        return company_info
    
    def _get_tech_stack(self, soup) -> List[str]:
        """Detect technology stack"""
        tech_stack = []
        page_source = str(soup)
        
        # Common tech indicators
        tech_indicators = {
            'React': ['react.js', 'react/'],
            'Vue': ['vue.js', 'vue/'],
            'Angular': ['angular.js', 'angularjs'],
            'Node.js': ['nodejs', 'node.js'],
            'Python': ['python', 'django', 'flask'],
            'GraphQL': ['graphql'],
            'REST API': ['api/rest', '/api/'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'Docker': ['docker'],
        }
        
        for tech, indicators in tech_indicators.items():
            if any(indicator in page_source.lower() for indicator in indicators):
                tech_stack.append(tech)
        
        return tech_stack
    
    def _get_integrations(self, soup) -> List[str]:
        """Extract integration information"""
        integrations = []
        
        integration_section = soup.find(string=re.compile('Integrations|API', re.IGNORECASE))
        if integration_section:
            parent = integration_section.parent
            # Find all links in integration section
            links = parent.find_all('a', limit=10)
            for link in links:
                text = link.get_text().strip()
                if text and len(text) < 50:
                    integrations.append(text)
        
        return integrations[:5]
    
    def _get_social_links(self, soup) -> Dict:
        """Extract social media links"""
        social_links = {
            'twitter': '',
            'linkedin': '',
            'github': '',
            'facebook': '',
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if 'twitter.com' in href:
                social_links['twitter'] = link['href']
            elif 'linkedin.com' in href:
                social_links['linkedin'] = link['href']
            elif 'github.com' in href:
                social_links['github'] = link['href']
            elif 'facebook.com' in href:
                social_links['facebook'] = link['href']
        
        return {k: v for k, v in social_links.items() if v}
    
    def _calculate_success_score(self, soup) -> int:
        """
        Calculate tool quality score (0-100) based on available information
        """
        score = 0
        
        # Check for SSL certificate indication
        if 'https' in str(soup):
            score += 10
        
        # Check for professional design indicators
        if soup.find('meta', attrs={'name': 'viewport'}):
            score += 10
        
        # Check for social proof
        if soup.find(string=re.compile('trusted|secure|verified', re.IGNORECASE)):
            score += 10
        
        # Check for clear call-to-action
        if soup.find(string=re.compile('sign up|get started|try free', re.IGNORECASE)):
            score += 10
        
        # Check for documentation
        if soup.find(string=re.compile('documentation|api docs|guide', re.IGNORECASE)):
            score += 10
        
        # Check for company info
        if soup.find(string=re.compile('about|contact|team', re.IGNORECASE)):
            score += 10
        
        # Check for testimonials/reviews
        if soup.find(string=re.compile('testimonial|review|case study', re.IGNORECASE)):
            score += 10
        
        # Check for security badges
        if soup.find(string=re.compile('certified|secure|gdpr|sso', re.IGNORECASE)):
            score += 10
        
        # Check for active development indicators
        if soup.find(string=re.compile('recently|new|updated', re.IGNORECASE)):
            score += 10
        
        return min(score, 100)


class SEOOptimizer:
    """Optimize tool listings for search engines"""
    
    @staticmethod
    def generate_meta_description(tool_name: str, category: str, features: List[str]) -> str:
        """Generate SEO-optimized meta description"""
        feature_text = ', '.join(features[:2]) if features else category
        description = f"{tool_name} - {category} tool for {feature_text}. Explore features, pricing, and reviews."
        return description[:160]  # Meta descriptions should be under 160 chars
    
    @staticmethod
    def generate_keywords(tool_name: str, category: str, tags: str = "") -> str:
        """Generate SEO-optimized keywords"""
        keywords = [
            tool_name.lower(),
            category.lower(),
            f"{category} AI tool",
            f"best {category.lower()} tool",
            "AI tools",
        ]
        
        if tags:
            keywords.extend(tags.lower().split(','))
        
        return ', '.join(keywords[:10])
    
    @staticmethod
    def generate_slug(tool_name: str) -> str:
        """Generate URL-friendly slug"""
        slug = tool_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    @staticmethod
    def generate_schema_markup(tool: 'Tool') -> Dict:
        """Generate JSON-LD schema markup for better SEO"""
        schema = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": tool.name,
            "description": tool.description[:200],
            "applicationCategory": "BusinessApplication",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": min(5, (tool.upvotes / 100) + 3),
                "reviewCount": tool.upvotes
            }
        }
        
        if tool.image:
            schema["image"] = tool.image.url
        
        if tool.website:
            schema["url"] = tool.website
        
        return schema


class ToolCategoryOptimizer:
    """Optimize tool categorization for better discovery"""
    
    CATEGORY_KEYWORDS = {
        'Generative AI': ['chatgpt', 'gpt', 'text generation', 'llm', 'language model'],
        'Image Generation': ['image', 'picture', 'visual', 'art', 'design', 'dall-e', 'midjourney'],
        'Video Generation': ['video', 'video creation', 'animation', 'motion'],
        'Copywriting': ['writing', 'content', 'copy', 'article', 'blog'],
        'Data Analysis': ['data', 'analytics', 'business intelligence', 'dashboard'],
        'Machine Learning': ['ml', 'model', 'prediction', 'classification'],
        'API Development': ['api', 'integration', 'webhook', 'rest'],
    }
    
    @staticmethod
    def suggest_categories(description: str, name: str) -> List[str]:
        """Suggest categories based on tool description"""
        text = f"{name} {description}".lower()
        suggested = []
        
        for category, keywords in ToolCategoryOptimizer.CATEGORY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                suggested.append(category)
        
        return suggested[:3]
    
    @staticmethod
    def suggest_tags(description: str, category: str) -> str:
        """Suggest relevant tags"""
        base_tags = [
            'AI', 'automation', 'productivity', 'SaaS',
            'free', 'paid', 'open-source'
        ]
        
        tags = []
        
        # Category-specific tags
        if 'data' in category.lower():
            tags.extend(['data', 'analytics', 'business-intelligence'])
        elif 'image' in category.lower():
            tags.extend(['image', 'design', 'visual', 'creative'])
        elif 'video' in category.lower():
            tags.extend(['video', 'media', 'production'])
        elif 'writing' in category.lower():
            tags.extend(['writing', 'content', 'copywriting'])
        
        # Description-based tags
        if 'free' in description.lower():
            tags.append('free')
        if 'api' in description.lower():
            tags.append('api')
        if 'open source' in description.lower():
            tags.append('open-source')
        
        return ', '.join(base_tags + tags)[:200]
