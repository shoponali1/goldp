# Gold and Silver Price Scraper

This project scrapes gold and silver prices from https://www.bajus.org/gold-price

## Files

- `scraper.py` - Basic scraper with detailed output
- `advanced_scraper.py` - Advanced scraper with JSON and CSV export
- `requirements.txt` - Python dependencies

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Scraper
```
python scraper.py
```

This will:
- Fetch the webpage
- Extract all tables and price data
- Display the results
- Save to `prices.json`

### Advanced Scraper
```
python advanced_scraper.py
```

This will:
- Fetch the webpage
- Parse all tables and extract gold/silver data
- Extract all prices from the page
- Display a summary
- Save to both `prices.json` and `prices.csv`

## Output Files

- `prices.json` - Structured JSON data with all scraped information
- `prices.csv` - CSV format with all tables and prices

## Features

- Extracts gold prices
- Extracts silver prices
- Parses all tables from the website
- Identifies price values
- Exports to JSON and CSV formats
- Includes timestamp for each scrape
- Handles errors gracefully

## Notes

- The scraper uses a browser User-Agent to avoid being blocked
- Prices are extracted from tables and text content
- All prices above 50 are considered valid prices
- The scraper includes error handling for network issues
