from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests, os
from PIL import Image
from io import BytesIO
import time
import random
from PIL import UnidentifiedImageError

# Output directory
SAVE_DIR = "leaf_samples"
os.makedirs(SAVE_DIR, exist_ok=True)
downloaded = set(os.listdir(SAVE_DIR))

# Chrome driver options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")

# Launch browser
driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver.get("https://www.reddit.com/r/plantclinic/top/?t=month")

input("Scroll manually to load images. Press ENTER to start scraping...\n")

def get_images():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_candidates = set()

    # Extract from <img src=...>
    for img_tag in soup.find_all("img"):
        src = img_tag.get("src")
        if src and "i.redd.it" in src:
            img_candidates.add(src.split("?")[0])

    # Extract from <a href=...>
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "i.redd.it" in href and (href.endswith(".jpg") or href.endswith(".png")):
            img_candidates.add(href.split("?")[0])

    print(f"Found {len(img_candidates)} image candidates")

    stats = {
        "saved": 0,
        "avatar_skipped": 0,
        "html_skipped": 0,
        "too_small": 0,
        "invalid": 0,
        "duplicate": 0
    }

    for url in img_candidates:
        filename = url.split("/")[-1]

        # Skip avatars or already downloaded
        if "profileIcon" in filename or "headshot" in filename:
            stats["avatar_skipped"] += 1
            continue
        if filename in downloaded:
            stats["duplicate"] += 1
            continue

        try:
            r = requests.get(url, timeout=10)
            content_type = r.headers.get("Content-Type", "")
            if "text/html" in content_type:
                stats["html_skipped"] += 1
                continue

            img = Image.open(BytesIO(r.content)).convert("RGB")
            if img.width < 300 or img.height < 300:
                stats["too_small"] += 1
                continue

            save_path = os.path.join(SAVE_DIR, filename)
            img.save(save_path)
            downloaded.add(filename)
            stats["saved"] += 1
            print(f"Saved: {filename}")
            time.sleep(random.uniform(0.5, 1.5))  # delay between saves

        except UnidentifiedImageError:
            stats["invalid"] += 1
            print(f"Invalid image: {url}")
        except Exception as e:
            print(f"Failed: {url}, reason: {e}")

    print("\nSummary of this round:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print()

# Repeatedly scroll and scrape
while True:
    get_images()
    input("Scroll more and press ENTER to continue scraping...\n")
