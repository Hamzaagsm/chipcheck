# MEER Chip Check — MT Mapping Verification Report

**Built:** 2026-11-18 (PKT) · **Source DB:** `~/workspace/hamza-tool-pro/tools/mdm-models.json`
(2,530 models, **548 distinct `chipset` strings**)
**Output:** [`mt-mapping.json`](sandbox:/workspace/chipcheck/mt-mapping.json)
**Builder (reproducible):** [`build_mapping.py`](sandbox:/workspace/chipcheck/build_mapping.py)

## Counts

| Bucket | Exact DB strings | Total keys incl. normalized lookups |
|---|---|---|
| `mapped` (MediaTek → verified MT number) | **242** | 296 |
| `non_mtk` (other vendors, by name) | **290** | 336 |
| `unverified` | **16** | 16 |
| **Total** | **548** | **648** |

242 + 290 + 16 = 548 — every distinct DB chipset string is accounted for exactly once.
100 normalized lookup keys were added (vendor-prefix-stripped, parenthetical-stripped,
and suffix-stripped forms, e.g. `Helio G100` alongside `Helio G100 Ultimate`,
`Dimensity 6100+` alongside `Dimensity 6100 Plus`). Normalized keys never overwrite an
exact DB string's entry. 69 distinct MT numbers appear in `mapped`.

Every `mapped` entry carries a `source` naming where the MT number was verified, plus
`nm`/`cpu`/`gpu` where the source gives them (omitted, never guessed, where unknown),
and a `variant` field with the exact part number(s) where they differ from the base
(e.g. G200 → `MT6789`, variant `MT6789T`).

## Method

1. **Primary source:** Wikipedia, "List of MediaTek systems on chips"
   (`en.wikipedia.org/wiki/List_of_MediaTek_systems_on_chips`, page crawled
   2026-11-05) — Helio A/P/G/X and Dimensity 700–9600 tables read in full.
   It gives the MT part number, fab node, CPU and GPU per chip.
2. **Spot checks** (one search each) for chips Wikipedia lists without a part
   number or with OEM suffix variants: 91mobiles, NanoReview, DeviceInfo.app,
   CPU-Boss, Radargit, Once Human official requirements, a USPTO patent-filing
   table, Geekbench listings, and real tool logs (F64, Android Multi Tool).
3. **Suffix-variant rule** (verified, not assumed): OEM suffixes
   (Ultra/Ultimate/Max/Pro/Plus/Turbo/Energy/Super/Extreme/AI) denote the same
   base silicon. Verified cases: 7200 Pro = MT6886, 7300 Energy = MT6878,
   7300 Pro = MT6878, 7400 Turbo = MT6878, 7500 Turbo = MT6881,
   7350 Pro = MT6886, 8350 Extreme = MT6897, 6360 Max = MT6835c,
   7025 Ultra = MT6855, 8000 Max / 8100 Max / 8100 Ultra = MT6895,
   8200 Ultra = MT6896ZB, 8300 Ultra = MT6897, 7200 Ultra = MT6886,
   G92 Max = MT6769I, G99 Ultra/Ultimate = G99.
4. **Bare MT strings** in the DB (e.g. `MT6835`, `MT6897`) map to themselves.
5. **Non-MediaTek** strings get vendor + chip name as-is, no MT number.
6. **Never guessed:** anything unconfirmed is in `unverified` (see below).

## Anchor checks — all 4 confirmed ✅

| Model | DB chipset | Mapping | Verified by |
|---|---|---|---|
| KM6 — Tecno Spark 40 Pro | Helio G100 Ultimate | **MT6789H** | Wikipedia (G100 = MT6789H/I/J) |
| X6840 — Infinix Smart 20 | Helio G81 Ultimate | **MT6769** | Wikipedia (G81 = MT6769J/L/S) |
| CN5c — Tecno Camon 50 Pro | Helio G200 Ultimate | **MT6789** | Wikipedia (G200 part MT6789T) |
| X6885 — Infinix Hot 60 Pro | Helio G200 | **MT6789** | Wikipedia (G200 part MT6789T) |

KM7 (Spark 40 Pro+, Helio G200) also maps to MT6789. Helio G70 — flagged
"verify" by the parent — is confirmed **MT6769** on Wikipedia (variant MT6769V/CB).

## Dimensity 7400 conflict — RESOLVED ✅

