#!/usr/bin/env python3
"""Replace generic logo/share-card placeholders with branded bottle studies.

This keeps real product photos wherever a product-specific photo is available.
For entries with only a publisher logo or generic social graphic, it creates a
consistent, original Byredo-inspired minimalist bottle illustration labelled
with that catalog record. It is explicitly illustrative, not exact packaging.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src/data/fragrances.json"
OUTPUT = ROOT / "public/images/fragrance-illustrations"
IMAGE_OVERRIDES = ROOT / "data/sources/product-image-search-overrides.json"
STOP = {"eau", "de", "parfum", "edp", "edt", "cologne", "spray", "the"}

FAMILY_COLOR = {
    "amber": "#b8844e", "vanilla": "#c5a679", "woody": "#786951",
    "spicy": "#a75d39", "leather": "#715747", "gourmand": "#9a684c",
    "floral": "#c18b94", "fresh": "#9eafa5", "aquatic": "#809ca5",
    "citrus": "#c7ac57",
}


def words(value):
    return re.findall(r"[A-Za-z0-9À-ž]+", value or "")


def wrap(value, limit, max_lines=3):
    result, line = [], ""
    for word in words(value):
        candidate = f"{line} {word}".strip()
        if len(candidate) > limit and line:
            result.append(line)
            line = word
        else:
            line = candidate
    if line:
        result.append(line)
    if len(result) > max_lines:
        result = result[:max_lines]
        result[-1] = result[-1][:limit - 1].rstrip() + "…"
    return result


def text_lines(lines, x, y, size, spacing, color, family="Georgia, serif", weight="400"):
    spans = "".join(
        f'<tspan x="{x}" dy="{0 if i == 0 else spacing}">{html.escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}">{spans}</text>'


def illustration(item):
    brand = item["brand"]
    name = item["name"]
    color = next((FAMILY_COLOR[f] for f in item.get("families", []) if f in FAMILY_COLOR), "#a47b52")
    brand_lines = wrap(brand.upper(), 19, 2)
    name_lines = wrap(name, 16, 3)
    brand_svg = text_lines(brand_lines, 350, 350, 13, 17, "#342b24", "Arial, sans-serif", "500")
    name_svg = text_lines(name_lines, 350, 414, 18 if len(name_lines) < 3 else 15, 24, "#342b24")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 700" role="img" aria-labelledby="title">
<title id="title">Illustrative bottle study for {html.escape(brand)} {html.escape(name)}</title>
<defs>
  <linearGradient id="glass" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#fff" stop-opacity=".78"/><stop offset=".3" stop-color="#e8e3d9" stop-opacity=".66"/><stop offset=".72" stop-color="#fff" stop-opacity=".82"/><stop offset="1" stop-color="#d9d3c8" stop-opacity=".72"/></linearGradient>
  <linearGradient id="liquid" x1="0" x2="0" y1="0" y2="1"><stop stop-color="{color}" stop-opacity=".28"/><stop offset="1" stop-color="{color}" stop-opacity=".72"/></linearGradient>
  <linearGradient id="cap" x1="0" x2="1"><stop stop-color="#171614"/><stop offset=".48" stop-color="#302d28"/><stop offset="1" stop-color="#100f0e"/></linearGradient>
  <filter id="shadow" x="-.3" y="-.2" width="1.6" height="1.7"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<rect width="700" height="700" fill="#f1efe9"/>
<ellipse cx="350" cy="605" rx="158" ry="22" fill="#62513e" opacity=".14" filter="url(#shadow)"/>
<ellipse cx="350" cy="596" rx="145" ry="14" fill="#76654f" opacity=".1"/>
<rect x="286" y="126" width="128" height="79" rx="9" fill="url(#cap)"/>
<rect x="302" y="194" width="96" height="39" rx="4" fill="#292722"/>
<path d="M270 225 Q270 212 284 208 L310 198 L390 198 L416 208 Q430 212 430 225 L460 252 Q476 266 476 286 L476 558 Q476 582 452 582 L248 582 Q224 582 224 558 L224 286 Q224 266 240 252 Z" fill="url(#glass)" stroke="#cfc8bc" stroke-width="3"/>
<path d="M235 437 H465 V556 Q465 570 449 570 H251 Q235 570 235 556Z" fill="url(#liquid)"/>
<path d="M242 275 Q242 260 255 255 L278 242" fill="none" stroke="#fff" stroke-opacity=".78" stroke-width="8" stroke-linecap="round"/>
<path d="M455 287 V520" fill="none" stroke="#fff" stroke-opacity=".42" stroke-width="5" stroke-linecap="round"/>
<rect x="263" y="314" width="174" height="185" rx="2" fill="#f8f6f0" stroke="#d7d0c4" stroke-width="1.5"/>
<path d="M280 329 H420" stroke="#c5b89f" stroke-width="1"/>
{brand_svg}
{name_svg}
<text x="350" y="477" text-anchor="middle" fill="#8d806b" font-family="Arial, sans-serif" font-size="8" letter-spacing="2">EAU DE PARFUM</text>
<path d="M280 486 H420" stroke="#c5b89f" stroke-width="1"/>
<text x="350" y="630" text-anchor="middle" fill="#8f8678" font-family="Arial, sans-serif" font-size="9" letter-spacing="2.4">MAISON SILLAGE · BOTTLE STUDY</text>
</svg>'''


def main():
    records = json.loads(CATALOG.read_text())
    overrides = {row["id"]: row for row in json.loads(IMAGE_OVERRIDES.read_text())} if IMAGE_OVERRIDES.exists() else {}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    generated = 0
    for item in records:
        if item["id"] in overrides:
            item.update(overrides[item["id"]])
            item["imageProvider"] = "Product image search"
            item["imageLicense"] = None
            item["imageLicenseUrl"] = None
        filename = f"{item['id']}.svg"
        (OUTPUT / filename).write_text(illustration(item), encoding="utf-8")
        item["fallbackImage"] = f"/images/fragrance-illustrations/{filename}"
        item["fallbackImageAlt"] = f"Illustrative bottle study for {item['brand']} {item['name']}"
        image_url = (item.get("image") or "").lower()
        generic = (
            "scento-logo" in image_url
            or "opengraph-image" in image_url
            or (item.get("id", "").startswith("clone-") and item.get("imageProvider") == "Product source")
        )
        if not generic:
            continue
        item["image"] = f"/images/fragrance-illustrations/{filename}"
        item["imageProvider"] = "Maison Sillage illustration"
        item["imageSourceUrl"] = next((u for u in item.get("sourceUrls", []) if isinstance(u, str) and u.startswith("https://")), None)
        item["imageAuthor"] = "MAISON SILLAGE"
        item["imageAlt"] = f"Illustrative bottle study for {item['brand']} {item['name']}; not exact product packaging"
        item["imageLicense"] = None
        item["imageLicenseUrl"] = None
        generated += 1
    CATALOG.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {generated} labeled bottle illustrations; all real product image references were retained.")


if __name__ == "__main__":
    main()
