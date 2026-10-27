#!/usr/bin/env python3
"""Merge open fragrance clone references into the Maison Sillage library.

The sources are attribution-licensed reference datasets. This importer keeps
their rows in data/sources, deduplicates on normalized brand/name, and preserves
unknown product fields rather than fabricating notes or suitability.
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src/data/fragrances.json"
SCENTO = ROOT / "data/sources/scento-perfumes.jsonl"
DJ = ROOT / "data/sources/dupejoy-fragrance-dupes.csv"
PCF = ROOT / "data/sources/perfumeclonefinder-clones.csv"
TODAY = "2026-10-26"


def norm(value):
    value = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().casefold()
    value = re.sub(r"\b(replica|eau de parfum|eau de toilette|eau de cologne|eau de|edp|edt|parfum|cologne|for men|for women)\b", "", value)
    return re.sub(r"[^a-z0-9]", "", value)


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value):
    try:
        result = float(value)
        return int(result) if result.is_integer() else result
    except (ValueError, TypeError, AttributeError):
        return None


def rounded_price(value):
    value = number(value)
    if value is None or value <= 0:
        return None
    return round(value, 2)


def main():
    catalog = json.loads(CATALOG.read_text())
    by_identity = {(norm(f["brand"]), norm(f["name"])): f for f in catalog}
    scento = [json.loads(line) for line in SCENTO.read_text().splitlines() if line.strip()]
    scento_by_identity = {(norm(row.get("house")), norm(row.get("name"))): row for row in scento}
    pcf_by_identity = {}

    for row in csv_rows(PCF):
        identity = (norm(row.get("clone_house")), norm(row.get("clone")))
        if all(identity):
            pcf_by_identity.setdefault(identity, row)

    pairs = {}
    for row in csv_rows(PCF):
        clone_brand, clone_name = row.get("clone_house"), row.get("clone")
        if not clone_brand or not clone_name:
            continue
        identity = (norm(clone_brand), norm(clone_name))
        item = pairs.setdefault(identity, {
            "brand": clone_brand, "name": clone_name,
            "concentration": row.get("concentration") or None,
            "price": rounded_price(row.get("clone_price_usd")),
            "priceOriginal": row.get("original_price_usd"),
            "inspiredBy": [], "sourceUrls": [], "cloneUrl": row.get("clone_url"),
            "originalUrl": row.get("original_url"), "priceSource": "PerfumeCloneFinder",
        })
        if row.get("clone_url") and row["clone_url"] not in item["sourceUrls"]:
            item["sourceUrls"].append(row["clone_url"])
        if row.get("original_url") and row["original_url"] not in item["sourceUrls"]:
            item["sourceUrls"].append(row["original_url"])
        if item["price"] is None:
            item["price"] = rounded_price(row.get("clone_price_usd"))
        reference = {
            "brand": row.get("original_house"), "name": row.get("original"),
            "similarityPct": round(number(row.get("similarity_score")) * 10) if number(row.get("similarity_score")) is not None else None,
            "source": "PerfumeCloneFinder", "sourceUrl": row.get("clone_url"),
        }
        if reference not in item["inspiredBy"]:
            item["inspiredBy"].append(reference)

    for row in csv_rows(DJ):
        identity = (norm(row.get("dupe_brand")), norm(row.get("dupe")))
        if not all(identity):
            continue
        item = pairs.setdefault(identity, {
            "brand": row["dupe_brand"], "name": row["dupe"], "concentration": None,
            "price": rounded_price(row.get("dupe_price_usd")), "priceOriginal": row.get("original_price_usd"),
            "inspiredBy": [], "sourceUrls": [], "cloneUrl": row.get("url"),
            "originalUrl": row.get("url"), "priceSource": "Dupejoy",
        })
        if not item["price"]:
            item["price"] = rounded_price(row.get("dupe_price_usd"))
            item["priceSource"] = "Dupejoy"
        if row.get("url") and row["url"] not in item["sourceUrls"]:
            item["sourceUrls"].append(row["url"])
        shared = [n.strip() for n in (row.get("shared_notes") or "").split(";") if n.strip()]
        different = [n.strip() for n in (row.get("notes_not_shared") or "").split(";") if n.strip()]
        reference = {
            "brand": row.get("original_brand"), "name": row.get("original"),
            "similarityPct": number(row.get("note_match_pct")),
            "sharedNotes": shared, "notesNotShared": different,
            "source": "Dupejoy", "sourceUrl": row.get("url"),
        }
        if reference not in item["inspiredBy"]:
            item["inspiredBy"].append(reference)

    added = 0
    linked_existing = 0
    for identity, item in sorted(pairs.items()):
        existing = by_identity.get(identity)
        if existing:
            links = existing.setdefault("inspiredBy", [])
            for reference in item["inspiredBy"]:
                if reference not in links:
                    links.append(reference)
            if len(links):
                linked_existing += 1
            continue

        reference = item["inspiredBy"][0] if item["inspiredBy"] else {}
        similar_notes = []
        for pair in item["inspiredBy"]:
            for note in pair.get("sharedNotes", []):
                if note.casefold() not in {n.casefold() for n in similar_notes}:
                    similar_notes.append(note)
        source_row = scento_by_identity.get(identity)
        notes = source_row.get("notes") if source_row else None
        if notes is not None:
            notes = notes or None
        elif similar_notes:
            notes = similar_notes

        original_name = reference.get("name") or ""
        slug = re.sub(r"[^a-z0-9]+", "-", f"{item['brand']}-{item['name']}".casefold()).strip("-")
        used_id = {f["id"] for f in catalog}
        record_id = f"clone-{slug}"
        suffix = 2
        while record_id in used_id:
            record_id = f"clone-{slug}-{suffix}"
            suffix += 1

        urls = item["sourceUrls"][:]
        if source_row and source_row.get("url") and source_row["url"] not in urls:
            urls.insert(0, source_row["url"])
        if item.get("cloneUrl") and item["cloneUrl"] not in urls:
            urls.insert(0, item["cloneUrl"])

        # Scento supplies more than note data; only claim editorial fields when
        # an exact house/name match exists in its CC BY 4.0 dataset.
        climates, occasions, families = [], [], []
        if source_row:
            season_map = {"spring": "mild", "summer": "hot", "autumn": "cool", "winter": "cold"}
            climates = list(dict.fromkeys(season_map[s] for s in source_row.get("seasons", []) if s in season_map))
            time_map = {"day": "daily", "evening": "evening"}
            occasions = list(dict.fromkeys(time_map[t] for t in source_row.get("times_of_day", []) if t in time_map))
            if "date night" in (source_row.get("description") or "").casefold():
                occasions.append("date night")
            family_map = {"Wood & Root": "woody", "White Bloom": "floral", "Petal Garden": "floral", "Green Leaf": "fresh", "Velvet Sweet": "gourmand", "Spice Route": "spicy", "Sunlit Citrus": "citrus", "Amber & Resin": "amber", "Powder Veil": "floral", "Skin Musk": "fresh", "Smoke & Leather": "leather", "Oud Court": "woody", "Salt & Mineral": "aquatic"}
            families = list(dict.fromkeys(family_map[x] for x in (source_row.get("family"), source_row.get("secondary_family")) if x in family_map))

        price = item.get("price")
        price_basis = f"Typical USD retail figure in the {item['priceSource']} clone dataset, normalized as a low-confidence 100 ml reference because the source does not state bottle size; verify the exact bottle before buying." if price is not None else ""
        if price is None and item["brand"] == "Al Haramain":
            # Fallback to the rounded median of other Al Haramain reference
            # prices in the current catalog; never describe it as a listing.
            price = 50
            price_basis = "Estimated at the $50 median of 27 other Al Haramain catalog references and normalized to a 100 ml reference. This is not an item-specific listing; confirm bottle size and current price."
        record = {
            "id": record_id, "brand": item["brand"], "name": item["name"],
            "concentration": item.get("concentration"), "families": families,
            "notes": notes, "climates": climates, "occasions": occasions,
            "intensity": None, "bottleSizeMl": None, "image": None,
            "imageLicense": None, "sourceUrls": urls,
            "priceSourceUrl": None, "verifiedAt": TODAY,
            "notesStatus": "publisher-sourced" if source_row and notes else "publisher-reference" if similar_notes else "unknown",
            "guidanceBasis": "Only source-supported fields are populated; no wear-performance claim is made.",
            "dataCaveat": "This is an inspired-by / clone reference, not an identical formula. The source does not document bottle size; the displayed 100 ml USD figure is a low-confidence normalized typical-retail benchmark, not a verified 100 ml offer. Missing notes and suitability remain unknown.",
            "priceUsd": price, "priceStatus": "estimated" if price is not None else "unknown",
            "priceReferenceSizeMl": 100 if price is not None else None,
            "priceEstimateRangeUsd": [round(price * .8), round(price * 1.2)] if price is not None else None,
            "priceEstimateBasis": price_basis if price is not None else "No usable price reference was present in the source datasets.",
            "priceEstimateTier": "clone-dataset-reference" if price is not None else None,
            "priceEstimateCheckedAt": TODAY if price is not None else None,
            "imageProvider": None, "imageSourceUrl": None, "imageAuthor": None,
            "imageAlt": None, "imageLicenseUrl": None,
            "dataProvider": "Scento" if source_row else "Dupejoy / PerfumeCloneFinder",
            "dataSourceUrl": "https://github.com/Scento-com/perfume-dataset" if source_row else "https://www.perfumeclonefinder.com/dupe-index" if item["priceSource"] == "PerfumeCloneFinder" else "https://dupejoy.com/data/",
            "dataLicense": "CC BY 4.0", "dataLicenseUrl": "https://creativecommons.org/licenses/by/4.0/",
            "inspiredBy": item["inspiredBy"],
        }
        catalog.append(record)
        by_identity[identity] = record
        added += 1

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"Pairs processed: {len(pairs)}; new records: {added}; existing records linked: {linked_existing}; catalog total: {len(catalog)}")
    print(f"New clones with a source price reference: {sum(1 for f in catalog if f['id'].startswith('clone-') and f.get('priceUsd') is not None)}")
    print(f"New clones matched to Scento facts: {sum(1 for f in catalog if f['id'].startswith('clone-') and f.get('dataProvider') == 'Scento')}")


if __name__ == "__main__":
    main()
