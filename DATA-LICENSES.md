# Data and photograph attribution

## Scento fragrance data

Scento — https://www.scento.com/perfume-database

Source: https://github.com/Scento-com/perfume-dataset
Snapshot: 21 October 2026. License: Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/ . The publisher's license notice is retained in `data/sources/SCENTO-LICENSE.txt`.

Changes: selected factual fields were normalized into the local schema; existing curated identities were deduplicated; family tags were mapped to the site's taxonomy with explicit note-term rules; seasonal and daytime guidance was mapped editorially to climate and occasion tags. Missing prices, bottle sizes, intensity and images are not claimed as Scento data. These adaptations do not imply publisher or fragrance-house endorsement.

The imported records retain `dataProvider`, `dataLicense`, `dataLicenseUrl` and their original product source URL. Notes are publisher-sourced, not independently manufacturer-verified by this project.

## Clone / inspired-by pairing data

- Dupejoy, “Most Duped Fragrances” dataset: https://dupejoy.com/data/ . CSV snapshot: `data/sources/dupejoy-fragrance-dupes.csv`. Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ .
- PerfumeCloneFinder, “Dupe Index” dataset: https://www.perfumeclonefinder.com/dupe-index . CSV snapshot: `data/sources/perfumeclonefinder-clones.csv`. Licensed under CC BY 4.0.

The pairing labels, similarity references, note overlaps, and typical USD retail benchmarks are publisher-provided and were merged, normalized, and deduplicated by brand/name. A similarity score is not evidence that formulas or smells are identical. Clone dataset prices do not state a bottle size; the application shows them as low-confidence 100 ml-normalized estimates and explicitly warns users to verify the actual size and current offer. Many clones have no publisher-verified notes or suitability tags, so these remain unknown. The dataset credits are linked in product details.

## USD price records and estimates

The 9 `priceStatus: "listed"` entries are 100 ml prices recorded from the linked brand or retailer product page, with `priceCheckedAt` and `priceSourceUrl`. The other 1,316 pre-expansion records used an explicitly labeled low-confidence midpoint estimate (`priceStatus: "estimated"`) for a 100 ml reference. Estimates are generated from a manually maintained broad house-price tier, include an approximate ±20% range, and do not have item-specific price URLs. They are modeled values supplied because the user requested approximate budget coverage; they are not distributor averages, offers, or checkout prices. The application uses them for filtering and recommendations but labels them on cards and in detail views. `scripts/estimate-prices.py` generates these estimates and applies the small set of fresh 100 ml listings checked on 26 October 2026. Check the linked listing before purchase; currency, shipping, tax, availability, concentration and bottle variants can change.

## Open Beauty Facts photographs and metadata

Contains information from Open Beauty Facts, https://world.openbeautyfacts.org/ , made available under the Open Database License 1.0: https://opendatacommons.org/licenses/odbl/1-0/ . The combined database in `src/data/fragrances.json` is offered under ODbL 1.0 for its database rights; underlying Scento contents retain CC BY 4.0 and its attribution requirements. Application code is separate from these data licenses.

The barcode identity list `data/sources/open-beauty-facts.csv` was obtained from parfica's open-data repository, https://github.com/parfica/parfica-open-data . Parfica's own identity columns are CC0; Open Beauty Facts-derived barcode/product links are ODbL 1.0. The API responses are cached under `data/sources/obf/`.

Product photographs are separate works under Creative Commons Attribution-ShareAlike 3.0, https://creativecommons.org/licenses/by-sa/3.0/ . The Open Beauty Facts presentation documents CC BY-SA reuse for product photos: https://wiki.openfoodfacts.org/images/e/ed/OpenBeautyFacts.pdf . They are downloaded from the public Open Beauty Facts JSON API, with the selected original image uploader retained as author, and are displayed without pixel modifications (CSS containment only). Credit the named contributor and Open Beauty Facts, link the product source page and license, and retain share-alike for adaptations. The detail dialog includes this attribution.

`data/sources/photo-review.json` is the manually reviewed display allowlist. The image manifest records per-image origins. Known deodorants, unrelated flankers and ambiguous edition matches were rejected. Unused downloaded candidate images are not evidence that a product photo has been approved for display.

## Original brand artwork

The hero image is a generated fictional still life. It is not a photograph of a catalog fragrance. Its provenance and prompt are in `ASSETS.md`.


## External product-image references

777 catalog image references are remote: 229 product bottle images found through image search and linked to the result page, plus 548 product/source-page images. Their files are not copied into the repository and reuse rights are not confirmed. Every record also has an original MAISON SILLAGE bottle-study SVG as a local fallback. 919 of these illustrations are the primary image where no suitable product photo was available; the rest appear automatically if a remote photo fails. The 33 Open Beauty Facts photos are local under CC BY-SA 3.0. Bottle studies are stylistic illustrations labeled with the catalog name, not photographs or claims about exact packaging. Product-photo search mappings are retained in `data/sources/product-image-search-overrides.json`; direct image URLs and source pages are retained in the catalog and `data/sources/product-image-references.json`.

These remote image works are not included in the repository, and this project has not established a license or reproduction permission for them. They remain hosted by their respective publishers or rights holders. The site links back to the source and does not label these images as licensed. Confirm the applicable rights and hotlink terms before public or commercial distribution. Image hosts may change or remove their URLs at any time.
