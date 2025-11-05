# Wikipedia Mobile Article Creation Pattern Analysis

**Comprehensive research into articles created using Mobile Web Visual Editor**

## 🎯 Project Overview

This repository contains tools, queries, and findings for analyzing Wikipedia articles created using the mobile web visual editor over the last 30 days. The goal is to understand editing patterns to build a better mobile editing experience.

### What You'll Find Here

1. **SQL Queries** - Ready-to-run Quarry queries to fetch mobile VE article data
2. **Analysis Scripts** - Python tools to analyze the data and identify patterns
3. **Research Findings** - Comprehensive report with verified statistics and actionable recommendations
4. **Methodology** - Fully documented, reproducible research process

## 📊 Key Findings Summary

Based on verified Wikimedia Foundation research (2025):

- **95% abandonment rate** - Mobile users open editor but don't complete edits
- **8.44% reversion rate** - IP mobile VE edits vs 0.57% for desktop
- **11-13% mobile share** - Of all Wikipedia edits despite majority mobile readership
- **Huge opportunity** - Mobile represents largest untapped contributor potential

**Full details**: See [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md)

## 🚀 Quick Start

### Option 1: Run Quarry Queries (Recommended)

1. Go to https://quarry.wmcloud.org/
2. Create account (Wikimedia login)
3. Open `quarry_queries.sql` in this repo
4. Copy **Query 1** (Find mobile VE articles)
5. Select database: `enwiki_p` (English Wikipedia)
6. Run query
7. Export results as CSV
8. Repeat for other queries as needed

### Option 2: Analyze Existing Data

If you have CSV exports from Quarry:

```bash
# Place CSV files in this directory
# Then run:
python3 analyze_quarry_results.py
```

This will generate:
- Console output with statistics
- `analysis_report.md` with detailed findings

### Option 3: Direct API (if accessible)

```bash
# Requires Wikipedia API access
python3 wikipedia_mobile_analysis.py
```

Note: API access may be restricted in some environments.

## 📁 Repository Structure

```
mobile-article-creation-patter/
│
├── README.md                          # This file
├── RESEARCH_FINDINGS.md               # Comprehensive research report
│
├── quarry_queries.sql                 # SQL queries for Wikimedia Quarry
├── wikipedia_mobile_analysis.py       # Direct API analysis script
├── analyze_quarry_results.py          # Analyze CSV data from Quarry
│
└── (data files - generated)
    ├── mobile_ve_articles.json        # Article list
    ├── mobile_ve_detailed_analysis.json
    └── *.csv                          # Quarry exports
```

## 🔍 Detailed Methodology

### Research Questions

1. **Which articles** were created using mobile web visual editor in last 30 days?
2. **How did they start** - lead section first? Sections? Structure?
3. **What patterns emerge** - content length, section order, element usage?
4. **How do they evolve** - single session or multiple revisions?
5. **What works well** - which articles succeed vs get deleted/reverted?

### Data Collection Process

#### Step 1: Identify Articles

**Criteria**:
- Created in last 30 days
- Main namespace (actual articles, not talk pages)
- Tagged with BOTH:
  - Mobile tag (`mobile edit` or `mobile web edit`)
  - Visual Editor tag (`visualeditor` or `visualeditor-wikitext`)

**Query**: See `Query 1` in `quarry_queries.sql`

#### Step 2: Get Revision Histories

For each identified article, fetch:
- All revisions (oldest to newest)
- Revision metadata (timestamp, user, tags, comment)
- Revision content (wikitext)

**Query**: See `Query 3` in `quarry_queries.sql`

#### Step 3: Analyze Patterns

For each article, analyze:

**First Revision**:
- Character count
- Has lead paragraph?
- Section structure
- Infobox present?
- References present?
- Images present?
- Categories present?
- Wikilinks count
- Template count

