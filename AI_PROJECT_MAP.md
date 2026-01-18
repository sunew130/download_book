# AI Project Map: Download Book System

## Project Purpose

This is an automated book downloading and management system that integrates multiple book sources and notification platforms. The tool enables users to:

1. **Search** for books from Project Gutenberg's catalog
2. **Download** books from Z-Library in EPUB or PDF formats
3. **Convert** PDF books to EPUB format using Calibre
4. **Push** completion notifications via multiple channels (PushPlus, Telegram, WxPusher)

The system is designed for automated execution through GitHub Actions workflows, making it easy to download and convert books on-demand without local setup.

---

## File Architecture

### Core Python Files

| File | Primary Responsibility |
|------|----------------------|
| **config.py** | Configuration management - handles environment variables, API tokens, cookies, headers, and reading parameters. Provides a central place for all system configurations. |
| **download_and_convert.py** | Z-Library integration - searches for books, downloads EPUB (preferred) or PDF formats, and converts PDFs to EPUB using Calibre's `ebook-convert` tool. |
| **push.py** | Multi-platform notification system - supports PushPlus, Telegram, and WxPusher for sending download completion notifications. |
| **search.py** | Gutenberg catalog search - downloads Project Gutenberg's catalog, filters books, and batch downloads EPUB files. |

### Configuration & Workflows

| File | Purpose |
|------|---------|
| **.github/workflows/download_and_convert.yml** | GitHub Actions workflow for automated book downloading. Runs in a Docker container with Calibre installed. |
| **README.md** | Currently empty - this AI_PROJECT_MAP.md serves as the main documentation. |

---

## Core Workflow

The system operates in multiple modes depending on the entry point:

### Workflow 1: Manual Z-Library Download (via GitHub Actions)

```
User Input (Book Title)
    ↓
GitHub Actions Triggered
    ↓
download_and_convert.py
    ├─→ Search Z-Library
    ├─→ Download EPUB (if available)
    └─→ OR Download PDF → Convert to EPUB
    ↓
Store as GitHub Artifact
    ↓
push.py (Optional)
    └─→ Send notification (PushPlus/Telegram/WxPusher)
```

### Workflow 2: Gutenberg Batch Download

```
search.py executed
    ↓
Download pg_catalog.csv.gz
    ↓
Filter books (exclude specific authors, only Text type)
    ↓
Batch download EPUB files
```

### Workflow 3: WeChat Reading Automation

The `config.py` includes WeChat reading automation parameters:
- Simulates reading sessions with configurable read count (default: 120/60min)
- Uses authenticated headers and cookies for WeChat reading API
- Sends periodic read events to maintain reading streaks

---

## Key Configurations

### Environment Variables (config.py)

The system uses environment variables for secure configuration. All values can be set locally or via GitHub Secrets:

#### Reading Parameters
- **READ_NUM**: Number of reading sessions (default: 120 per 60 minutes)

#### Push Notification Tokens
- **PUSH_METHOD**: Choose notification channel (`"pushplus"`, `"telegram"`, or `"wxpusher"`)
- **PUSHPLUS_TOKEN**: Token for PushPlus service
- **TELEGRAM_BOT_TOKEN**: Telegram bot authentication token
- **TELEGRAM_CHAT_ID**: Target Telegram chat ID
- **WXPUSHER_SPT**: WxPusher SPT (Simple Push Token)

#### WeChat Reading Authentication
- **WXREAD_CURL_BASH**: Full cURL command with headers/cookies for WeChat reading API
- **headers**: HTTP headers for API requests (User-Agent, Accept, etc.)
- **cookies**: Session cookies for authenticated requests
- **data**: Sample reading event payload (default: "The Three-Body Problem" book)

### Z-Library Configuration (download_and_convert.py)

Required as command-line arguments or GitHub Secrets:
- **--userid**: Z-Library `remix_userid`
- **--userkey**: Z-Library `remix_userkey`
- **--title**: Book title to search for
- **--output**: Output directory for downloaded files

### Conversion Priority

1. **First**: Search for EPUB format (preferred, no conversion needed)
2. **Fallback**: Download PDF and convert to EPUB using `ebook-convert`

---

## Dependencies

The project requires the following Python libraries:

### Core Dependencies
```python
# HTTP requests
import requests

# File and system operations
import os
import subprocess
import tempfile
import argparse
import sys

# Data parsing
import csv
import gzip
import json
import re

# Utilities
import random
import time
import logging
```

