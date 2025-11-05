#!/usr/bin/env python3
"""
Wikipedia Mobile Article Creation Analysis
Analyzes articles created in the last 30 days using mobile web visual editor
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from collections import defaultdict

class WikipediaAnalyzer:
    def __init__(self):
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaMobileAnalysis/1.0 (Research Project)'
        })

    def get_available_tags(self) -> List[Dict[str, Any]]:
        """Fetch all available edit tags from Wikipedia"""
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'tags',
            'tglimit': 500,
            'tgprop': 'name|displayname|description|hitcount'
        }

        response = self.session.get(self.api_url, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers.get('content-type')}")

        if response.status_code != 200:
            print(f"Error response: {response.text[:500]}")
            return [], []

        try:
            data = response.json()
        except Exception as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text[:500]}")
            return [], []

        tags = data.get('query', {}).get('tags', [])
        print(f"\n=== Available Tags (Total: {len(tags)}) ===")

        mobile_ve_tags = []
        for tag in tags:
            tag_name = tag.get('name', '')
            # Look for mobile and visual editor related tags
            if 'mobile' in tag_name.lower() or 'visual' in tag_name.lower():
                print(f"  - {tag_name}: {tag.get('displayname', 'N/A')} (hits: {tag.get('hitcount', 0)})")
                mobile_ve_tags.append(tag)

        return tags, mobile_ve_tags

    def get_new_pages_with_tags(self, tags: List[str], days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch new pages created with specific tags in the last N days
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Format: 2025-10-06T00:00:00Z
        start_timestamp = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f"\n=== Searching for new articles created since {start_timestamp} ===")
        print(f"Looking for tags: {', '.join(tags)}")

        all_pages = []

        for tag in tags:
            print(f"\nQuerying tag: {tag}")
            continue_param = None
            page_count = 0

            while True:
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'recentchanges',
                    'rctype': 'new',  # Only new page creations
                    'rctag': tag,
                    'rcnamespace': 0,  # Main namespace (articles)
                    'rcstart': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'rcend': start_timestamp,
                    'rclimit': 500,
                    'rcprop': 'title|timestamp|ids|tags|user|userid|sizes|comment'
                }

                if continue_param:
                    params.update(continue_param)

                try:
                    response = self.session.get(self.api_url, params=params)
                    data = response.json()

                    pages = data.get('query', {}).get('recentchanges', [])
                    page_count += len(pages)
                    all_pages.extend(pages)

                    print(f"  Found {len(pages)} pages in this batch (total for this tag: {page_count})")

                    # Check if there are more results
                    if 'continue' not in data:
                        break

                    continue_param = data['continue']
                    time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    print(f"  Error querying tag {tag}: {e}")
                    break

        # Remove duplicates based on page ID
        unique_pages = {}
        for page in all_pages:
            page_id = page.get('pageid')
            if page_id not in unique_pages:
                unique_pages[page_id] = page

        result = list(unique_pages.values())
        print(f"\n=== Total unique articles found: {len(result)} ===")

        return result

    def get_page_revisions(self, page_title: str) -> List[Dict[str, Any]]:
        """
        Get complete revision history for a page
        """
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'titles': page_title,
            'rvprop': 'ids|timestamp|user|userid|size|tags|comment|content',
            'rvlimit': 500,
            'rvslots': 'main',
            'rvdir': 'newer'  # Oldest first
        }

        try:
            response = self.session.get(self.api_url, params=params)
            data = response.json()

            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if 'revisions' in page_data:
                    return page_data['revisions']

            return []
        except Exception as e:
            print(f"Error fetching revisions for {page_title}: {e}")
            return []

    def analyze_revision_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze the content structure of a revision
        """
        lines = content.split('\n')

        analysis = {
            'total_chars': len(content),
            'total_lines': len(lines),
            'sections': [],
            'has_infobox': False,
            'has_references': False,
            'has_categories': False,
            'has_images': False,
            'reference_count': 0,
            'category_count': 0,
            'image_count': 0,
            'external_links': 0,
            'template_count': 0,
            'lead_length': 0,
            'wikilinks_count': 0
        }

        current_section = None
        lead_section = []
        in_lead = True

        for line in lines:
            # Check for sections (headers)
            if line.strip().startswith('=='):
                in_lead = False
                # Count the number of '=' to determine level
                level = len(line) - len(line.lstrip('='))
                section_title = line.strip('= \t\n')
                analysis['sections'].append({
                    'title': section_title,
                    'level': level // 2  # Each level uses 2 '='
                })
            elif in_lead:
                lead_section.append(line)

            # Check for various Wikipedia elements
            if '{{Infobox' in line or '{{infobox' in line:
                analysis['has_infobox'] = True

            if '[[File:' in line or '[[Image:' in line:
                analysis['has_images'] = True
                analysis['image_count'] += line.count('[[File:') + line.count('[[Image:')

            if '[[Category:' in line:
                analysis['has_categories'] = True
                analysis['category_count'] += line.count('[[Category:')

            if '<ref' in line:
                analysis['has_references'] = True
                analysis['reference_count'] += line.count('<ref')

            if '{{' in line:
                analysis['template_count'] += line.count('{{')

            if '[[' in line:
                analysis['wikilinks_count'] += line.count('[[')

            if line.strip().startswith('*') and ('http://' in line or 'https://' in line):
                analysis['external_links'] += 1

        # Calculate lead section length
        analysis['lead_length'] = len('\n'.join(lead_section))

        return analysis

    def analyze_editing_pattern(self, revisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the editing pattern from revision history
        """
        if not revisions:
            return {}

        pattern = {
            'total_revisions': len(revisions),
            'revision_analyses': [],
            'first_revision': None,
            'progression': {
                'sections_added_order': [],
                'when_infobox_added': None,
                'when_references_added': None,
                'when_categories_added': None,
                'when_images_added': None
            }
        }

        for idx, rev in enumerate(revisions):
            content = rev.get('slots', {}).get('main', {}).get('*', '')

            analysis = self.analyze_revision_content(content)
            analysis['revision_number'] = idx + 1
            analysis['timestamp'] = rev.get('timestamp')
            analysis['user'] = rev.get('user')
            analysis['tags'] = rev.get('tags', [])
            analysis['comment'] = rev.get('comment', '')

            pattern['revision_analyses'].append(analysis)

            # Track when key elements were added
            if analysis['has_infobox'] and pattern['progression']['when_infobox_added'] is None:
                pattern['progression']['when_infobox_added'] = idx + 1

            if analysis['has_references'] and pattern['progression']['when_references_added'] is None:
                pattern['progression']['when_references_added'] = idx + 1

            if analysis['has_categories'] and pattern['progression']['when_categories_added'] is None:
                pattern['progression']['when_categories_added'] = idx + 1

            if analysis['has_images'] and pattern['progression']['when_images_added'] is None:
                pattern['progression']['when_images_added'] = idx + 1

            # Track section addition order
            if idx > 0:
                prev_sections = {s['title'] for s in pattern['revision_analyses'][idx-1]['sections']}
                curr_sections = {s['title'] for s in analysis['sections']}
                new_sections = curr_sections - prev_sections

                for section in new_sections:
                    pattern['progression']['sections_added_order'].append({
                        'section': section,
                        'revision': idx + 1
                    })

        if pattern['revision_analyses']:
            pattern['first_revision'] = pattern['revision_analyses'][0]

        return pattern

def main():
    analyzer = WikipediaAnalyzer()

    print("=" * 80)
    print("WIKIPEDIA MOBILE ARTICLE CREATION ANALYSIS")
    print("Analyzing articles created via mobile web visual editor (last 30 days)")
    print("=" * 80)

    # Step 1: Get available tags
    all_tags, mobile_ve_tags = analyzer.get_available_tags()

    # Step 2: Identify the right tags to use
    # Common tag names based on research:
    tags_to_search = [
        'mobile web edit',
        'mobile edit',
        'visualeditor',
        'visualeditor-wikitext'
    ]

    print(f"\n=== Tag Search Configuration ===")
    print(f"Will search for combinations of: {tags_to_search}")

    # Step 3: Fetch new pages with these tags
    new_pages = analyzer.get_new_pages_with_tags(tags_to_search, days=30)

    # Filter for pages that have BOTH mobile and visual editor tags
    mobile_ve_pages = []
    for page in new_pages:
        page_tags = page.get('tags', [])
        has_mobile = any('mobile' in tag.lower() for tag in page_tags)
        has_ve = any('visual' in tag.lower() for tag in page_tags)

        if has_mobile and has_ve:
            mobile_ve_pages.append(page)

    print(f"\n=== Filtered Results ===")
    print(f"Articles with BOTH mobile AND visual editor tags: {len(mobile_ve_pages)}")

    # Save initial results
    with open('mobile_ve_articles.json', 'w', encoding='utf-8') as f:
        json.dump(mobile_ve_pages, f, indent=2, ensure_ascii=False)

    print(f"\nSaved article list to: mobile_ve_articles.json")

    # Step 4: Analyze each article's editing pattern
    print(f"\n{'=' * 80}")
    print("DETAILED ARTICLE ANALYSIS")
    print(f"{'=' * 80}")

    detailed_analyses = []

    for idx, page in enumerate(mobile_ve_pages[:50], 1):  # Limit to first 50 for now
        title = page.get('title')
        print(f"\n[{idx}/{min(len(mobile_ve_pages), 50)}] Analyzing: {title}")

        revisions = analyzer.get_page_revisions(title)

        if revisions:
            pattern = analyzer.analyze_editing_pattern(revisions)

            detailed_analyses.append({
                'title': title,
                'page_id': page.get('pageid'),
                'created': page.get('timestamp'),
                'creator': page.get('user'),
                'initial_tags': page.get('tags', []),
                'editing_pattern': pattern
            })

            print(f"  - Total revisions: {pattern['total_revisions']}")
            if pattern.get('first_revision'):
                first = pattern['first_revision']
                print(f"  - First revision: {first['total_chars']} chars, {len(first['sections'])} sections")
                print(f"  - Started with: {'Lead section' if first['lead_length'] > 0 else 'No lead'}")

        time.sleep(0.5)  # Rate limiting

    # Save detailed analysis
    with open('mobile_ve_detailed_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_analyses, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print(f"Saved detailed analysis to: mobile_ve_detailed_analysis.json")
    print(f"{'=' * 80}")

    return detailed_analyses, mobile_ve_pages

if __name__ == "__main__":
    main()
