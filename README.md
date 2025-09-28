# DadAssist Content Automation

Automated content discovery and processing pipeline for DadAssist legal resources.

## Overview

This repository automates the process of:
- Finding relevant legal articles using Apify web scraping
- Downloading and organizing content locally
- Preparing articles for Q Developer processing
- Managing the content pipeline for DadAssist website

## Repository Structure

```
dadassist-content-automation/
├── .github/workflows/          # GitHub Actions automation
│   └── weekly-scraping.yml     # Weekly content scraping workflow
├── scripts/                    # Python automation scripts
│   ├── apify_scraper.py       # Apify API integration
│   ├── content_downloader.py  # Download scraped content
│   └── notifier.py            # Send completion notifications
├── config/                     # Configuration files
│   ├── apify_config.json      # Apify scraping settings
│   └── sources.json           # Target legal websites
├── templates/                  # DadAssist article templates
│   └── dadassist_template.html # Standard article template
├── downloads/                  # Local content storage
│   └── [date-organized folders]
└── requirements.txt           # Python dependencies
```

## Workflow

1. **Weekly Trigger**: GitHub Actions runs every Monday at 9 AM
2. **Content Discovery**: Apify searches for new legal articles
3. **Content Extraction**: Full article text and metadata extracted
4. **Local Download**: Content saved to local drive
5. **Notification**: Email/Slack notification sent with summary
6. **Manual Processing**: Use Q Developer to rewrite and publish

## Setup Instructions

1. Clone this repository
2. Set up Apify account and get API token
3. Configure GitHub Secrets for API keys
4. Test workflow manually before scheduling

## Cost

- GitHub Actions: Free (public repository)
- Apify: Free tier (100 compute units/month)
- Total: $0/month

## Content Sources

Targeting Australian legal websites:
- legalaid.vic.gov.au
- familycourt.gov.au
- ag.gov.au
- lawhandbook.sa.gov.au
- lawaccess.nsw.gov.au

## Output

Each run produces:
- 5 new legal articles
- Structured JSON data
- Article metadata
- Ready for Q Developer processing
