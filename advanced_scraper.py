import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import csv

class GoldSilverScraper:
    """
    Scraper for gold and silver prices from bajus.org
    """
    
    def __init__(self):
        self.url = "https://www.bajus.org/gold-price"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.prices = {}
    
    def fetch_page(self):
        """Fetch the webpage"""
        try:
            print(f"Fetching {self.url}...")
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def parse_prices(self, html_content):
        """Parse prices from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        prices_data = {
            'timestamp': datetime.now().isoformat(),
            'url': self.url,
            'gold': {},
            'silver': {},
            'all_tables': [],
            'all_prices': []
        }
        
        # Extract all tables
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            table_data = {
                'table_number': table_idx + 1,
                'rows': []
            }
            
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data['rows'].append(row_data)
                
                # Check for gold/silver keywords
                row_text = ' '.join(row_data).lower()
                if 'gold' in row_text:
                    prices_data['gold']['table'] = table_idx + 1
                    prices_data['gold']['row_data'] = row_data
                
                if 'silver' in row_text:
                    prices_data['silver']['table'] = table_idx + 1
                    prices_data['silver']['row_data'] = row_data
            
            prices_data['all_tables'].append(table_data)
        
        # Extract all numbers that look like prices
        all_text = soup.get_text()
        price_pattern = r'[\d,]+\.?\d*'
        numbers = re.findall(price_pattern, all_text)
        
        for num_str in numbers:
            try:
                num = float(num_str.replace(',', ''))
                if num > 50:  # Likely a price
                    prices_data['all_prices'].append({
                        'value': num,
                        'original': num_str
                    })
            except:
                pass
        
        # Remove duplicates
        seen = set()
        unique_prices = []
        for p in prices_data['all_prices']:
            if p['value'] not in seen:
                seen.add(p['value'])
                unique_prices.append(p)
        
        prices_data['all_prices'] = unique_prices[:50]  # Top 50 unique prices
        
        return prices_data
    
    def scrape(self):
        """Main scraping method"""
        html = self.fetch_page()
        if html:
            self.prices = self.parse_prices(html)
            return self.prices
        return None
    
    def save_json(self, filename='prices.json'):
        """Save to JSON"""
        if self.prices:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.prices, f, indent=2, ensure_ascii=False)
            print(f"Saved to {filename}")
    
    def save_csv(self, filename='prices.csv'):
        """Save prices to CSV"""
        if self.prices and self.prices['all_tables']:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['Timestamp', self.prices['timestamp']])
                writer.writerow(['URL', self.prices['url']])
                writer.writerow([])
                
                # Write all table data
                for table in self.prices['all_tables']:
                    writer.writerow([f"Table {table['table_number']}"])
                    for row in table['rows']:
                        writer.writerow(row)
                    writer.writerow([])
            
            print(f"Saved to {filename}")
    
    def display_summary(self):
        """Display summary of scraped data"""
        if not self.prices:
            print("No data scraped yet")
            return
        
        print("\n" + "="*70)
        print("GOLD AND SILVER PRICE SCRAPER - SUMMARY")
        print("="*70)
        print(f"Timestamp: {self.prices['timestamp']}")
        print(f"URL: {self.prices['url']}")
        print(f"\nTables found: {len(self.prices['all_tables'])}")
        
        if self.prices['gold']:
            print(f"\nGold Data:")
            print(f"  Table: {self.prices['gold'].get('table')}")
            print(f"  Row: {self.prices['gold'].get('row_data')}")
        
        if self.prices['silver']:
            print(f"\nSilver Data:")
            print(f"  Table: {self.prices['silver'].get('table')}")
            print(f"  Row: {self.prices['silver'].get('row_data')}")
        
        print(f"\nUnique prices found: {len(self.prices['all_prices'])}")
        if self.prices['all_prices']:
            print("Top 10 prices:")
            for i, price in enumerate(self.prices['all_prices'][:10], 1):
                print(f"  {i}. {price['original']} ({price['value']})")
        
        print("="*70 + "\n")

if __name__ == "__main__":
    scraper = GoldSilverScraper()
    scraper.scrape()
    scraper.display_summary()
    scraper.save_json('prices.json')
    scraper.save_csv('prices.csv')
