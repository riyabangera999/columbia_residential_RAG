# webscraping.py
import time
import csv
import re
import cloudscraper
from bs4 import BeautifulSoup

BASE_URL      = "https://residential.columbia.edu"
LISTING_PATH  = "/content/explore-residences"
URLS_CSV      = "columbia_building_urls.csv"
DETAILS_CSV   = "columbia_buildings_detailed.csv"

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def clean_text(txt: str) -> str:
    return re.sub(r"\s+", " ", txt).strip()

def fetch_soup(scraper, url: str) -> BeautifulSoup:
    resp = scraper.get(url, headers={"Referer": BASE_URL}, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def dump_building_urls():
    scraper = cloudscraper.create_scraper()
    scraper.headers.update(COMMON_HEADERS)
    scraper.get(BASE_URL, timeout=20)  # prime cookies

    seen = set()
    page = 0
    print("Gathering building URLs…")
    while True:
        listing_url = f"{BASE_URL}{LISTING_PATH}?page={page}"
        print(f"  page {page} → {listing_url}")
        soup = fetch_soup(scraper, listing_url)

        new_count = 0
        for a in soup.select("a[href^='/content/']"):
            href = a["href"].split("#")[0]
            if LISTING_PATH not in href:
                full = BASE_URL + href
                if full not in seen:
                    seen.add(full)
                    new_count += 1

        print(f"    found {new_count} new links")
        if new_count == 0:
            break

        page += 1
        time.sleep(0.2)

    with open(URLS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["URL"])
        for u in sorted(seen):
            w.writerow([u])
    print(f"→ Wrote {len(seen)} URLs to {URLS_CSV}")

def extract_building_name_and_desc(soup: BeautifulSoup, url: str):
    # title case
    title = soup.find("title")
    if title:
        name = title.get_text().split("|", 1)[0].strip()
        if name and "Columbia Residential" not in name:
            # try to extract the summary/description paragraph too:
            desc_p = soup.select_one(".summary-text .field--name-field-cu-summary")
            desc = clean_text(desc_p.get_text()) if desc_p else ""
            return name, desc

    # fallback to slug
    slug = url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
    return slug, ""

def extract_details_and_amenities(soup: BeautifulSoup):
    details = {}
    # 1) all <dt>/<dd> under .table-def-list
    if dl := soup.select_one(".table-def-list dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            key = clean_text(dt.get_text()).rstrip(":")
            details[key] = clean_text(dd.get_text())

    # 2) amenities list
    ams = []
    if h3 := soup.find(lambda t: t.name=="h3" and "Building Amenities" in t.get_text()):
        if ul := h3.find_next_sibling("ul"):
            for li in ul.find_all("li"):
                ams.append(clean_text(li.get_text()))

    return details, ", ".join(ams)

def scrape_building_details():
    scraper = cloudscraper.create_scraper()
    scraper.headers.update(COMMON_HEADERS)
    scraper.get(BASE_URL, timeout=20)

    fields = [
        "Building Name", "Description",
        "Built in", "Entrance Location",
        "Number of Residential Floors", "Number of Residential Apartments",
        "Accessible", "Air Conditioning", "Laundry Location", "Laundry Hours",
        "Trash & Recycling Disposal Location", "Trash Pick-up Days",
        "Recycling Pick-up Days", "Cable Provider", "Fire Safety Plan",
        "Superintendent", "Back-up Superintendent",
        "Director of Asset Management", "Portfolio Manager",
        "Building Amenities", "URL"
    ]

    # load URLs
    with open(URLS_CSV, newline="", encoding="utf-8") as f:
        urls = [row["URL"] for row in csv.DictReader(f)]

    with open(DETAILS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{len(urls)}] {url}")
            try:
                soup = fetch_soup(scraper, url)
                name, desc = extract_building_name_and_desc(soup, url)
                details, amenities = extract_details_and_amenities(soup)

                row = {k: details.get(k, "") for k in fields}
                row.update({
                    "Building Name":      name,
                    "Description":        desc,
                    "Building Amenities": amenities,
                    "URL":                url
                })

                writer.writerow(row)
                print("  ✓ scraped")
            except Exception as e:
                print("  ✗ failed:", e)
                # fallback
                slug = url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
                fallback = {k: "" for k in fields}
                fallback.update({
                    "Building Name": slug,
                    "URL":           url
                })
                writer.writerow(fallback)

            time.sleep(0.5)

    print(f"→ Done → {DETAILS_CSV}")

if __name__ == "__main__":
    dump_building_urls()
    scrape_building_details()
