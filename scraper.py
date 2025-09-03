import os
import re
import requests
import random
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURATION ---
WEB_APP_URL = os.environ.get("WEB_APP_URL")
TARGET_PRODUCTS_PER_RUN = 2
MAX_PAGES_TO_CHECK = 10
BASE_DOMAIN = "https://www.daraz.com.bd"
SEARCH_URLS = [
    "https://www.daraz.com.bd/catalog/?q=shirt",
    "https://www.daraz.com.bd/catalog/?q=bra",
    "https://www.daraz.com.bd/catalog/?q=air+pods",
    "https://www.daraz.com.bd/catalog/?q=shoes",
    "https://www.daraz.com.bd/catalog/?q=thongs",
    "https://www.daraz.com.bd/catalog/?q=condom",
    "https://www.daraz.com.bd/catalog/?q=woman+underwear",
    "https://www.daraz.com.bd/catalog/?q=jewelry",
    "https://www.daraz.com.bd/catalog/?q=bag",
    "https://www.daraz.com.bd/catalog/?q=woman+cosmetic",
    "https://www.daraz.com.bd/catalog/?q=watch",
    "https://www.daraz.com.bd/catalog/?q=sarees",
    "https://www.daraz.com.bd/catalog/?q=pants",
    "https://www.daraz.com.bd/catalog/?q=mobile+phone",
    "https://www.daraz.com.bd/catalog/?q=power+bank",
    "https://www.daraz.com.bd/catalog/?q=earphones",
    "https://www.daraz.com.bd/catalog/?q=trimmer",
    "https://www.daraz.com.bd/catalog/?q=face+wash",
    "https://www.daraz.com.bd/catalog/?q=shampoo",
    "https://www.daraz.com.bd/catalog/?q=skincare",
    "https://www.daraz.com.bd/catalog/?q=soap",
    "https://www.daraz.com.bd/catalog/?q=detergent",
    "https://www.daraz.com.bd/catalog/?q=diapers",
    "https://www.daraz.com.bd/catalog/?q=notebook",
    "https://www.daraz.com.bd/catalog/?q=snacks",
    "https://www.daraz.com.bd/catalog/?q=tea",
    "https://www.daraz.com.bd/catalog/?q=spices",
    "https://www.daraz.com.bd/catalog/?q=hair+oil",
    "https://www.daraz.com.bd/catalog/?q=kitchen+appliances",
    "https://www.daraz.com.bd/catalog/?q=sunglasses",
    "https://www.daraz.com.bd/catalog/?q=cooking+oil",
    "https://www.daraz.com.bd/catalog/?q=rice",
    "https://www.daraz.com.bd/catalog/?q=flour",
    "https://www.daraz.com.bd/catalog/?q=sugar",
    "https://www.daraz.com.bd/catalog/?q=dal",
    "https://www.daraz.com.bd/catalog/?q=masala",
    "https://www.daraz.com.bd/catalog/?q=biscuits",
    "https://www.daraz.com.bd/catalog/?q=cereals",
    "https://www.daraz.com.bd/catalog/?q=milk+powder",
    "https://www.daraz.com.bd/catalog/?q=coffee",
    "https://www.daraz.com.bd/catalog/?q=toothpaste",
    "https://www.daraz.com.bd/catalog/?q=body+lotion",
    "https://www.daraz.com.bd/catalog/?q=perfume",
    "https://www.daraz.com.bd/catalog/?q=hand+sanitizer",
    "https://www.daraz.com.bd/catalog/?q=kitchen+utensils",
    "https://www.daraz.com.bd/catalog/?q=water+bottle",
    "https://www.daraz.com.bd/catalog/?q=bed+sheet",
    "https://www.daraz.com.bd/catalog/?q=pillow",
    "https://www.daraz.com.bd/catalog/?q=towel",
    "https://www.daraz.com.bd/catalog/?q=light+bulb"
]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"


def get_existing_products(url):
    """Fetches existing product titles and URLs, and handles the missing secret case."""
    if not url:
        print("\n--- CRITICAL ERROR ---")
        print("[ERROR] WEB_APP_URL secret is not set in GitHub repository settings.")
        print("Please add it under Settings > Secrets and variables > Actions.")
        return None, None
    print("\n--- Checking for existing products in Google Sheets... ---")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        existing_titles, existing_urls = set(data.get('titles', [])), set(data.get('urls', []))
        print(f"Found {len(existing_titles)} existing titles and {len(existing_urls)} existing URLs.")
        return existing_titles, existing_urls
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not fetch existing product data: {e}")
        return set(), set()

