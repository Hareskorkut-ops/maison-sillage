"""Restore licensed Scento accords as the only Scento family tags.

Ingredient notes stay in the note field and can only provide partial evidence
in the recommendation engine. This updates families without rebuilding prices,
images, or other catalog fields.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "src/data/fragrances.json"
SOURCE = ROOT / "data/sources/scento-perfumes.jsonl"
OVERRIDES = ROOT / "data/sources/family-overrides.json"

FAMILY_MAP = {
    "Wood & Root": "woody",
    "White Bloom": "floral",
    "Petal Garden": "floral",
    "Green Leaf": "fresh",
    "Velvet Sweet": "gourmand",
    "Spice Route": "spicy",
    "Sunlit Citrus": "citrus",
    "Amber & Resin": "amber",
    "Powder Veil": "floral",
    "Skin Musk": "fresh",
    "Smoke & Leather": "leather",
    "Oud Court": "woody",
    "Salt & Mineral": "aquatic",
}

source = {
    row["id"]: row
    for row in (json.loads(line) for line in SOURCE.read_text().splitlines() if line)
}
overrides = {
    row["catalogId"]: row
    for row in json.loads(OVERRIDES.read_text())
}
catalog = json.loads(CATALOG.read_text())
changed = 0
for fragrance in catalog:
    if fragrance.get("dataProvider") != "Scento":
        continue
    row = source.get(fragrance.get("providerId"))
    if row is None:
        continue
    families = sorted({
        FAMILY_MAP[group]
        for group in (row.get("family"), row.get("secondary_family"))
        if group in FAMILY_MAP
    })
    override = overrides.get(fragrance["id"])
    if override:
        families = sorted(set(families) | set(override["families"]))
        fragrance["sourceUrls"] = list(dict.fromkeys([
            *(fragrance.get("sourceUrls") or []), override["sourceUrl"]
        ]))
        fragrance["familyTagSourceNote"] = override.get("sourceNote")
    fragrance["families"] = families
    fragrance["guidanceBasis"] = (
        "Scent families follow the publisher's primary and secondary accord "
        "groups; ingredient notes remain separate. Climate and occasion are "
        "editorial mappings of seasons and time-of-day guidance."
    )
    changed += 1

CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
print(f"Updated publisher family tags for {changed} Scento fragrances.")
