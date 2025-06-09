# Changelog

## [v0.1.0] - 2025-06-07
### Added
- Core script to explore recent congressional bills via Congress.gov API
- Metadata, sponsors, cosponsors, amendments, related bills, and summaries
- HTML-to-text fallback for bill summaries when plain text is missing
- Pagination-aware cosponsor parsing with party breakdown
- Amendment detail enrichment
- Detection and logging of bills with no summaries for future scraping

### Improvements
- Error handling for missing fields (e.g. None replaced with 'Unknown')
- Log file creation with timestamps
- Command-line script execution with debug info


### 📅 2025-06-08

#### 🔧 Major Updates
- Integrated a **Selenium-powered HTML scraper** (`html_scraper_utils.py`) to extract summaries and latest actions from Congress.gov when the API data is missing.
- Implemented **XPath fallback** to extract the most accurate "Latest Action" field directly from the bill info table.
- Enabled **summary fallback** scraping with detailed logs.
- Ensured **screenshot capturing and cleanup** for debugging, with storage at `logs/screenshots/`.
- Added a **debug toggle** (`DEBUG_MODE`) to control whether screenshots are retained or removed after scraping.

#### ✅ Bug Fixes & Enhancements
- Patched `explore_api_data.py` to:
  - Automatically queue and scrape bills that have no summary from the API.
  - Integrate HTML-scraped summaries and latest actions directly into the metadata display.
  - Prevent duplicate scraping or missing logs.
- Improved **log clarity** for scraped and API-loaded data sources.
- Verified all scraper functions with manual testing and screenshots.
- Added guardrails for Cloudflare protection and bot detection.
