"""Add product-image references from catalog source pages.

The site is not copying image files. It stores direct image references and a
link to the public page where each image was found. Existing Open Beauty Facts
images remain local and carry their CC BY-SA attribution.
"""
import concurrent.futures
import html
import json
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "src/data/fragrances.json"
SENTO = ROOT / "data/sources/scento-perfumes.jsonl"
CACHE = ROOT / "data/sources/product-image-references.json"


def normalize_title(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    value = re.sub(r"\b(replica|eau de parfum|eau de toilette|eau de cologne|eau de|edp|edt|parfum|cologne)\b", "", value)
    return re.sub(r"[^a-z0-9]", "", value)


def image_from_page(url):
    """Return the first product page social image and alt label via curl."""
    try:
        result = subprocess.run(
            ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "20",
             "--user-agent", "Mozilla/5.0 MaisonSillage/1.0 (product image source lookup)", url],
            check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    page = result.stdout[:1_200_000]
    tags = re.findall(r'<meta\s+[^>]*>', page, flags=re.I)
    images, alt = [], ""
    for tag in tags:
        prop = re.search(r'(?:property|name)=["\']([^"\']+)["\']', tag, flags=re.I)
        content = re.search(r'content=["\']([^"\']+)["\']', tag, flags=re.I)
        if not prop or not content:
            continue
        key = prop.group(1).casefold()
        value = html.unescape(content.group(1))
        if key == "og:image":
            images.append(value)
        elif key == "og:image:alt":
            alt = value
    for candidate in images:
        image_url = urljoin(url, candidate)
        if image_url.startswith("https://"):
            return {"image": image_url, "alt": alt}
    return None


def main():
    fragrances = json.loads(CATALOG.read_text())
    scento_rows = [json.loads(line) for line in SENTO.read_text().splitlines() if line.strip()]
    page_by_name = {}
    for row in scento_rows:
        page_by_name.setdefault((normalize_title(row["house"]), normalize_title(row["name"])), row.get("url"))

    requests = {}
    for fragrance in fragrances:
        # Keep the existing open-licensed community photos and their credits.
        if fragrance.get("image"):
            continue
        current = next((u for u in fragrance.get("sourceUrls", []) if "scento.com/" in u), None)
        if not current:
            # Use Scento's public product page when its record is an exact title/house match.
            current = page_by_name.get((normalize_title(fragrance["brand"]), normalize_title(fragrance["name"])))
        if not current:
            current = next(iter(fragrance.get("sourceUrls", [])), None)
        if current and current.startswith("https://"):
            requests.setdefault(current, []).append(fragrance["id"])

    cached = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [(url, ids) for url, ids in requests.items() if not cached.get(url)]
    print(f"Looking up {len(todo)} public product pages for {len(requests)} fragrances (3 concurrent requests).", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(image_from_page, url): url for url, _ in todo}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                image = future.result()
            except Exception:
                image = None
            cached[url] = image
            completed += 1
            if completed % 50 == 0:
                print(f"Checked {completed}/{len(todo)} pages; image references found: {sum(bool(v) for v in cached.values())}.", flush=True)
            if completed % 100 == 0:
                CACHE.write_text(json.dumps(cached, ensure_ascii=False, indent=2) + "\n")
    CACHE.write_text(json.dumps(cached, ensure_ascii=False, indent=2) + "\n")

    by_id = {f["id"]: f for f in fragrances}
    added = 0
    for url, ids in requests.items():
        info = cached.get(url)
        if not info or not info.get("image"):
            continue
        for fragrance_id in ids:
            f = by_id[fragrance_id]
            if f.get("image"):
                continue
            f.update({
                "image": info["image"],
                "imageProvider": "Scento" if "scento.com/" in url else "Product source",
                "imageSourceUrl": url,
                "imageAuthor": info.get("alt") or f"{f['brand']} / {f['name']} product page",
                "imageAlt": info.get("alt") or f"{f['brand']} {f['name']} perfume product image",
                "imageLicense": None,
                "imageLicenseUrl": None,
            })
            added += 1

    CATALOG.write_text(json.dumps(fragrances, ensure_ascii=False, indent=2) + "\n")
    print(f"Added {added} remotely hosted product image references.", flush=True)
    print(f"Total catalog photos: {sum(bool(f.get('image')) for f in fragrances)}/{len(fragrances)}.", flush=True)


if __name__ == "__main__":
    main()
