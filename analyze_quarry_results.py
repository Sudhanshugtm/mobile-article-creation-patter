#!/usr/bin/env python3
"""
Analyze Quarry Query Results for Mobile Visual Editor Article Creation Patterns
This script processes CSV exports from Quarry queries to identify editing patterns
"""

import pandas as pd
import json
from datetime import datetime
from collections import defaultdict, Counter
import glob
import os

class MobileArticlePatternAnalyzer:
    """Analyzes patterns in mobile visual editor article creation"""

    def __init__(self):
        self.articles = []
        self.patterns = defaultdict(list)

    def load_article_list(self, csv_path):
        """Load the list of mobile VE created articles from Quarry export"""
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} articles from {csv_path}")
            print(f"Columns: {df.columns.tolist()}")

            self.articles = df.to_dict('records')
            return df
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            return None

    def load_revision_history(self, csv_path):
        """Load revision history for an article from Quarry export"""
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error loading {csv_path}: {e}")
            return None

    def analyze_first_revision_patterns(self, articles_df):
        """Analyze patterns in how articles are initially created"""

        print("\n" + "="*80)
        print("FIRST REVISION PATTERNS ANALYSIS")
        print("="*80)

        patterns = {
            'length_distribution': [],
            'by_hour_of_day': defaultdict(int),
            'by_day_of_week': defaultdict(int),
            'unique_creators': set(),
            'articles_per_creator': Counter()
        }

        for article in articles_df.to_dict('records'):
            # Length distribution
            if 'initial_length' in article:
                patterns['length_distribution'].append(article['initial_length'])

            # Creator statistics
            if 'creator' in article:
                creator = article['creator']
                patterns['unique_creators'].add(creator)
                patterns['articles_per_creator'][creator] += 1

            # Time patterns
            if 'creation_timestamp' in article:
                try:
                    timestamp = pd.to_datetime(article['creation_timestamp'])
                    patterns['by_hour_of_day'][timestamp.hour] += 1
                    patterns['by_day_of_week'][timestamp.day_name()] += 1
                except:
                    pass

        # Calculate statistics
        lengths = patterns['length_distribution']

        print(f"\n📊 INITIAL ARTICLE LENGTH STATISTICS")
        print(f"   Total articles analyzed: {len(lengths)}")
        if lengths:
            print(f"   Average length: {sum(lengths)/len(lengths):.0f} bytes")
            print(f"   Median length: {sorted(lengths)[len(lengths)//2]:.0f} bytes")
            print(f"   Min length: {min(lengths)} bytes")
            print(f"   Max length: {max(lengths)} bytes")

            # Categorize by length
            very_short = len([l for l in lengths if l < 500])
            short = len([l for l in lengths if 500 <= l < 2000])
            medium = len([l for l in lengths if 2000 <= l < 5000])
            long = len([l for l in lengths if l >= 5000])

            print(f"\n   Length Categories:")
            print(f"   - Very short (<500 bytes): {very_short} ({very_short/len(lengths)*100:.1f}%)")
            print(f"   - Short (500-2000 bytes): {short} ({short/len(lengths)*100:.1f}%)")
            print(f"   - Medium (2000-5000 bytes): {medium} ({medium/len(lengths)*100:.1f}%)")
            print(f"   - Long (>5000 bytes): {long} ({long/len(lengths)*100:.1f}%)")

        print(f"\n👥 CREATOR STATISTICS")
        print(f"   Unique creators: {len(patterns['unique_creators'])}")
        print(f"   Articles per creator (avg): {len(articles_df)/len(patterns['unique_creators']):.2f}")

        # Top creators
        print(f"\n   Top 10 Most Active Creators:")
        for idx, (creator, count) in enumerate(patterns['articles_per_creator'].most_common(10), 1):
            print(f"   {idx}. {creator}: {count} articles")

        # Time patterns
        print(f"\n⏰ CREATION TIME PATTERNS")
        print(f"\n   By Hour of Day:")
        for hour in sorted(patterns['by_hour_of_day'].keys()):
            count = patterns['by_hour_of_day'][hour]
            bar = '█' * (count // max(1, max(patterns['by_hour_of_day'].values()) // 20))
            print(f"   {hour:02d}:00 - {count:3d} {bar}")

        print(f"\n   By Day of Week:")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in day_order:
            if day in patterns['by_day_of_week']:
                count = patterns['by_day_of_week'][day]
                bar = '█' * (count // max(1, max(patterns['by_day_of_week'].values()) // 20))
                print(f"   {day:10s}: {count:3d} {bar}")

        return patterns

    def analyze_revision_progression(self, revision_df, article_title):
        """Analyze how an article evolved through revisions"""

        print(f"\n" + "="*80)
        print(f"REVISION PROGRESSION: {article_title}")
        print("="*80)

        if revision_df is None or len(revision_df) == 0:
            print("No revision data available")
            return None

        revisions = revision_df.to_dict('records')

        print(f"\nTotal revisions: {len(revisions)}")
        print(f"First revision: {revisions[0].get('rev_timestamp', 'N/A')}")
        print(f"Latest revision: {revisions[-1].get('rev_timestamp', 'N/A')}")

        # Analyze length growth
        print(f"\n📈 ARTICLE GROWTH")
        for idx, rev in enumerate(revisions[:10], 1):  # First 10 revisions
            length = rev.get('rev_len', 0)
            user = rev.get('rev_user_text', 'Unknown')
            timestamp = rev.get('rev_timestamp', 'N/A')
            tags = rev.get('tags', '')

            # Calculate growth
            if idx == 1:
                growth = length
            else:
                prev_length = revisions[idx-2].get('rev_len', 0)
                growth = length - prev_length

            growth_str = f"+{growth}" if growth >= 0 else str(growth)
            mobile_indicator = "📱" if 'mobile' in str(tags).lower() else "🖥️"
            ve_indicator = "✏️" if 'visual' in str(tags).lower() else "📝"

            print(f"   Rev {idx}: {length:5d} bytes ({growth_str:+6s}) {mobile_indicator}{ve_indicator} by {user}")

        if len(revisions) > 10:
            print(f"   ... ({len(revisions) - 10} more revisions)")

        # Tag analysis
        print(f"\n🏷️  EDITING PLATFORM USAGE")
        mobile_count = 0
        desktop_count = 0
        ve_count = 0
        source_count = 0

        for rev in revisions:
            tags = str(rev.get('tags', '')).lower()
            if 'mobile' in tags:
                mobile_count += 1
            else:
                desktop_count += 1

            if 'visual' in tags:
                ve_count += 1
            else:
                source_count += 1

        print(f"   Mobile edits: {mobile_count} ({mobile_count/len(revisions)*100:.1f}%)")
        print(f"   Desktop edits: {desktop_count} ({desktop_count/len(revisions)*100:.1f}%)")
        print(f"   Visual editor: {ve_count} ({ve_count/len(revisions)*100:.1f}%)")
        print(f"   Source editor: {source_count} ({source_count/len(revisions)*100:.1f}%)")

        # Unique contributors
        contributors = set(rev.get('rev_user_text', '') for rev in revisions)
        print(f"\n   Unique contributors: {len(contributors)}")
        if len(contributors) > 1:
            print(f"   Collaboration detected! Multiple editors worked on this article.")

        return {
            'total_revisions': len(revisions),
            'mobile_edits': mobile_count,
            'desktop_edits': desktop_count,
            've_edits': ve_count,
            'source_edits': source_count,
            'unique_contributors': len(contributors)
        }

    def generate_report(self, articles_df, output_path='analysis_report.md'):
        """Generate a comprehensive markdown report"""

        report = []
        report.append("# Mobile Visual Editor Article Creation Analysis Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("="*80 + "\n")

        report.append("## Executive Summary\n")
        report.append(f"- Total articles analyzed: {len(articles_df)}")
        report.append(f"- Date range: Last 30 days")
        report.append(f"- Platform: Mobile Web Visual Editor\n")

        # Add patterns
        patterns = self.analyze_first_revision_patterns(articles_df)

        report.append("\n## Key Findings\n")

        if patterns['length_distribution']:
            avg_length = sum(patterns['length_distribution']) / len(patterns['length_distribution'])
            report.append(f"### Initial Article Length")
            report.append(f"- Average: {avg_length:.0f} bytes")
            report.append(f"- This indicates that mobile VE articles typically start ")

            if avg_length < 500:
                report.append(f"as **stubs** - very short articles that need expansion.\n")
            elif avg_length < 2000:
                report.append(f"as **short articles** - basic but incomplete coverage.\n")
            else:
                report.append(f"as **substantial articles** - relatively complete from the start.\n")

        report.append(f"\n### Creator Behavior")
        report.append(f"- {len(patterns['unique_creators'])} unique creators")

        # Check if there are power users
        top_creator_count = patterns['articles_per_creator'].most_common(1)[0][1] if patterns['articles_per_creator'] else 0
        if top_creator_count > 5:
            report.append(f"- Power users detected: Some creators made {top_creator_count}+ articles")
            report.append(f"- This suggests experienced mobile editors are comfortable creating articles\n")
        else:
            report.append(f"- Most creators made only 1-2 articles")
            report.append(f"- This suggests mobile article creation may be used by newcomers\n")

        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))

        print(f"\n📄 Report saved to: {output_path}")

        return '\n'.join(report)


def main():
    print("="*80)
    print("MOBILE VISUAL EDITOR ARTICLE PATTERN ANALYZER")
    print("="*80)

    analyzer = MobileArticlePatternAnalyzer()

    # Look for CSV files from Quarry exports
    csv_files = glob.glob('*.csv')

    if not csv_files:
        print("\n⚠️  No CSV files found in current directory")
        print("\nPlease export query results from Quarry as CSV files and place them here.")
        print("\nExpected files:")
        print("  - articles_list.csv (from Query 1 or 5)")
        print("  - article_revisions_*.csv (from Query 3 for each article)")
        return

    print(f"\nFound {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f}")

    # Load main articles list
    articles_file = None
    for f in csv_files:
        if 'article' in f.lower() and 'revision' not in f.lower():
            articles_file = f
            break

    if not articles_file and csv_files:
        articles_file = csv_files[0]

    if articles_file:
        print(f"\n📂 Loading articles from: {articles_file}")
        articles_df = analyzer.load_article_list(articles_file)

        if articles_df is not None:
            # Analyze patterns
            patterns = analyzer.analyze_first_revision_patterns(articles_df)

            # Generate report
            analyzer.generate_report(articles_df)

            # Look for revision history files
            revision_files = [f for f in csv_files if 'revision' in f.lower()]

            if revision_files:
                print(f"\n\nFound {len(revision_files)} revision history files")

                for rev_file in revision_files[:5]:  # Analyze first 5
                    rev_df = analyzer.load_revision_history(rev_file)
                    if rev_df is not None:
                        article_title = os.path.splitext(rev_file)[0].replace('revisions_', '')
                        analyzer.analyze_revision_progression(rev_df, article_title)
    else:
        print("\n⚠️  Could not identify main articles CSV file")


if __name__ == "__main__":
    main()
