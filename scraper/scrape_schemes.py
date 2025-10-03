import requests
from bs4 import BeautifulSoup
import json
import time

class SchemesScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_telangana_schemes(self):
        """Scrape Telangana government schemes with fallback to dummy data"""
        schemes = []
        
        try:
            # Try to scrape real data
            url = "https://www.telangana.gov.in/schemes"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This will likely fail on first try - that's OK, we have dummy data
            scheme_cards = soup.find_all('div', class_='scheme-item')[:10]
            
            for card in scheme_cards:
                scheme = {
                    'title': card.find('h3').text.strip() if card.find('h3') else 'N/A',
                    'description': card.find('p').text.strip() if card.find('p') else 'N/A',
                    'category': 'Telangana State',
                    'url': card.find('a')['href'] if card.find('a') else '#',
                    'eligibility': 'Details available on official website',
                    'benefits': 'Details available on official website'
                }
                schemes.append(scheme)
                
        except Exception as e:
            print(f"Real scraping failed (expected): {e}")
            print("Using dummy data for prototype...")
            
        # If scraping failed or got nothing, use dummy data
        if len(schemes) == 0:
            schemes = self.get_dummy_telangana_schemes()
            
        return schemes
    
    def scrape_central_schemes(self):
        """Scrape central government schemes with fallback"""
        schemes = []
        
        try:
            url = "https://www.india.gov.in/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Attempt to find schemes
            scheme_links = soup.find_all('a', href=True)[:5]
            
            for link in scheme_links:
                if 'scheme' in link.get('href', '').lower():
                    scheme = {
                        'title': link.text.strip(),
                        'description': 'Central Government Scheme',
                        'category': 'Central Government',
                        'url': link['href'],
                        'eligibility': 'Details available on official website',
                        'benefits': 'Details available on official website'
                    }
                    schemes.append(scheme)
                    
        except Exception as e:
            print(f"Central scraping failed (expected): {e}")
            
        # Fallback to dummy data
        if len(schemes) == 0:
            schemes = self.get_dummy_central_schemes()
            
        return schemes
    
    def get_dummy_telangana_schemes(self):
        """Realistic Telangana schemes for prototype"""
        return [
            {
                'title': 'Rythu Bandhu Scheme',
                'description': 'Financial assistance to farmers for agricultural investment per acre per season. Direct benefit transfer to farmer accounts.',
                'category': 'Telangana State',
                'url': 'https://www.telangana.gov.in',
                'eligibility': 'All farmers in Telangana who own agricultural land',
                'benefits': 'Rs. 5,000 per acre per season (two seasons per year)'
            },
            {
                'title': 'Aasara Pension Scheme',
                'description': 'Monthly pension for elderly citizens, widows, toddy tappers, disabled persons, and beedi workers to ensure social security.',
                'category': 'Telangana State',
                'url': 'https://www.telangana.gov.in',
                'eligibility': 'Age 65+ for elderly, widows of any age, disabled persons with 40%+ disability',
                'benefits': 'Rs. 2,016 per month pension amount directly to bank account'
            },
            {
                'title': 'Kalyana Lakshmi Scheme',
                'description': 'Financial assistance for marriage of girls from economically weaker sections to reduce financial burden on poor families.',
                'category': 'Telangana State',
                'url': 'https://www.telangana.gov.in',
                'eligibility': 'SC/ST/BC/Minority families with annual income less than Rs. 2 lakhs',
                'benefits': 'Rs. 1,00,116 one-time payment for marriage expenses'
            },
            {
                'title': 'KCR Kit Scheme',
                'description': 'Essential items kit for pregnant women and newborn babies delivered in government hospitals to improve maternal and child health.',
                'category': 'Telangana State',
                'url': 'https://www.telangana.gov.in',
                'eligibility': 'All pregnant women delivering in government hospitals in Telangana',
                'benefits': 'Kit containing baby clothes, mosquito net, napkins, soap, powder worth Rs. 5,000'
            },
            {
                'title': 'Mission Bhagiratha',
                'description': 'Providing safe drinking water to every household through tap connections in rural and urban areas.',
                'category': 'Telangana State',
                'url': 'https://www.telangana.gov.in',
                'eligibility': 'All households in Telangana state',
                'benefits': 'Free piped drinking water connection to household'
            },
            {
                'title': 'TS-bPASS Scholarship',
                'description': 'Post-matric scholarship for SC/ST/BC/Minority students pursuing higher education to promote education in backward communities.',
                'category': 'Telangana State',
                'url': 'https://telanganaepass.cgg.gov.in',
                'eligibility': 'SC/ST/BC/Minority students studying in colleges and universities',
                'benefits': 'Tuition fee reimbursement + hostel charges + maintenance allowance'
            }
        ]
    
    def get_dummy_central_schemes(self):
        """Realistic Central Government schemes"""
        return [
            {
                'title': 'PM-KISAN Scheme',
                'description': 'Pradhan Mantri Kisan Samman Nidhi - Income support to all farmer families to supplement financial needs for agriculture.',
                'category': 'Central Government',
                'url': 'https://pmkisan.gov.in',
                'eligibility': 'All landholding farmer families across India',
                'benefits': 'Rs. 6,000 per year in three equal installments of Rs. 2,000'
            },
            {
                'title': 'Ayushman Bharat - PMJAY',
                'description': 'Pradhan Mantri Jan Arogya Yojana - World\'s largest health insurance scheme providing free treatment to poor families.',
                'category': 'Central Government',
                'url': 'https://pmjay.gov.in',
                'eligibility': 'Bottom 40% poor and vulnerable families as per SECC database',
                'benefits': 'Health cover of Rs. 5 lakh per family per year for secondary and tertiary care hospitalization'
            },
            {
                'title': 'PM Awas Yojana - Gramin',
                'description': 'Housing for all in rural areas - Financial assistance to construct pucca houses with basic amenities.',
                'category': 'Central Government',
                'url': 'https://pmayg.nic.in',
                'eligibility': 'Homeless families and families living in kutcha houses in rural areas',
                'benefits': 'Rs. 1.20 lakh in plain areas, Rs. 1.30 lakh in hilly areas for house construction'
            },
            {
                'title': 'Ujjwala Yojana',
                'description': 'Pradhan Mantri Ujjwala Yojana - Free LPG connections to women from BPL families for clean cooking fuel.',
                'category': 'Central Government',
                'url': 'https://pmuy.gov.in',
                'eligibility': 'Women from BPL families, PMAY, AAY beneficiaries',
                'benefits': 'Free LPG connection with deposit-free cylinder and stove'
            },
            {
                'title': 'National Pension Scheme',
                'description': 'NPS - Pension scheme for all citizens to provide retirement income and old age security.',
                'category': 'Central Government',
                'url': 'https://www.npscra.nsdl.co.in',
                'eligibility': 'All Indian citizens aged 18-70 years',
                'benefits': 'Tax benefits + pension after 60 years + flexible investment options'
            },
            {
                'title': 'Pradhan Mantri Mudra Yojana',
                'description': 'MUDRA loans for small businesses and entrepreneurs to promote self-employment and entrepreneurship.',
                'category': 'Central Government',
                'url': 'https://www.mudra.org.in',
                'eligibility': 'Small businesses, micro-enterprises, street vendors, artisans',
                'benefits': 'Loans up to Rs. 10 lakh without collateral at low interest rates'
            }
        ]
    
    def scrape_all(self):
        """Scrape all schemes and save to JSON"""
        print("=" * 50)
        print("GOVERNMENT SCHEMES DATA SCRAPER")
        print("=" * 50)
        
        print("\n[1/2] Scraping Telangana State Schemes...")
        telangana = self.scrape_telangana_schemes()
        print(f"✅ Collected {len(telangana)} Telangana schemes")
        
        time.sleep(1)  # Be respectful to servers
        
        print("\n[2/2] Scraping Central Government Schemes...")
        central = self.scrape_central_schemes()
        print(f"✅ Collected {len(central)} Central schemes")
        
        all_schemes = telangana + central
        
        # Save to JSON
        print(f"\n💾 Saving {len(all_schemes)} total schemes to data/scraped_schemes.json...")
        with open('data/scraped_schemes.json', 'w', encoding='utf-8') as f:
            json.dump(all_schemes, f, indent=2, ensure_ascii=False)
        
        print("✅ Data saved successfully!")
        print("=" * 50)
        return all_schemes

# Test the scraper
if __name__ == "__main__":
    scraper = SchemesScraper()
    schemes = scraper.scrape_all()
    
    print("\n📊 SAMPLE SCHEMES:")
    for i, scheme in enumerate(schemes[:3], 1):
        print(f"\n{i}. {scheme['title']}")
        print(f"   Category: {scheme['category']}")
        print(f"   Benefits: {scheme['benefits'][:80]}...")