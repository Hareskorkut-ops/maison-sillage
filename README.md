# MAISON SILLAGE

A responsive, local-first fragrance discovery website built with React, Vite, and CSS. No backend, accounts, database, paid API, or checkout. Nothing has been deployed or pushed.

## Run locally

Requires Node.js 20.19+ (Node 22 LTS recommended) and npm.

```sh
npm install
npm run dev
```

Open the Local URL printed by Vite, normally http://127.0.0.1:5173/. Navigation uses hash routes, so direct links such as `/#collection`, `/#discover`, `/#results`, and `/#maison` work on static hosting.

```sh
npm test          # Node's built-in test runner; no service required
npm run build    # outputs dist/
npm run preview  # inspect the production build, normally on port 4173
```

## Experience

- Editorial homepage, original locally stored hero image, family browsing, and featured fragrances.
- Six-step discovery: USD target budget with an automatic +20% ceiling, wearer (male, female, or no preference), multiple families, climate, occasion, and optional intensity. Male and female edits include unisex records; no preference includes the full catalog. Previous preserves answers.
- Up to five in-budget recommendations, with no more than three from one brand. Family/note coverage ranks three, then two, then one; price closeness breaks ties, and note-led accord coherence refines an otherwise equal match. Unknown scent data is labeled unverified instead of being reported as a confirmed zero match. Edit answers inline to regenerate.
- Search by name, brand, sourced note, or inspired-by reference. Budget, category, text, and optional source/photo checks limit the pool. The target plus 20% remains an absolute price cap; within it, family/note coverage ranks first and price closeness breaks ties, followed by climate, occasion, and intensity. The recommendation edit caps each brand at three; collection browsing stays complete. Product note combinations receive an explained editorial scent read, with no performance claims inferred. Strong falls back to moderate and cold to cool/breezy when exact preference data is unavailable. “Show matches” jumps to the live results.
- Fragrance detail dialogs with keyboard focus trapping, Escape dismissal and focus restoration. Notes, product source links and transparent price provenance are shown.
- A saved fragrance shelf. Saved IDs persist in browser localStorage; a full page refresh returns to Home and resets the questionnaire answers. Clear saved fragrances from Our maison. Storage restrictions are handled without crashing the site.
- Responsive layouts, reduced-motion support, visible keyboard focus, a working skip link, semantic controls and accessible labels.

## Catalog, evidence and current coverage

`src/data/fragrances.json` contains **1,729** unique catalog records, expanded from the original 50 with Scento data and **459 public clone / dupe pairings** from Dupejoy and PerfumeCloneFinder (CC BY 4.0). This added 404 distinct clone fragrances and linked 55 existing catalog fragrances to source-published inspired-by references. The snapshot is saved in `data/sources/scento-perfumes.jsonl`; the original 50 records remain in `data/sources/maison-curated.json`. Three independently sourced affordable leather fragrances were added: Afnan Rare Carbon, Rasasi La Yuqawam Pour Homme, and Maison Alhambra Toscano Leather.

Coverage is deliberately distinguished from verification:

- **11** records have exact listed USD prices for 100 ml bottles, with the listing URL and check date. The remaining **1,718** have low-confidence estimates. This includes 401 typical retail figures from the clone datasets normalized to a 100 ml reference even though those sources do not state bottle size, three Al Haramain brand-median estimates, and 1,314 brand-tier estimates. All estimates are labeled and have an approximate ±20% band; none is presented as a verified item-specific offer.
- **Every catalog entry (1,729/1,729)** has an image reference. 33 are locally stored Open Beauty Facts community photographs under CC BY-SA 3.0. Every entry has a displayable visual: 229 remote bottle-photo references matched through image search, 548 hotlinked product-page images, 33 openly licensed community photos, and 919 original local bottle illustrations used as the primary image where no product photo was available. Every entry also has a local illustration fallback if its remote product image fails to load. The illustrations are clearly labeled as studies, not exact package photographs. Product image cards use one warm ivory scene inspired by the Libre Le Parfum product photo: a softly lit wall and pale stone plinth. Source links are shown in details; remote-image reuse rights are not confirmed.
- Imported key notes are marked `publisher-sourced`, with a source URL and attribution. They were not independently checked one by one against manufacturer pages. Existing manually checked records remain separate.
- Family tags map only the publisher's primary and secondary accord groups, with source-linked brand overrides in `data/sources/family-overrides.json` when a manufacturer explicitly classifies a particular variant. Ingredient notes stay separate; a note associated with a selected family can contribute limited partial match credit, but cannot make a fragrance a full family match. Climate tags map published seasons; occasion tags adapt daytime/evening guidance. These are interpretations, not performance measurements.
- Open Beauty Facts photo identity matching rejects known flankers, deodorants, body products and ambiguous concentration matches. Product photography can include packaging. Detail views link every image to its source; only Open Beauty Facts photographs carry a verified image license in this project.

Gender labels are conservative: explicit wording in a fragrance name or product-image listing is used where present; unisex records appear under both Male and Female. Records with no explicit label remain unclassified and visible in the full collection. The current snapshot has 99 male, 52 female, 18 unisex and 1,560 unlabeled records; Libre Le Parfum has a YSL product-page override.