def is_actually_image(url):
    """Checks the URL's Content-Type header to confirm it's an image and not an XML/HTML page."""
    try:
        response = requests.head(url, headers={'User-Agent': USER_AGENT}, timeout=7, allow_redirects=True)
        if response.status_code == 200 and 'image/' in response.headers.get('Content-Type', ''):
            return True
        else:
            print(f"    [Validation Failed] Status: {response.status_code}, Type: {response.headers.get('Content-Type', 'N/A')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"    [Validation Failed] Request error: {e}")
        return False

# --- NEW 3-STEP IMAGE VALIDATION AND CLEANING FUNCTION ---
def get_valid_image_url(url):
    """
    Validates a potential image URL using a three-step process:
    1. Check the original URL.
    2. If it fails and ends with '_', clean it and check again.
    3. If all checks fail, return None.
    """
    # Step 1: Check the original URL
    if is_actually_image(url):
        return url
    
    # Step 2: If the first check fails, see if it's eligible for cleaning
    if re.search(r'\.(jpg|jpeg|png)_$', url, re.IGNORECASE):
        cleaned_url = url.rstrip('_')
        print(f"    Original URL failed. Testing cleaned version: {cleaned_url}")
        # Step 2a: Check the cleaned URL
        if is_actually_image(cleaned_url):
            return cleaned_url
    
    # Step 3: If all attempts fail, give up
    print(f"    [Discarding URL] All validation attempts failed for: {url}")
    return None

def scrape_product_details(page, url):
    """Scrapes product details and uses the new 3-step validation for images."""
    print(f"Scraping details for: {url}")
    try:
        page.goto(url, timeout=90000, wait_until="domcontentloaded")
        page.wait_for_selector("h1.pdp-mod-product-badge-title", timeout=20000)
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        time.sleep(random.uniform(1, 2))
    except PlaywrightTimeoutError:
        print(f"Timeout: Essential content did not load for {url}.")
        page.screenshot(path="debug_product_page_failure.png")
        return {} 

    soup = BeautifulSoup(page.content(), 'html.parser')
    
    title = (soup.find('h1', class_='pdp-mod-product-badge-title').text.strip() if soup.find('h1', 'pdp-mod-product-badge-title') else "Title Not Found")
    price = "Price Not Found"
    if soup.select_one('span.pdp-price_size_xl'): price = soup.select_one('span.pdp-price_size_xl').text.strip()
    discount = "N/A"
    if soup.find('span', class_='pdp-product-price__discount'): discount = soup.find('span', 'pdp-product-price__discount').text.strip()
    
    validated_image_urls = []
    gallery = soup.find('div', class_='item-gallery')
    if gallery:
        thumbnails = gallery.find_all('img', class_='item-gallery__thumbnail-image')
        if thumbnails:
            print(f"Found {len(thumbnails)} potential image thumbnails. Validating...")
            for img in thumbnails:
                raw_src = img.get('src', '')
                if not raw_src: continue

                # --- BUG FIX for URL CONSTRUCTION ---
                if raw_src.startswith('//'):
                    base_url = 'https:' + raw_src
                else:
                    base_url = raw_src # Assumes it's already a full URL

                # Clean the URL to get the high-res version
                potential_url = re.sub(r'_\d+x\d+q\d+\.jpg|\.webp|_\d+x\d+q\d+\.png', '', base_url)
                
                # Use our new robust validation function
                valid_url = get_valid_image_url(potential_url)
                if valid_url:
                    validated_image_urls.append(valid_url)

            # If, after all that, no images are valid, discard the product.
            if not validated_image_urls:
                print(f"**DISCARDING PRODUCT '{title[:30]}...'**: All its image thumbnails led to invalid or broken URLs.")
                return {}

    print(f"Found {len(validated_image_urls)} valid image(s) for this product.")
    return {"title": title, "price": price, "discount": discount, "product_url": url, "image_urls": validated_image_urls}

def send_single_product_to_sheet(details, url):
    """Sends a single product's data and returns True on success, False on failure."""
    if not url or not details: return False
    
    title_preview = details.get('title', 'NA')[:40]
    print(f"--- Attempting to send '{title_preview}...' to Google Sheets ---")
    try:
        response = requests.post(url, json=details, timeout=20)
        response.raise_for_status()
        print(f"    SUCCESS: Data sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"    FAILURE: Could not send '{title_preview}...'. Error: {e}")
        return False

def main_scraper():
    """Main scraper with robust, multi-step image validation."""
    print("--- Starting the full scraping process... ---")
    existing_titles, existing_urls = get_existing_products(WEB_APP_URL)
    if existing_titles is None: return

    base_search_url = random.choice(SEARCH_URLS)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT, viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        successfully_sent_count = 0
        try:
            for page_num in range(1, MAX_PAGES_TO_CHECK + 1):
                if successfully_sent_count >= TARGET_PRODUCTS_PER_RUN: break
                
                current_url = f"{base_search_url}&page={page_num}"
                print(f"\n--- Checking Search Page {page_num}: {current_url} ---")
                try:
                    page.goto(current_url, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_selector('div[data-qa-locator="product-item"]', timeout=20000)
                except PlaywrightTimeoutError:
                    print(f"Could not load search page {page_num}. Ending run for this category.")
                    break
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                page_urls = ["https:" + item['href'] for item in soup.select('div[data-qa-locator="product-item"] a') if item.has_attr('href')]
                
                if not page_urls:
                    print(f"No more products found on page {page_num}. Ending search.")
                    break
                
                candidate_urls = [url for url in list(dict.fromkeys(page_urls)) if url not in existing_urls]
                
                if not candidate_urls:
                    print(f"No new products found on page {page_num}. Continuing to next page...")
                    continue

                print(f"Found {len(candidate_urls)} new potential products. Trying to scrape and send until target is met.")
                for url in candidate_urls:
                    if successfully_sent_count >= TARGET_PRODUCTS_PER_RUN: break
                        
                    details = scrape_product_details(page, url)
                    
                    if details and details.get('title') != 'Title Not Found' and details['title'] not in existing_titles:
                        if send_single_product_to_sheet(details, WEB_APP_URL):
                            successfully_sent_count += 1
                            existing_titles.add(details['title']) 
                            existing_urls.add(url)
                            print(f"Total successful sends so far: {successfully_sent_count}/{TARGET_PRODUCTS_PER_RUN}.")
                
            if successfully_sent_count >= TARGET_PRODUCTS_PER_RUN:
                print(f"\nTarget of {TARGET_PRODUCTS_PER_RUN} successfully sent products reached.")
            
            if successfully_sent_count == 0:
                print(f"\nNo new products were successfully sent after checking up to {MAX_PAGES_TO_CHECK} pages.")
            else:
                print(f"\nFinished run. Total products sent successfully: {successfully_sent_count}")
        finally:
            print("\n--- Scraper finished ---")
            browser.close()

if __name__ == "__main__":
    main_scraper()
