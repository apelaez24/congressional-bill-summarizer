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