All catalog entries have a price value for budget filtering. The 11 listed values are direct product prices checked on 26 October 2026, including the Macy's 100 ml equivalent of Versace Dylan Blue at $129 and Ulta's 100 ml equivalent of Azzaro The Most Wanted Parfum at $145. Clone benchmark prices are taken from the linked dataset, but its bottle size is unspecified; we normalize them as low-confidence 100 ml references for matching and call out this limitation. The rest are broad brand-tier or brand-median estimates—not averages observed across distributors—and should be treated as provisional. Shipping, tax and current availability are excluded. The `Show only source-listed prices` filter restricts browsing to the 11 observed 100 ml listings.

No runtime API, paid service or backend is required. The catalog is a separate local JSON asset loaded with `fetch` from the same static site. Google Fonts supplies the typefaces with local system fallbacks. All 1,729 entries have a local bottle-study SVG fallback, and 33 Open Beauty Facts photos are stored under their open license. The 777 real product-image references are hotlinked and may change or become unavailable; the interface switches to the local fallback if one fails. Public product pages were queried for image references; no retailer images were copied into the repository.

### Rebuilding the local catalog

```sh
python3 scripts/import-catalog.py
python3 scripts/reclassify-scento-families.py
python3 scripts/import-photos.py
python3 scripts/estimate-prices.py
python3 scripts/import-fragrance-dupes.py
python3 scripts/import-product-image-references.py
python3 scripts/generate-template-bottle-art.py
python3 scripts/apply-gender-tags.py
```

The first command is offline, using the included snapshot. Run the price estimator before the clone importer so clone-dataset benchmarks are retained. The photo and image-reference importers use cached public product data when present; uncached image references require network access and `curl`. The clone importer merges the included CC BY 4.0 CSV sources and deduplicates names. The product-image reference importer caches direct image URLs and keeps each source page. The image-reference command applies saved product-photo matches and creates consistent, labeled bottle-study illustrations for entries with only a generic logo or share graphic. The final gender-tag command applies explicit product-listing labels and source-linked exceptions; it leaves uncertain records unclassified. `data/sources/photo-review.json` remains the manually reviewed allowlist for licensed community photos. Do not approve a photo merely because a product name partially overlaps.

See `DATA-LICENSES.md` and `ASSETS.md` for attribution, modifications and licensing. No code or data was pushed or deployed.

## Closest-match recommendation rules

Pure functions live in `src/recommend.js`.

1. The user's entered budget is the target. The **hard ceiling is target × 1.20**, rounded to cents: $75 → $90. No fragrance above that price is eligible; preferences never widen the price limit.
2. Within the price cap, family/note coverage ranks first: match all selected families when possible, then two, then one. Every selected family contributes equally. A direct family tag or a note matching a whole normalized phrase counts as evidence; ambiguous overlaps such as treating orange blossom as citrus or ambergris as amber are explicitly excluded. Note-based matches are named. Records with no family tags and no note data are unverified, not reported as confirmed zero matches, and rank behind records with known scent data.
3. Climate and occasion each contribute 20 points. Exact tags score highest; nearby climates and related occasions receive partial credit instead of excluding the fragrance.
4. Optional intensity contributes 5 points. An exact intensity scores highest, a different one lower, and missing intensity is treated as unknown rather than a veto.
5. Price proximity breaks ties between fragrances with the same family/note coverage. A note-led accord blend refines candidates only when their family coverage and price distance are otherwise tied. Budget also contributes 15 points and peaks at the user's target. It declines with distance above or below the target; all prices above the hard +20% ceiling are excluded.
6. Return up to five ranked in-budget fragrances, with no more than three per brand. If brand diversity or the price cap leaves fewer than five, show all remaining eligible recommendations; never exceed either rule.
7. The score is a transparent ordering aid, not a probability of liking a scent. When family data is unknown, that component is shown as unverified and the displayed score is normalized over recorded criteria. Price-estimate uncertainty is shown on each estimated result.

Catalog browse filters remain exact on the selected tags. Recommendation matching is intentionally softer. A source-listed-only checkbox filters out modeled price estimates; the photo-only filter is independent.

Results provide a prefilled inline editor for budget, families, climate, occasion and optional intensity. The recommendation list previews and re-sorts as answers change; Apply changes saves the new answers and Cancel returns to the applied profile. Opening the editor scrolls it into view and focuses the budget field. Browsing the exact profile carries those selections into the catalog. No repeated questionnaire is required.

The automated tests cover equal family weights, phrase-safe note evidence, note-combination impressions, unknown scent-data handling, family-coverage-first ranking, the three-per-brand cap, climate/occasion proximity, soft intensity, the $75/$90 hard-price boundary, five results, short price-qualified lists, and the user's prior profile.

## Netlify (when ready)

`netlify.toml` is configured with:

- Build command: `npm run build`
- Publish directory: `dist`
- SPA fallback: `/*` → `/index.html` (200)

After deciding to publish, import this folder/repository into Netlify and use those settings with Node 22. No environment variables are required. Alternatively build locally and upload `dist/`. This project has not been deployed or connected to GitHub.

## Files

- `src/main.jsx`: pages, questionnaire, catalog and dialogs.
- `src/styles.css`: responsive styling and photo presentation.
- `src/recommend.js`: scoring and filters.
- `src/recommend.test.js`: matching and data integrity tests.
- `src/data/fragrances.json`: curated local catalog.
- `public/images/hero.jpg`: optimized original hero image.
- `ASSETS.md`: asset provenance and generation prompt.
