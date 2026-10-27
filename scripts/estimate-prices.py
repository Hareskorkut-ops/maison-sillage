#!/usr/bin/env python3
"""Fill missing 100 ml reference prices with explicit, editable house-tier estimates.

These are discovery estimates, not quotations or sourced product-level prices.
Keep them marked as estimates and do not attach fabricated retailer URLs.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src/data/fragrances.json"
TODAY = "2026-10-26"

# Typical full-bottle US retail tiers for a 100 ml reference. These are coarse
# house-level anchors; every estimate is labeled and given a +/- 20% band.
TIERS = {
    "accessible-arabian": 65,
    "arabian-premium": 120,
    "designer-accessible": 105,
    "designer-core": 155,
    "designer-premium": 195,
    "niche-accessible": 190,
    "niche-core": 275,
    "niche-premium": 350,
    "niche-haute": 550,
}

GROUPS = {
    "accessible-arabian": "Afnan, Armaf, Lattafa, Maison Alhambra, Rasasi, Nabeel, Ajmal, Al Haramain, Arabian Oud, Swiss Arabian, Orientica",
    "arabian-premium": "Amouage, Kajal, Widian, Stéphane Humbert Lucas 777",
    "designer-accessible": "Ariana Grande, Billie Eilish, Elizabeth Arden, Jennifer Lopez, Kenneth Cole, Nautica, Zara, Tommy Hilfiger, Sol de Janeiro",
    "designer-core": "Azzaro, Boucheron, Burberry, Cacharel, Calvin Klein, Carolina Herrera, Davidoff, Dolce&Gabbana, Dsquared2, Elie Saab, Giorgio Armani, Givenchy, Gucci, Hugo Boss, Issey Miyake, Jean Paul Gaultier, Jimmy Choo, Jo Malone London, Kenzo, Lacoste, Lancôme, Lalique, Marc Jacobs, Michael Kors, Moschino, Mugler, Narciso Rodriguez, Nina Ricci, Rabanne, Ralph Lauren, Roberto Cavalli, Rochas, Salvatore Ferragamo, Trussardi, Valentino, Versace, Viktor&Rolf, Zadig & Voltaire, Gisada",
    "designer-premium": "Acqua di Parma, Annick Goutal, Atelier Cologne, Atelier des Ors, Balmain, Bvlgari, Carner Barcelona, Cartier, Chanel, Chloé, Comme des Garçons, Dior, Etro, Floris London, Hermès, Jo Malone London, Loewe, Miu Miu, Prada, Santa Maria Novella, Serge Lutens, Sisley, Van Cleef & Arpels, Yves Saint Laurent",
    "niche-accessible": "Etat Libre d'Orange, Escentric Molecules, Fugazzi, Juliette Has a Gun, Mancera, Montale, Molinard, Ormonde Jayne, Tauer Perfumes, The Different Company, James Heeley, Nicolaï",
    "niche-core": "Byredo, Creed, Diptyque, Eisenberg, Ex Nihilo, Frédéric Malle, Giardini di Toscana, Houbigant, Initio Parfums Prives, Jovoy Paris, Kayali, Kilian Paris, Le Labo, Maison Crivelli, Maison Francis Kurkdjian, Maison Margiela, Memo Paris, Nishane, Pantheon Roma, Parfums de Marly, Penhaligon's, Profumum Roma, Roja Parfums, Tiziana Terenzi, Vilhelm Parfumerie, Zoologist Perfumes, Caron, Atkinsons, Orto Parisi, Sospiro",
    "niche-premium": "Fragrance du Bois, Marc-Antoine Barrois, Matière Première, Nasomatto, Parfums Dusita, Robert Piguet, Tiziana Terenzi",
    "niche-haute": "Boadicea the Victorious, Clive Christian",
}
GROUPS["designer-premium"] += ", Guerlain, Jean Patou, Maison Margiela Fragrances, Montblanc"
GROUPS["niche-premium"] += ", Tom Ford"
BRAND_TIER = {}
for tier, names in GROUPS.items():
    for name in names.split(", "):
        BRAND_TIER[name] = tier

# Specific, source-backed 100 ml regular/list prices already present in the
# catalog are retained. These estimate anchors only fill nulls.
KNOWN_HOUSE_100ML = {
    "Lattafa": 45, "Afnan": 60, "Chanel": 173, "Prada": 136,
    "Elizabeth Arden": 52, "Dior": 185, "Amouage": 395,
    # SHL's common US retailer bottle is 50 ml ($255 at Luckyscent); convert
    # to a 100 ml reference so a 50 ml price cannot masquerade as a budget fit.
    "Stéphane Humbert Lucas 777": 510, "Tom Ford": 500,
    "Byredo": 390, "Hermès": 155, "Yves Saint Laurent": 180,
}

# Fresh exact 100 ml listings checked on 26 October 2026. Lattafa's US shop
# identifies these offers as direct from Lattafa; listed, non-sale price shown.
OBSERVATIONS = {
    "ms-004": (44.99, "https://www.lattafa-usa.com/products/khamrah"),
    "ms-008": (44.99, "https://www.lattafa-usa.com/products/yara"),
    "ms-009": (44.99, "https://www.lattafa-usa.com/products/eclaire"),
    "ms-010": (44.99, "https://www.lattafa-usa.com/products/fakhar"),
    "ms-046": (44.99, "https://www.lattafa-usa.com/products/asad"),
    "scento-versace-dylan-blue-pour-homme": (129, "https://www.macys.com/shop/product/versace-mens-pour-homme-dylan-blue-eau-de-toilette-spray-3.4-oz?ID=2903352"),
    "scento-azzaro-the-most-wanted-parfum": (145, "https://www.ulta.com/p/most-wanted-parfum-pimprod2032753?sku=2595269"),
}

def rounded(value):
    return int(round(value / 5) * 5)

def product_adjustment(item):
    n = item["name"].casefold()
    # Collection-specific luxury lines generally command a higher regular list price.
    if any(term in n for term in ("extrait", "parfum intense", "elixir", "absolu", "parfum concentration")):
        return 1.18
    return 1.0

def main():
    catalog = json.loads(CATALOG.read_text())
    estimated = 0
    unknown_house = set()
    for item in catalog:
        # Make the importer idempotent: clear a previous run's generated fields.
        if item.get("priceStatus") == "estimated":
            for key in ("priceUsd", "priceStatus", "priceReferenceSizeMl", "priceEstimateRangeUsd",
                        "priceEstimateBasis", "priceEstimateTier", "priceEstimateCheckedAt"):
                item.pop(key, None)
        elif item.get("priceStatus") == "listed" and not item.get("priceSourceUrl"):
            # Repair the initial importer run, which predated priceStatus and
            # had temporarily mislabeled generated values as listed prices.
            item.pop("priceUsd", None)
            item.pop("priceStatus", None)
            item.pop("priceReferenceSizeMl", None)
        if item.get("priceUsd") is not None and item.get("bottleSizeMl") != 100:
            # The application compares a standard 100 ml reference. Keep an
            # exact listed amount only when the cited bottle itself is 100 ml.
            item.pop("priceUsd", None)
            item.pop("priceStatus", None)
            item.pop("priceReferenceSizeMl", None)
            item["priceSourceUrl"] = None
        if item["id"] in OBSERVATIONS:
            price, url = OBSERVATIONS[item["id"]]
            item.update(priceUsd=price, bottleSizeMl=100, priceReferenceSizeMl=100,
                        priceStatus="listed", priceSourceUrl=url, priceCheckedAt=TODAY, verifiedAt=TODAY)
        # These two earlier rows used discount-oriented third-party shops. They
        # are deliberately replaced with labeled estimates per the user's brief.
        if item["id"] in {"ms-052", "ms-053"}:
            item["priceUsd"] = None
            item["priceSourceUrl"] = None
        if item.get("priceUsd") is not None:
            item["priceStatus"] = "listed"
            item.setdefault("priceReferenceSizeMl", item.get("bottleSizeMl"))
            item.setdefault("priceCheckedAt", TODAY)
            item.setdefault("verifiedAt", TODAY)
            for key in ("priceEstimateRangeUsd", "priceEstimateBasis", "priceEstimateTier", "priceEstimateCheckedAt"):
                item.pop(key, None)
            continue

        brand = item["brand"]
        tier = BRAND_TIER.get(brand)
        if tier is None:
            # Deliberately conservative designer-tier fallback; still called out
            # as a low-confidence estimate in every product record and the UI.
            tier = "designer-core"
            unknown_house.add(brand)
        anchor = KNOWN_HOUSE_100ML.get(brand, TIERS[tier])
        amount = rounded(anchor * product_adjustment(item))
        item["priceUsd"] = amount
        item["priceStatus"] = "estimated"
        item["priceReferenceSizeMl"] = 100
        item["priceEstimateRangeUsd"] = [rounded(amount * .8), rounded(amount * 1.2)]
        item["priceEstimateBasis"] = (
            "Approximate mid-market 100 ml US retail reference based on a broad house-price tier; "
            "no item-specific retailer listing was verified. Low-confidence discovery estimate, not a quote."
        )
        item["priceEstimateTier"] = tier
        item["priceEstimateCheckedAt"] = TODAY
        # A product source URL is not a pricing source. Do not add one for estimates.
        item["priceSourceUrl"] = None
        estimated += 1

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"Catalog: {len(catalog)}; modeled 100 ml estimates added: {estimated}; "
          f"still unknown: {len([x for x in catalog if x.get('priceUsd') is None])}")
    if unknown_house:
        print("Houses using conservative fallback tier: " + ", ".join(sorted(unknown_house)))

if __name__ == "__main__":
    main()
