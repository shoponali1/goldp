import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

def scrape_gold_silver_prices():
    """
    Scrape gold and silver prices from bajus.org
    """
    url = "https://www.bajus.org/gold-price"
    
    try:
        # Set headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"Fetching data from {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        prices = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'gold': {},
            'silver': {},
            'raw_data': []
        }
        
        # Get all text content
        all_text = soup.get_text()
        
        # Look for price tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page")
        
        # Extract data from tables
        for idx, table in enumerate(tables):
            rows = table.find_all('tr')
            print(f"\nTable {idx + 1} has {len(rows)} rows:")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                if row_data:
                    print(f"  {row_data}")
                    prices['raw_data'].append(row_data)
                    
                    # Check if this row contains gold or silver data
                    row_text = ' '.join(row_data).lower()
                    if 'gold' in row_text:
                        prices['gold']['raw_row'] = row_data
                    if 'silver' in row_text:
                        prices['silver']['raw_row'] = row_data
        
        # Look for divs with price information
        divs = soup.find_all('div', class_=re.compile(r'price|rate|value', re.I))
        print(f"\nFound {len(divs)} price-related divs")
        
        for div in divs[:10]:  # Show first 10
            text = div.get_text(strip=True)
            if text:
                print(f"  {text[:100]}")
        
        # Extract all numbers that might be prices
        price_pattern = r'[\d,]+\.?\d*'
        all_numbers = re.findall(price_pattern, all_text)
        
        # Filter for likely prices (numbers > 100)
        likely_prices = []
        for num_str in all_numbers:
            try:
                num = float(num_str.replace(',', ''))
                if num > 100:  # Likely a price
                    likely_prices.append(num_str)
            except:
                pass
        
        prices['likely_prices'] = likely_prices[:20]  # First 20 likely prices
        
        return prices
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None
    except Exception as e:
        print(f"Error parsing the page: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_prices_to_json(prices, filename='prices.json'):
    """
    Save scraped prices to a JSON file
    """
    if prices:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(prices, f, indent=2, ensure_ascii=False)
        print(f"\nPrices saved to {filename}")
    else:
        print("No prices to save")

if __name__ == "__main__":
    print("="*60)
    print("GOLD AND SILVER PRICE SCRAPER")
    print("="*60)
    prices = scrape_gold_silver_prices()
    
    if prices:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Timestamp: {prices['timestamp']}")
        print(f"Gold data: {prices['gold']}")
        print(f"Silver data: {prices['silver']}")
        print(f"Likely prices found: {prices['likely_prices']}")
        
        save_prices_to_json(prices)
    else:
        print("Failed to scrape prices")