**Answer: Dimensity 7400 = MT6878.** Settled by **Wikipedia**: its Dimensity 7400 row
lists `MT6878V/TZA, MT6878V_B/TZA, MT6878V_C/TZA`, and its Dimensity 1050 row lists
`MT6879` — so MT6879 belongs to the Dimensity 1050 (and the 7030, its rename), not
the 7400. Corroborated by the DB's own X6876 note ("both MT6878", 7 sources
unanimous) and by Geekbench (Vivo V80 FE, Dimensity 7400-Turbo = MT6878).
**`mtk_2026_coverage.py` is wrong here** — its `MT6879 = Dimensity 7400` line and
`DIMENSITY 7400 → MT6879` entry need correcting to MT6878.

## Other conflicts found (and how resolved)

1. **Dimensity 8200 vs 8000/8100 — `mtk_2026_coverage.py` has them swapped.**
   Wikipedia: Dimensity **8200 = MT6896**, Dimensity **8000/8100 = MT6895**.
   The coverage file says the opposite (MT6895 = 8200, MT6896 = 8000/8100).
   The DB itself already flagged this: note on PHV110 (`MT6895`) says
   "Dimensity 8200 (chip ID MT6895 per UnlockTool list; naming conflict §6.1)".
   Mapped per Wikipedia: 8200/8250 → MT6896; 8000/8100 (+Max/Ultra) → MT6895.
2. **Dimensity 7200 Pro — DB string embeds the wrong MT number.**
   `MediaTek Dimensity 7200 Pro (MT6878)` (Phone (2a) row; its note repeats
   "MT6878 (Dimensity 7200 Pro)"). Three sources say **MT6886**: the USPTO
   patent-filing table (Daedalus Prime v. MediaTek), 91mobiles (Model No
   MT6886), and a real Android Multi Tool log on a Nothing Phone (2a)
   (ChipId MT6886). Mapped to MT6886; the embedded MT6878 is the 7300's number.
3. **Dimensity 8050 — DB route notes assume the wrong class.**
   Notes on X6710/CK8n/CK9n/AD11 say "D8050/MT6896 class rule". Wikipedia:
   8050 is the **Dimensity 1300 renamed = MT6893**. Mapped to MT6893.
4. **Dimensity 9600M — sources split MT6994 vs MT6993.**
   Wikipedia lists 9600M with no part number. NanoReview (×3) and 91mobiles
   (×4) say **MT6994**; OTON Technology and SiliconCat argue it is a rebadged
   9500 die (**MT6993**, same clocks). Mapped to MT6994 on the majority of
   aggregators plus the MT6993/6994/6995 sequence; the conflict is recorded in
   the entry's `note` — **flag for re-check when a device log appears**.
5. **`MT6768 Helio G70` — token and label disagree.**
   The explicit MT token (MT6768 = Helio P65) conflicts with the "Helio G70"
   label (G70 = MT6769 per Wikipedia). Mapped to the explicit token **MT6768**;
   the disagreement is recorded in the entry's `note`.
6. **`Helio P20 (MT6757CD)` — token is the P25 part.**
   P20 = MT6757; MT6757CD is the P25/P25T part. Base is MT6757 either way;
   mapped to MT6757 with variant MT6757CD and a note.
7. **`Helio G37 (MT6765)` vs Wikipedia's G37 = MT6765H.**
   Mapped to the string's explicit token MT6765; the normalized key `Helio G37`
   keeps the exact DB string's MT6765H (exact strings win over normalized keys).
8. **`MT6580A (MT6580P per MobileWithDrivers — Conflict 3)`** and
   **`MT6737 (MT6737W per Spec411)`** — in-string source conflicts; the primary
   token (MT6580A / MT6737) is kept, the alternative is recorded in `note`.
9. **X6840 note** — a Fenix log once claimed D9400/MT6991 for this code while
   GSMArena says Helio G81 Ultimate; the DB kept GSMArena's. Anchor mapping
   (MT6769) follows GSMArena + Wikipedia, as the parent directed.

## Notable non-obvious mappings (easy to get wrong)

- **Dimensity 7300e = MT6858**, NOT MT6878 — it is the 7100-family part
  (Wikipedia: MT6858T). The 7300/7300X/7360/7400 are MT6878.
- **Dimensity 7030 = MT6879** (1050 renamed); **7050 = MT6877** (1080 renamed);
  **7020 = MT6855** (930 renamed); **6020 = MT6833** (700 renamed);
  **6080 = MT6833** (810 renamed); **8020 = MT6891** (1100 renamed).