**Revision Progression**:
- When was infobox added? (revision #)
- When were references added?
- When were sections added? (order)
- Mobile vs desktop edits
- Single creator vs collaborative

**Aggregate Patterns**:
- Common initial lengths
- Common section orders
- Common starting approaches
- Success factors (articles that survive vs deleted)

#### Step 4: Statistical Analysis

- Average/median initial article length
- Distribution of revision counts
- Time-of-day patterns
- Creator behavior (one-time vs repeat)
- Collaboration patterns

### Verification Standards

All claims in this research are:

✅ **Cited** - Sources provided for all statistics
✅ **Reproducible** - Queries and methods fully documented
✅ **Verifiable** - Official Wikimedia sources only
✅ **Transparent** - Hypotheses clearly labeled as such

## 📈 Analysis Tools

### quarry_queries.sql

Six comprehensive SQL queries:

1. **Find mobile VE articles** - Last 30 days, with tags
2. **Get available tags** - Identify exact tag names in use
3. **Revision history** - Complete history for specific article
4. **Statistics** - Aggregate data by date
5. **Articles with revision counts** - Growth patterns
6. **User contribution patterns** - Creator behavior

### analyze_quarry_results.py

Python analysis script features:

- **Load CSV exports** from Quarry
- **First revision analysis** - Length, structure, patterns
- **Time pattern detection** - Hour of day, day of week
- **Creator statistics** - Power users, one-time creators
- **Revision progression** - How articles evolve
- **Platform usage** - Mobile vs desktop, VE vs source
- **Report generation** - Markdown formatted findings

**Usage**:
```bash
python3 analyze_quarry_results.py

# Looks for CSV files in current directory
# Generates analysis_report.md
```

### wikipedia_mobile_analysis.py

Direct Wikipedia API script (when API accessible):

- **Tag discovery** - Find all available edit tags
- **Article search** - Query by tags and date
- **Revision fetching** - Complete histories
- **Content analysis** - Parse wikitext structure
- **Pattern detection** - Automated pattern recognition

## 📚 Research Findings

See [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md) for full report including:

### Current State
- Mobile editing landscape
- Platform distribution statistics
- Abandonment funnel analysis

### Editing Patterns (Verified & Hypothesized)
- Lead section priority pattern
- Plain text first, formatting later
- Start small, expand later
- Collaborative completion
- Time-of-day patterns
- Topic patterns

### Pain Points
- Interface complexity
- Citation/reference difficulty
- Multitasking barriers
- Limited special character access
- Talk page integration issues

### Actionable Recommendations

**Priority 1 - Reduce Abandonment**:
- Simplified article creation wizard
- Auto-save & draft recovery
- Progressive complexity

**Priority 2 - Improve Citations**:
- Smart citation assistant
- Citation templates
- Bulk reference mode

**Priority 3 - Structure & Formatting**:
- Section templates
- Smart infobox builder
- Content suggestions

**Priority 4 - Multi-Session Support**:
- Save draft vs publish
- Collaboration invitation
- Mobile ↔ desktop sync

**Priority 5 - Feedback & Learning**:
- Post-creation guidance
- Revision notifications
- Quality checkpoints

## 🔬 Example Findings

### Pattern: Stub-Then-Grow

**Observation**: Many mobile-created articles start as stubs (<500 bytes) and grow through multiple revisions.

**Example Flow**:
1. **Rev 1** (Mobile VE): Lead paragraph only, 234 bytes, no references
2. **Rev 2** (Mobile VE): Same user adds a section, 456 bytes
3. **Rev 3** (Desktop): Different user adds infobox and references, 1,823 bytes
4. **Rev 4** (Desktop): Categories and cleanup, 2,104 bytes

**Implication**: Mobile creators need better support for:
- Multi-session drafts
- Guidance on what to add next
- Easy desktop handoff

### Pattern: Citation Gap

**Observation**: Mobile VE created articles initially lack references.

**Stats** (hypothesized, needs verification):
- 70%+ have zero references in first revision
- References often added by different editor
- Higher deletion rate for unreferenced mobile articles

**Implication**: Critical need for simplified mobile citation tools.

## 🎯 How to Use This Research

### For Product Managers
1. Read [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md)
2. Review Priority 1 recommendations
3. Validate with current data using Quarry queries
4. Plan A/B tests for proposed solutions

### For UX Designers
1. Review pain points section
2. Study user journey patterns
3. Use recommendations as starting point for wireframes
4. Consider mobile-first redesign

### For Researchers
1. Run Quarry queries for current data
2. Use analysis scripts to process results
3. Validate or refute hypothesized patterns
4. Expand research to other languages/time periods

### For Developers
1. Review technical recommendations
2. Identify API requirements for proposed features
3. Estimate implementation complexity
4. Propose technical solutions

### For Wikipedia Community
1. Understand challenges faced by mobile creators
2. Consider WikiProject support for mobile-created stubs
3. Develop mobile-friendly templates
4. Create mentorship for mobile editors

## 📊 Sample Output

When you run the analysis, expect output like:

```
================================================================================
FIRST REVISION PATTERNS ANALYSIS
================================================================================

📊 INITIAL ARTICLE LENGTH STATISTICS
   Total articles analyzed: 127
   Average length: 847 bytes
   Median length: 512 bytes
   Min length: 89 bytes
   Max length: 4,523 bytes

   Length Categories:
   - Very short (<500 bytes): 58 (45.7%)
   - Short (500-2000 bytes): 48 (37.8%)
   - Medium (2000-5000 bytes): 18 (14.2%)
   - Long (>5000 bytes): 3 (2.4%)

👥 CREATOR STATISTICS
   Unique creators: 94
   Articles per creator (avg): 1.35

   Top 10 Most Active Creators:
   1. User:MobileEditor123: 8 articles
   2. User:NewContributor: 5 articles
   ...

⏰ CREATION TIME PATTERNS

   By Hour of Day:
   00:00 -   4 ██
   01:00 -   2 █
   ...
   12:00 -  18 █████████
   ...

   By Day of Week:
   Monday    :  23 ███████████
   Tuesday   :  19 █████████
   ...
```

## 🚧 Limitations & Future Work

### Current Limitations

1. **API Access** - Direct API restricted in some environments
2. **Sample Period** - 30 days may not capture seasonal patterns
3. **Language** - Currently English Wikipedia only
4. **Content Analysis** - Requires wikitext parsing (complex)

### Future Enhancements

- [ ] Multi-language support (es, fr, de, etc.)
- [ ] 90-day and 365-day trend analysis
- [ ] Topic classification (using categories)
- [ ] Quality scoring (predict deletion risk)
- [ ] User journey visualization
- [ ] Automated pattern detection with ML
- [ ] Real-time dashboard

## 🤝 Contributing

This is a research project. Contributions welcome:

1. **Run queries** and share findings
2. **Validate patterns** with current data
3. **Extend analysis** to other languages
4. **Improve tools** - pull requests welcome
5. **Share insights** - found interesting patterns?

## 📖 References

### Primary Sources

1. [Insights on mobile web editing (2025)](https://diff.wikimedia.org/2025/09/26/insights-on-mobile-web-editing-on-wikipedia-in-2025-part-i/)
2. [Mobile Web Editing Research](https://www.mediawiki.org/wiki/Contributors/Mobile_Web_Editing_Research)
3. [Wikimedia Foundation Annual Plan 2025-2026](https://meta.wikimedia.org/wiki/Wikimedia_Foundation_Annual_Plan/2025-2026/)
4. [Wikipedia:Tags](https://en.wikipedia.org/wiki/Wikipedia:Tags)

### Tools & Resources

- [Quarry](https://quarry.wmcloud.org/) - SQL queries against Wikipedia
- [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page)
- [Wikimedia Statistics](https://stats.wikimedia.org/)

## 📧 Contact & Support

- **Issues**: Open GitHub issue in this repository
- **Questions**: See Wikimedia research community pages
- **Collaboration**: Contact Wikimedia Foundation Mobile Editing Working Group

## 📄 License

This research and associated tools are open source.

- **Code**: MIT License
- **Documentation**: CC-BY-SA 4.0 (compatible with Wikipedia)
- **Data**: Subject to Wikimedia Foundation data policies

## ⚡ Quick Commands

```bash
# View the main research report
cat RESEARCH_FINDINGS.md

# View SQL queries
cat quarry_queries.sql

# Run analysis on CSV files
python3 analyze_quarry_results.py

# Try direct API analysis (if accessible)
python3 wikipedia_mobile_analysis.py
```

## 🎓 Citation

If using this research, please cite:

```
Wikipedia Mobile Article Creation Pattern Analysis (2025)
Repository: https://github.com/Sudhanshugtm/mobile-article-creation-patter
Based on: Wikimedia Foundation Mobile Web Editing Research
Accessed: November 5, 2025
```

---

**Last Updated**: November 5, 2025
**Status**: ✅ Ready for use
**Version**: 1.0

*For the best mobile Wikipedia editing experience*