# MEER Chip Check

Chip lookup + compare tool for the mobile shop. Type a model code or name
(e.g. KM6, X6840, "Spark 40 Pro") and see its chip; compare two models to
see if their chips match — for tool model selection.

**Live web page:** https://hamzaagsm.github.io/gsmtool/chip-check/
(web page is hosted in the `Hamzaagsm/gsmtool` repo under `chip-check/`)

## What it does

- **Lookup:** model code or name → brand, name, code, chip (Helio name +
  MediaTek MT number + process nm + CPU + GPU where known), Android
  version, servicing route where the DB has it.
- **Compare:** two models → verdict in plain Roman Urdu:
  - **MATCH** — same MT number (same chip)
  - **FAMILY** — same MT family, e.g. MT6789 vs MT6789H (usually works, try it)
  - **NO MATCH** — different chip families
  - Every compare result carries the warning: "Firmware hamesha apne model
    ki — chip match hona firmware match hona nahi hai."
- UI in Roman Urdu; chip names in English. Works fully offline — the whole
  model database (2,496 models) is embedded in the page.

## Data

- Model data: MEER Tool Pro's `tools/mdm-models.json` (2,530 rows → 2,496
  after dedupe by code, preferring verified rows).
- Chipset → MT number mapping: `web/mt-mapping.json` — **verified mappings
  only** (Wikipedia "List of MediaTek processors" + MEER coverage files +
  GSMArena spot-checks). 242 exact MediaTek mappings, 290 non-MTK chipsets
  keyed by vendor+chip, 16 unverified (variant splits + Helio G99+).
  Unverified chips show the Helio name with MT marked "verify nahi hua" —
  never guessed.
- Anchors: Helio G81/G85/G88 = MT6769; Helio G99 = MT6789; Helio G100 =
  MT6789H; Helio G200 = MT6789; Helio G70 = MT6769; Dimensity 7400 = MT6878.

## Layout

- `web/` — page generator (`build_page.py`), template (`template.html`),
  live verifier (`verify_page.py`), MT mapping + report.
- `android/` — WebView wrapper app (package `com.albadar.chipcheck`,
  minSdk 24, targetSdk 34, NO internet permission, loads the page from
  `assets/chip-check/index.html`).
- `build-apk.sh` — builds the APK with aapt2/d8/apksigner (needs Android
  SDK 34 + JDK 17; signing keystore is kept outside any repo).

## Rebuild the page

    cd web
    python3 build_page.py --mapping mt-mapping.json --out index.html
    python3 verify_page.py --file index.html

Self-checks (must all pass): KM6 → Helio G100 Ultimate / MT6789H;
X6840 → Helio G81 Ultimate / MT6769; CN5c → Helio G200 / MT6789;
X6885 → Helio G200 / MT6789. Compares: KM6 vs X6840 = NO MATCH;
CN5c vs X6885 = MATCH; KM6 vs KM7 = FAMILY.

## Rules

- No paid routes, prices, or "paid" wording anywhere.
- No other tool opens inside it; no vendor code.
- Signing keystore lives only in the builder's secure store, never in a repo.
