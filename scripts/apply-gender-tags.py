#!/usr/bin/env python3
"""Apply explicit gender labels from product naming and a small sourced override list."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src" / "data" / "fragrances.json"
OVERRIDES = ROOT / "data" / "sources" / "gender-overrides.json"

UNISEX = re.compile(r"\b(?:unisex|genderless|for everyone|all genders)\b", re.I)
MALE = re.compile(r"\b(?:men(?:'s)?|male|masculine|for him|pour homme|homme|hombre)\b", re.I)
FEMALE = re.compile(r"\b(?:women(?:'s)?|female|feminine|for her|pour femme|femme|mujer)\b", re.I)


def main():
    fragrances = json.loads(CATALOG.read_text())
    overrides = {item["catalogId"]: item for item in json.loads(OVERRIDES.read_text())}
    counts = Counter()

    for fragrance in fragrances:
        # Only examine identifying/product-listing fields. Notes and descriptive copy
        # can mention another gender and should not determine who the product is for.
        evidence = " ".join(
            str(value)
            for value in [
                fragrance.get("name"),
                fragrance.get("imageAlt"),
                fragrance.get("imageAuthor"),
                fragrance.get("imageSourceUrl"),
                *(fragrance.get("sourceUrls") or []),
            ]
            if value
        )
        has_male = bool(MALE.search(evidence))
        has_female = bool(FEMALE.search(evidence))
        if UNISEX.search(evidence) or (has_male and has_female):
            gender = "unisex"
        elif has_male:
            gender = "male"
        elif has_female:
            gender = "female"
        else:
            gender = None

        fragrance["gender"] = gender
        fragrance["genderBasis"] = (
            "explicit product or image-listing wording" if gender else None
        )

        override = overrides.get(fragrance["id"])
        if override:
            fragrance["gender"] = override["gender"]
            fragrance["genderBasis"] = "brand product page"
            fragrance["genderSourceUrl"] = override["sourceUrl"]
            fragrance["genderSourceNote"] = override["sourceNote"]
            fragrance["sourceUrls"] = list(
                dict.fromkeys([*(fragrance.get("sourceUrls") or []), override["sourceUrl"]])
            )

        counts[fragrance["gender"] or "unclassified"] += 1

    CATALOG.write_text(json.dumps(fragrances, ensure_ascii=False, indent=2) + "\n")
    print(f"Tagged {len(fragrances)} fragrances: {dict(counts)}")


if __name__ == "__main__":
    main()
