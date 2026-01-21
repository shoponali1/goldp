from curl_cffi import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import csv
import os
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class PriceScraper:
    """
    Advanced scraper for gold and silver prices with categorization and history
    """
    
    def __init__(self):
        self.url = "https://www.bajus.org/gold-price"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.prices = {
            'gold': {
                '22_carat': [],
                '21_carat': [],
                '18_carat': [],
                'traditional': [],
                'all': []
            },
            'silver': {
                '22_carat': [],
                '21_carat': [],
                '18_carat': [],
                'traditional': [],
                'all': []
            },
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'url': self.url
        }
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories for storing data"""
        directories = [
            'data',
            'data/gold',
            'data/silver',
            'data/raw',
            'data/history'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Directory created/exists: {directory}")
    
    def fetch_page(self):
        """Fetch the webpage with retries and different impersonations"""
        impersonations = [
            "chrome120", 
            "chrome110", 
            "chrome100",
            "safari15_3",
            "edge101"
        ]
        
        for imp in impersonations:
            try:
                print(f"\n📥 Fetching {self.url} (Impersonation: {imp})...")
                response = requests.get(
                    self.url, 
                    headers=self.headers, 
                    timeout=30,
                    impersonate=imp
                )
                
                # If we get a 403, raise specifically to trigger retry
                if response.status_code == 403:
                    print(f"⚠ Got 403 Forbidden with {imp}")
                    continue
                    
                response.raise_for_status()
                print("✓ Page fetched successfully")
                return response.content
            except Exception as e:
                print(f"✗ Error fetching page with {imp}: {e}")
        
        print("❌ All attempts failed.")
        return None
    
    def extract_price_value(self, text):
        """Extract numeric price value from text"""
        # Remove common currency symbols and text
        text = str(text).replace('৳', '').replace('TK', '').replace('BDT', '').strip()
        
        # Extract numbers
        match = re.search(r'[\d,]+\.?\d*', text)
        if match:
            try:
                value = float(match.group().replace(',', ''))
                return value
            except:
                return None
        return None
    
    def categorize_price(self, row_text, price_value):
        """Categorize price based on carat type"""
        row_lower = row_text.lower()
        
        if '22' in row_lower or '22 carat' in row_lower:
            return '22_carat'
        elif '21' in row_lower or '21 carat' in row_lower:
            return '21_carat'
        elif '18' in row_lower or '18 carat' in row_lower:
            return '18_carat'
        elif 'traditional' in row_lower or 'ট্র্যাডিশনাল' in row_text:
            return 'traditional'
        else:
            return 'all'
    
    def parse_prices(self, html_content):
        """Parse prices from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\n🔍 Parsing prices...")
        
        # Extract all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                row_text = ' '.join(row_data)
                
                if not row_text.strip():
                    continue
                
                # Check for gold prices
                if 'gold' in row_text.lower() or 'সোনা' in row_text:
                    print(f"\n🥇 Gold row found: {row_text[:80]}")
                    
                    # Extract all prices from this row
                    for cell_text in row_data:
                        # Skip cells that only contain carat numbers
                        if re.match(r'^(18|21|22)(\s+karat)?$', cell_text.lower()):
                            continue
                            
                        price = self.extract_price_value(cell_text)
                        # Gold prices are typically > 1000 per gram or > 50000 per bhori
                        if price and price > 1000:
                            category = self.categorize_price(row_text, price)
                            
                            price_entry = {
                                'value': price,
                                'original_text': cell_text,
                                'row': row_data,
                                'timestamp': datetime.now().isoformat(),
                                'table': table_idx + 1
                            }
                            
                            self.prices['gold'][category].append(price_entry)
                            self.prices['gold']['all'].append(price_entry)
                            print(f"  ✓ {category}: {price}")
                
                # Check for silver prices
                if 'silver' in row_text.lower() or 'রূপা' in row_text or 'রুপা' in row_text:
                    print(f"\n🥈 Silver row found: {row_text[:80]}")
                    
                    # Extract all prices from this row
                    for cell_text in row_data:
                        # Skip cells that only contain carat numbers
                        if re.match(r'^(18|21|22)(\s+karat)?$', cell_text.lower()):
                            continue
                            
                        price = self.extract_price_value(cell_text)
                        # Silver prices are typically > 100 but < 10000
                        if price and price > 100:
                            category = self.categorize_price(row_text, price)
                            
                            price_entry = {
                                'value': price,
                                'original_text': cell_text,
                                'row': row_data,
                                'timestamp': datetime.now().isoformat(),
                                'table': table_idx + 1
                            }
                            
                            self.prices['silver'][category].append(price_entry)
                            self.prices['silver']['all'].append(price_entry)
                            print(f"  ✓ silver_{category}: {price}")
    
    def save_gold_json(self):
        """Save gold prices to JSON"""
        filename = 'data/gold/gold_prices.json'
        gold_data = {
            'timestamp': self.prices['timestamp'],
            'url': self.prices['url'],
            'prices': self.prices['gold']
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(gold_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Gold prices saved to {filename}")
    
    def save_silver_json(self):
        """Save silver prices to JSON"""
        filename = 'data/silver/silver_prices.json'
        silver_data = {
            'timestamp': self.prices['timestamp'],
            'url': self.prices['url'],
            'prices': self.prices['silver']
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(silver_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Silver prices saved to {filename}")
    
    def save_gold_csv(self):
        """Save gold prices to CSV"""
        filename = 'data/gold/gold_prices.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', self.prices['timestamp']])
            writer.writerow(['URL', self.prices['url']])
            writer.writerow([])
            for cat in ['22_carat', '21_carat', '18_carat', 'traditional']:
                writer.writerow([cat.replace('_', ' ').capitalize()])
                writer.writerow(['Price', 'Original Text', 'Table', 'Time'])
                for entry in self.prices['gold'][cat]:
                    writer.writerow([entry['value'], entry['original_text'], entry['table'], entry['timestamp']])
                writer.writerow([])
        print(f"✓ Gold prices saved to {filename}")
    
    def save_silver_csv(self):
        """Save silver prices to CSV"""
        filename = 'data/silver/silver_prices.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', self.prices['timestamp']])
            writer.writerow(['URL', self.prices['url']])
            writer.writerow([])
            for cat in ['22_carat', '21_carat', '18_carat', 'traditional']:
                writer.writerow([cat.replace('_', ' ').capitalize() + " Silver"])
                writer.writerow(['Price', 'Original Text', 'Table', 'Time'])
                for entry in self.prices['silver'][cat]:
                    writer.writerow([entry['value'], entry['original_text'], entry['table'], entry['timestamp']])
                writer.writerow([])
        print(f"✓ Silver prices saved to {filename}")
    
    def save_raw_data(self):
        """Save raw summary data"""
        filename = 'data/raw/raw_data.json'
        raw_data = {
            'timestamp': self.prices['timestamp'],
            'url': self.prices['url'],
            'gold_summary': {cat: len(self.prices['gold'][cat]) for cat in ['22_carat', '21_carat', '18_carat', 'traditional', 'all']},
            'silver_summary': {cat: len(self.prices['silver'][cat]) for cat in ['22_carat', '21_carat', '18_carat', 'traditional', 'all']}
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Raw data summary saved to {filename}")

    def get_averages(self, metal_type):
        """Calculate average prices for each category for today"""
        averages = {
            'date': self.prices['date'],
            'k22': 0,
            'k21': 0,
            'k18': 0,
            'traditional': 0
        }
        mapping = {
            '22_carat': 'k22',
            '21_carat': 'k21',
            '18_carat': 'k18',
            'traditional': 'traditional'
        }
        for category, key in mapping.items():
            entries = self.prices[metal_type][category]
            if entries:
                averages[key] = int(sum(e['value'] for e in entries) / len(entries))
        return averages

    def save_history(self):
        """Save historical data for gold and silver"""
        for metal in ['gold', 'silver']:
            averages = self.get_averages(metal)
            csv_file = f'data/history/{metal}_history.csv'
            json_file = f'data/history/{metal}_history.json'
            
            # Save CSV
            rows = []
            if os.path.isfile(csv_file):
                with open(csv_file, 'r', encoding='utf-8') as f:
                    rows = list(csv.DictReader(f))
            
            # Update or append
            found = False
            for row in rows:
                if row.get('date') == averages['date']:
                    for key in ['k22', 'k21', 'k18', 'traditional']:
                        row[key] = averages[key]
                    found = True
                    break
            if not found:
                rows.append(averages)
            
            rows.sort(key=lambda x: x['date'])
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'k18', 'k21', 'k22', 'traditional'])
                writer.writeheader()
                writer.writerows(rows)
            
            # Save JSON
            json_rows = []
            if os.path.isfile(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_rows = json.load(f)
                except: pass
            
            found = False
            for i, entry in enumerate(json_rows):
                if entry.get('date') == averages['date']:
                    json_rows[i] = averages
                    found = True
                    break
            if not found:
                json_rows.append(averages)
            
            json_rows.sort(key=lambda x: x['date'])
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_rows, f, indent=2)
            
            print(f"✓ {metal.capitalize()} history updated in data/history/")

    def display_summary(self):
        """Display summary of scraped data"""
        print("\n" + "="*70)
        print("📊 GOLD AND SILVER PRICE SCRAPER - SUMMARY")
        print("="*70)
        print(f"Timestamp: {self.prices['timestamp']}")
        for metal in ['gold', 'silver']:
            icon = "🥇" if metal == "gold" else "🥈"
            print(f"\n{icon} {metal.upper()} PRICES:")
            for cat in ['22_carat', '21_carat', '18_carat', 'traditional']:
                count = len(self.prices[metal][cat])
                avg = sum(e['value'] for e in self.prices[metal][cat]) / count if count > 0 else 0
                print(f"  {cat.replace('_', ' ').capitalize()}: {avg:.2f} ({count} entries)")
        print("\n📄 FILES SAVED:")
        print("  ✓ data/history/gold_history.json & .csv")
        print("  ✓ data/history/silver_history.json & .csv")
        print("="*70 + "\n")
    
    def scrape(self):
        """Main scraping method"""
        html = self.fetch_page()
        if html:
            self.parse_prices(html)
            self.save_gold_json()
            self.save_gold_csv()
            self.save_silver_json()
            self.save_silver_csv()
            
            # Save history only every 3 hours (e.g., 0, 3, 6, 9, 12, 15, 18, 21)
            # This ensures history only grows at 3-hour intervals
            if datetime.now().hour % 3 == 0:
                self.save_history()
            else:
                print("ℹ Skipping history update (scheduled for every 3 hours)")
                
            self.save_raw_data()
            self.display_summary()
            return True
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 GOLD AND SILVER PRICE SCRAPER")
    print("="*70)
    scraper = PriceScraper()
    scraper.scrape()