- **Dimensity 6360 Max = MT6835** (variant MT6835c, DeviceInfo.app) —
  Wikipedia's 6360 row has no part number.
- **Dimensity 7500 Turbo = MT6881** (91mobiles); base 7500 = MT6881 (Wikipedia).
- **Dimensity 9400e = MT6989** (9300-family part, variant MT6989T_e), not MT6991.
- **Dimensity 9500s = MT6991** (9400-family); **9500 = MT6993**;
  **9600 Pro = MT6995** (2nm).
- **Helio P25 Lite = MT6757** (variant MT6757CD, confirmed by Kimovil/Mobosdata/
  FindPare).
- **Helio G50 = MT6765V** (Wikipedia + NanoReview); **G36 = MT6765V**;
  **G37 = MT6765H**; **G35 = MT6765G**; **G25 = MT6762G** (distinct from P22's
  MT6762).

## Unverified (16 strings) — why each

| String | Reason |
|---|---|
| `Helio G99+` | **Only genuinely unmapped chip.** Wikipedia lists G99+ (Q3 2026, LPDDR5X) with no part number; no web source gives one (MediaTek's own Helio page lists it with no MT number). Likely MT6789-family but NOT confirmed — not guessed. |
| `Helio A22 (MT6761, 2 GB) / Helio A25 (MT6762D, 3–4 GB)` | Variant split: MT6761 vs MT6762 |
| `Helio A22 (MT6761, 2 GB) / Helio P22 (MT6762, 4 GB)` | Variant split: MT6761 vs MT6762 |
| `Helio G25 (MT6762G) / Helio A22 (MT6761)` | Variant split: MT6762G vs MT6761 |
| `Helio G37 (MT6765V/CB, X6816) / Unisoc T610 (X6816C)` | Variant split, mixed vendors |
| `Helio P35 / Kirin 710A (variants)` | Variant split, mixed vendors |
| `MediaTek Dimensity 1300 (China) / 6020 (India variant) — variant split` | Variant split: MT6893 vs MT6833 |
| `MediaTek Helio P22 (Helio A22 in African version)` | Region variant: MT6762 vs MT6761 |
| `MediaTek MT6580 (1 GB ver.) / Helio A22 (2 GB ver.) — see conflict` | Variant split: MT6580 vs MT6761 |
| `MediaTek MT6737M / MT6580M` | Variant split: MT6737M vs MT6580M |
| `Snapdragon 8 Gen 1 (China: Dimensity 9000, per W-O text)` | Region variant, mixed vendors |
| `Snapdragon 8 Gen 1 or Dimensity 9000 by region/variant` | Region variant, mixed vendors |
| `Unisoc SC9863A (version 1) / MediaTek Helio A22 (version 2) — dual-chipset model, per GSMArena` | Dual-chipset model, mixed vendors |
| `Unisoc T606 (variant-reported; Helio G25 also reported)` | Variant-reported, mixed vendors |
| `Unknown` / `unknown` | No chipset information in the DB |

Note: two variant-split strings WERE mapped because both variants share one MT
number — `Dimensity 720 / Dimensity 800U (variants)` → MT6853, and
`Helio P60 (Global) / Helio P70 (India)` → MT6771. The `unverified` strings
above cannot be reduced to a single MT number without guessing which variant
a given phone has; the app should show both options for them.

## Caveats / follow-ups for the parent

- **`mtk_2026_coverage.py` needs two corrections** (see conflicts 1–2 above):
  Dimensity 7400 → MT6878 (not MT6879); Dimensity 8200 → MT6896 and
  8000/8100 → MT6895 (currently swapped). Its `BENCHMARK_CHIPS` comments carry
  the same errors.
- **Dimensity 9600M (MT6994)** is the one mapping resting on aggregator
  majority rather than Wikipedia or a device log — re-check when a 9600M
  device log or kernel source appears.
- **Helio G99+** is the only chip with no verified MT number at all.
- The 12 DB notes containing MT numbers were used as supporting evidence; two
  of them (7200 Pro, 8050) turned out to be wrong and are flagged above.
- Normalized key `Dimensity 6360` (from `Dimensity 6360 Max`) → MT6835 is an
  alias derived from the Max (MT6835c) and Apex (MT6835e) variants, both
  MT6835-family; the plain 6360 has no standalone part-number listing.