### External Python Packages
- **Zlibrary**: Custom Z-Library API wrapper (installed from GitHub)
  - Repository: `https://github.com/sunew130/Zlibrary-API.git@dev`
- **requests**: HTTP library for API calls

### System Dependencies (Docker Container)
- **Calibre**: E-book management and conversion tool
  - Provides `ebook-convert` CLI for PDF → EPUB conversion
- **python3-pip**: Python package manager
- **xvfb**: Virtual framebuffer for headless GUI operations

---

## Execution Guide

### Method 1: GitHub Actions (Recommended)

This is the primary deployment method for automated, cloud-based execution.

1. **Setup Secrets** in GitHub repository settings:
   - `ZLIBRARY_USERID`
   - `ZLIBRARY_USERKEY`
   - `PUSH_METHOD` (optional)
   - `WXPUSHER_SPT` or `PUSHPLUS_TOKEN` or `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`

2. **Trigger Workflow**:
   - Go to Actions → "Download and Convert Book"
   - Click "Run workflow"
   - Enter book title
   - Wait for completion

3. **Download Result**:
   - Check workflow run artifacts
   - Download the EPUB file
   - (Optional) Receive notification on configured platform

### Method 2: Local Execution

#### Prerequisites
```bash
# Install Calibre
sudo apt-get install calibre

# Install Python dependencies
pip install requests
pip install git+https://github.com/sunew130/Zlibrary-API.git@dev
```

#### Download and Convert a Book
```bash
python3 download_and_convert.py \
  --title "Book Title" \
  --output ./downloads \
  --userid "your_remix_userid" \
  --userkey "your_remix_userkey"
```

#### Search and Download from Gutenberg
```bash
python3 search.py
# This will download pg_catalog.csv.gz and batch download EPUBs
```

#### Send Test Notification
```bash
python3 push.py "Test message" "wxpusher"
# OR
python3 push.py "Test message" "pushplus"
# OR
python3 push.py "Test message" "telegram"
```

### Method 3: Docker Execution (GitHub Actions Style)

```bash
docker run --rm -v $(pwd):/workdir linuxserver/calibre:latest /bin/bash -c "
  apt-get update && \
  apt-get install -y python3-pip git xvfb && \
  python3 -m pip install requests --break-system-packages && \
  python3 -m pip install git+https://github.com/sunew130/Zlibrary-API.git@dev --break-system-packages && \
  mkdir -p /workdir/downloads && \
  xvfb-run python3 /workdir/download_and_convert.py \
    --title 'Book Title' \
    --output /workdir/downloads \
    --userid 'your_userid' \
    --userkey 'your_userkey'
"
```

---

## Technical Notes

### File Formats
- **Primary Target**: EPUB (widely supported, reflowable text)
- **Conversion Source**: PDF (converted using Calibre)
- **Artifact Storage**: GitHub Actions artifacts (90-day retention)

### Notification System
The push system implements:
- **Retry Logic**: 5 attempts with 3-6 minute delays (PushPlus, WxPusher)
- **Proxy Fallback**: Telegram tries proxy first, then direct connection
- **Logging**: Comprehensive logging for debugging failed pushes

### Security Considerations
- All tokens stored in GitHub Secrets (never committed)
- Cookie/header parsing from cURL commands for WeChat integration
- Environment variable fallback pattern for flexible deployment

### Error Handling
- Graceful degradation when EPUB unavailable (tries PDF)
- Temporary file cleanup after PDF conversion
- Validation of search results before download attempts

---

## Common Use Cases

1. **Automated Library Building**: Schedule workflow runs for book series
2. **Format Standardization**: Convert PDF collections to EPUB
3. **Mobile Reading**: Download EPUBs optimized for phone/tablet readers
4. **Notification Integration**: Get alerts when books finish downloading
5. **Batch Processing**: Use search.py for bulk Gutenberg downloads

---

## Future Enhancement Ideas

- Add more book sources (LibGen, Anna's Archive)
- Support for MOBI/AZW3 formats
- Metadata enhancement (cover images, author info)
- Download queue management
- Web interface for easier book requests
- Integration with e-reader services (Kindle, Kobo)

---

## License & Credits

This project integrates:
- **Z-Library API**: Custom wrapper for Z-Library access
- **Calibre**: Open-source e-book management (GPLv3)
- **Project Gutenberg**: Public domain book catalog

---

*Generated: 2026-01-18*
*Purpose: AI agent and developer onboarding documentation*
