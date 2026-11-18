#!/usr/bin/env python3
"""Build ~/workspace/chipcheck/mt-mapping.json from mdm-models.json.

Verified chipset -> MT-number mapping for the MEER Chip Check app.
Method: Wikipedia "List of MediaTek systems on chips" (primary), plus
spot-checks (91mobiles, NanoReview, deviceinfo.app, USPTO patent filing,
Geekbench/tool logs, Once Human requirements) for chips Wikipedia lists
without a part number or with suffix variants. NEVER guesses: anything
unconfirmed goes to "unverified".
"""
import json
import re
from pathlib import Path

DB = Path.home() / "workspace/hamza-tool-pro/tools/mdm-models.json"
OUT = Path.home() / "workspace/chipcheck/mt-mapping.json"

WIKI = ("Wikipedia List of MediaTek systems on chips "
        "(en.wikipedia.org/wiki/List_of_MediaTek_systems_on_chips, "
        "page crawled 2026-11-05)")
DBSELF = "DB chipset string itself (already an MT part number)"
SUFFIX_PATTERN = ("Wikipedia base chip + verified suffix-variant pattern "
                  "(OEM suffixes Ultra/Ultimate/Max/Pro/Plus/Turbo/Energy/"
                  "Super/Extreme share the base silicon; verified cases: "
                  "Dimensity 7200 Pro=MT6886, 7300 Energy=MT6878, "
                  "7300 Pro=MT6878, 7400 Turbo=MT6878, 7500 Turbo=MT6881, "
                  "7350 Pro=MT6886, 8350 Extreme=MT6897, 6360 Max=MT6835, "
                  "7025 Ultra=MT6855, 8100 Max/8000 Max=MT6895, "
                  "8100 Ultra=MT6895, 8200 Ultra=MT6896, 8300 Ultra=MT6897, "
                  "7200 Ultra=MT6886, Helio G92 Max=MT6769I, "
                  "Helio G99 Ultra/Ultimate=G99)")

# ---------------------------------------------------------------- base table
# key: cleaned chip name (no "MediaTek " prefix, no parentheticals)
# value: dict(mt, nm?, cpu?, gpu?, variant?, source, note?)
def E(mt, source, nm=None, cpu=None, gpu=None, variant=None, note=None):
    d = {"mt": mt, "source": source}
    if variant:
        d["variant"] = variant
    if nm:
        d["nm"] = nm
    if cpu:
        d["cpu"] = cpu
    if gpu:
        d["gpu"] = gpu
    if note:
        d["note"] = note
    return d

BASE = {
    # ---- Helio A ----
    "Helio A20": E("MT6761", WIKI, "12", "4x1.8 GHz Cortex-A53",
                   "PowerVR GE8300", "MT6761V/WE"),
    "Helio A22": E("MT6761", WIKI, "12", "4x2.0 GHz Cortex-A53",
                   "PowerVR GE8300", "MT6761V/WAB, MT6761V/WBB"),
    "Helio A25": E("MT6762", WIKI, "12",
                   "4x1.8 GHz Cortex-A53 + 4x1.5 GHz Cortex-A53",
                   "PowerVR GE8320", "MT6762V/WB, MT6762V/WD"),
    # ---- Helio X ----
    "Helio X20": E("MT6797", WIKI, "20",
                   "2x2.1 GHz Cortex-A72 + 4x1.85 GHz Cortex-A53 + "
                   "4x1.4 GHz Cortex-A53", "Mali-T880 MP4"),
    # ---- Helio P ----
    "Helio P10": E("MT6755", WIKI, "28",
                   "4x2.0 GHz Cortex-A53 + 4x1.2 GHz Cortex-A53",
                   "Mali-T860 MP2"),
    "Helio P20": E("MT6757", WIKI, "16",
                   "4x2.3 GHz Cortex-A53 + 4x1.6 GHz Cortex-A53",
                   "Mali-T880 MP2"),
    "Helio P25": E("MT6757", WIKI, "16",
                   "4x2.4/2.6 GHz Cortex-A53 + 4x1.65/1.7 GHz Cortex-A53",
                   "Mali-T880 MP2", "MT6757CD, MT6757T"),
    "Helio P25 Lite": E("MT6757",
                        "Kimovil + Mobosdata + FindPare spec pages "
                        "(Helio P25 Lite = MT6757CD); Wikipedia P25/P25T "
                        "= MT6757CD/MT6757T", "16",
                        "4x2.39 GHz Cortex-A53 + 4x1.6 GHz Cortex-A53",
                        "Mali-T880 MP2", "MT6757CD",
                        "Samsung marketing name for a lower-clocked P25; "
                        "part number MT6757CD confirmed by 3 spec sites."),
    "Helio P22": E("MT6762", WIKI, "12",
                   "4x2.0 GHz Cortex-A53 + 4x1.5 GHz Cortex-A53",
                   "PowerVR GE8320"),
    "Helio P23": E("MT6763", WIKI, "16",
                   "4x2.3/2.5 GHz Cortex-A53 + 4x1.65 GHz Cortex-A53",
                   "Mali-G71 MP2", "MT6763, MT6763T"),
    "Helio P30": E("MT6758", WIKI, "16",
                   "4x2.3 GHz Cortex-A53 + 4x1.65 GHz Cortex-A53",
                   "Mali-G71 MP2"),
    "Helio P35": E("MT6765", WIKI, "12",
                   "4x2.3 GHz Cortex-A53 + 4x1.8 GHz Cortex-A53",
                   "PowerVR GE8320"),
    "Helio P60": E("MT6771", WIKI, "12",
                   "4x2.0 GHz Cortex-A73 + 4x2.0 GHz Cortex-A53",
                   "Mali-G72 MP3"),
    "Helio P65": E("MT6768", WIKI, "12",
                   "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                   "Mali-G52 MC2"),
    "Helio P70": E("MT6771", WIKI, "12",
                   "4x2.1 GHz Cortex-A73 + 4x2.0 GHz Cortex-A53",
                   "Mali-G72 MP3", "MT6771V/CT, MT6771V/WT"),
    "Helio P90": E("MT6779", WIKI, "12",
                   "2x2.2 GHz Cortex-A75 + 6x2.0 GHz Cortex-A55",
                   "PowerVR GM9446", "MT6779V/CU"),
    "Helio P95": E("MT6779", WIKI, "12", variant="MT6779V/CV",
                   note="Wikipedia P95 row has no CPU/GPU listed; same "
                   "MT6779 silicon as P90."),
    # ---- Helio G ----
    "Helio G25": E("MT6762G", WIKI, "12",
                   "4x2.0 GHz Cortex-A53 + 4x1.5 GHz Cortex-A53",
                   "PowerVR GE8320"),
    "Helio G35": E("MT6765G", WIKI, "12",
                   "4x2.3 GHz Cortex-A53 + 4x1.8 GHz Cortex-A53",
                   "PowerVR GE8320", "MT6765G, MT6765V/CB"),
    "Helio G36": E("MT6765V", WIKI, "12",
                   "4x2.2 GHz Cortex-A53 + 4x1.6 GHz Cortex-A53",
                   variant="MT6765V/XAA, MT6765V/XBA",
                   note="Wikipedia G36 row lists no GPU."),
    "Helio G37": E("MT6765H", WIKI, "12",
                   "4x2.3 GHz Cortex-A53 + 4x1.8 GHz Cortex-A53",
                   note="Wikipedia G37 row lists no GPU."),
    "Helio G50": E("MT6765V",
                   WIKI + "; NanoReview (GPU PowerVR GE8320)", "12",
                   "4x2.2 GHz Cortex-A53 + 4x1.7 GHz Cortex-A53",
                   "PowerVR GE8320"),
    "Helio G50 Ultimate": E("MT6765V", SUFFIX_PATTERN, "12",
                            "4x2.2 GHz Cortex-A53 + 4x1.7 GHz Cortex-A53",
                            "PowerVR GE8320"),
    "Helio G70": E("MT6769", WIKI, "12",
                   "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                   "Mali-G52 MC2", "MT6769V/CB",
                   "Verified on Wikipedia (parent flagged 'verify'): G70 "
                   "is MT6769-family, variant MT6769V/CB."),
    "Helio G80": E("MT6769", WIKI, "12",
                   "2x2.0 GHz Cortex-A75 + 6x1.8 GHz Cortex-A55",
                   "Mali-G52 MC2", "MT6769T, MT6769V/CT, MT6769V/CU"),
    "Helio G81": E("MT6769", WIKI, "12",
                   "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                   "Mali-G52 MC2", "MT6769J, MT6769L, MT6769S"),
    "Helio G81 Ultimate": E("MT6769", WIKI, "12",
                            "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                            "Mali-G52 MC2", "MT6769J, MT6769L, MT6769S",
                            "Anchor: X6840 (Infinix Smart 20) -> MT6769."),
    "Helio G81 Ultra": E("MT6769", SUFFIX_PATTERN, "12",
                         "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                         "Mali-G52 MC2", "MT6769J, MT6769L, MT6769S"),
    "Helio G85": E("MT6769", WIKI, "12",
                   "2x2.0 GHz Cortex-A75 + 6x1.8 GHz Cortex-A55",
                   "Mali-G52 MC2", "MT6769Z, MT6769V/CZ"),
    "Helio G88": E("MT6769", WIKI, "12", variant="MT6769H",
                   note="Wikipedia G88 row lists no CPU/GPU."),
    "Helio G91": E("MT6769", WIKI, "12", variant="MT6769G, MT6769K",
                   note="Wikipedia G91 row lists no CPU/GPU."),
    "Helio G91 Ultra": E("MT6769",
                         "Wikipedia Helio G91 (MT6769G/K); Versus.com + "
                         "All Techno comparison (G91 Ultra CPU/GPU)", "12",
                         "2x2.0 GHz Cortex-A75 + 6x1.8 GHz Cortex-A55",
                         "Mali-G52 MC2", "MT6769G, MT6769K"),
    "Helio G92 Max": E("MT6769",
                       "CPU-Boss + NanoReview + Radargit + 91mobiles "
                       "(G92 Max = MT6769I); Wikipedia Helio G92 = MT6769I",
                       "12", "2x2.0 GHz Cortex-A75 + 6x1.8 GHz Cortex-A55",
                       "Mali-G52 MC2", "MT6769I"),
    "Helio G90T": E("MT6785", WIKI, "12",
                    "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                    "Mali-G76 MC4", "MT6785V/CC"),
    "Helio G95": E("MT6785", WIKI, "12",
                   "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                   "Mali-G76 MC4", "MT6785V/CD"),
    "Helio G96": E("MT6781", WIKI, "12",
                   "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                   "Mali-G57 MC2", "MT6781, MT6781V/CD"),
    "Helio G99": E("MT6789", WIKI, "6",
                   "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                   "Mali-G57 MC2",
                   "MT6789, MT6789G, MT6789U, MT6789V/CD, MT8781"),
    "Helio G99 Ultimate": E("MT6789",
                            WIKI + "; NanoReview (G99 Ultimate is the same "
                            "chip as G99)", "6",
                            "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                            "Mali-G57 MC2"),
    "Helio G99 Ultra": E("MT6789",
                         WIKI + "; PhoneRanked (G99 'also listed as Helio "
                         "G99 Ultra') + UMA Technology (G99-Ultra shares "
                         "G99 CPU/GPU)", "6",
                         "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                         "Mali-G57 MC2"),
    "Helio G100": E("MT6789H", WIKI, "6",
                    "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                    "Mali-G57 MC2", "MT6789H, MT6789I, MT6789J"),
    "Helio G100 Ultimate": E("MT6789H", WIKI, "6",
                             "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                             "Mali-G57 MC2", "MT6789H, MT6789I, MT6789J",
                             "Anchor: KM6 (Tecno Spark 40 Pro) -> MT6789H."),
    "Helio G100 Ultra": E("MT6789H", SUFFIX_PATTERN, "6",
                          "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                          "Mali-G57 MC2", "MT6789H, MT6789I, MT6789J"),
    "Helio G200": E("MT6789", WIKI, "6",
                    "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                    "Mali-G57 MC2", "MT6789T",
                    "Anchor: X6885 (Infinix Hot 60 Pro) -> MT6789; "
                    "Wikipedia lists the G200 part as MT6789T."),
    "Helio G200 Ultimate": E("MT6789", WIKI, "6",
                             "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                             "Mali-G57 MC2", "MT6789T",
                             "Anchor: CN5c (Tecno Camon 50 Pro) -> MT6789."),
    # ---- Dimensity 700/800/900 ----
    "Dimensity 700": E("MT6833", WIKI, "7",
                       "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                       "Mali-G57 MC2",
                       "MT6833, MT6833G, MT6833V/ZA, MT6833V/NZA"),
    "Dimensity 720": E("MT6853", WIKI, "7",
                       "2x2.0 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                       "Mali-G57 MC3", "MT6853V/ZA, MT6853V/NZA"),
    "Dimensity 720 5G": E("MT6853", WIKI, "7",
                          "2x2.0 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                          "Mali-G57 MC3", "MT6853V/ZA, MT6853V/NZA"),
    "Dimensity 800": E("MT6873", WIKI, "7",
                       "4x2.0 GHz Cortex-A76 + 4x2.0 GHz Cortex-A55",
                       "Mali-G57 MC4"),
    "Dimensity 800 5G": E("MT6873", WIKI, "7",
                          "4x2.0 GHz Cortex-A76 + 4x2.0 GHz Cortex-A55",
                          "Mali-G57 MC4"),
    "Dimensity 800U": E("MT6853", WIKI, "7",
                        "2x2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                        "Mali-G57 MC3", "MT6853T, MT6853V/TNZA"),
    "Dimensity 810": E("MT6833", WIKI, "6",
                       "2x2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                       "Mali-G57 MC2",
                       "MT6833P, MT6833GP, MT6833V/PNZA"),
    "Dimensity 820": E("MT6875", WIKI, "7",
                       "4x2.6 GHz Cortex-A76 + 4x2.0 GHz Cortex-A55",
                       "Mali-G57 MC5"),
    "Dimensity 900": E("MT6877", WIKI, "6",
                       "2x2.4 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                       "Mali-G68 MC4", "MT6877, MT6877V/ZA"),
    "Dimensity 920": E("MT6877", WIKI, "6",
                       "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                       "Mali-G68 MC4", "MT6877, MT6877T, MT6877V/TZA"),
    "Dimensity 930": E("MT6855", WIKI, "6",
                       "2x2.2 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                       "IMG BXM-8-256",
                       "MT6855, MT6855G, MT6855V/AZA"),
    # ---- Dimensity 1000 ----
    "Dimensity 1000": E("MT6889", WIKI, "7",
                        "4x2.6 GHz Cortex-A77 + 4x2.0 GHz Cortex-A55",
                        "Mali-G77 MC9"),
    "Dimensity 1000+": E("MT6889", WIKI, "7",
                         "4x2.6 GHz Cortex-A77 + 4x2.0 GHz Cortex-A55",
                         "Mali-G77 MC9", "MT6889Z/CZA"),
    "Dimensity 1000L": E("MT6885", WIKI, "7",
                         "4x2.2 GHz Cortex-A77 + 4x2.0 GHz Cortex-A55",
                         "Mali-G77 MC7", "MT6885Z/CZA"),
    "Dimensity 1050": E("MT6879", WIKI, "6",
                        "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        "Mali-G610 MC3",
                        "MT6879, MT6879V/ZA, MT6879V_T/ZA",
                        "MT6879 is the Dimensity 1050 (and 7030), NOT the "
                        "7400 — see Dimensity 7400 conflict in report."),
    "Dimensity 1080": E("MT6877", WIKI, "6",
                        "2x2.6 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        "Mali-G68 MC4",
                        "MT6877, MT6877V/TTZA, MT6877V_T/TTZA"),
    "Dimensity 1100": E("MT6891", WIKI, "6",
                        "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G77 MC9",
                        "MT6891, MT6891Z/CZA, MT6891Z_Z/CZA, MT6891Z_T/CZA"),
    "Dimensity 1200": E("MT6893", WIKI, "6",
                        "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                        "4x2.0 GHz Cortex-A55", "Mali-G77 MC9",
                        "MT6893, MT6893Z/CZA, MT6893Z_A/CZA"),
    "Dimensity 1200 AI": E("MT6893",
                           WIKI + "; GizChina + GizBot (1200-AI / 1200-Max "
                           "are Dimensity 1200 custom variants via "
                           "MediaTek 5G Open Architecture, same CPU/GPU)",
                           "6",
                           "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                           "4x2.0 GHz Cortex-A55", "Mali-G77 MC9"),
    "Dimensity 1200 Max": E("MT6893",
                            "Once Human official requirements (Dimensity "
                            "1200 Max = MT6893/64-bit); " + WIKI, "6",
                            "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                            "4x2.0 GHz Cortex-A55", "Mali-G77 MC9"),
    "Dimensity 1300": E("MT6893", WIKI, "6",
                        "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                        "4x2.0 GHz Cortex-A55", "Mali-G77 MC9",
                        "MT6893Z_Z/CZA, MT6893Z_T/CZA"),
    # ---- Dimensity 6000 ----
    "Dimensity 6020": E("MT6833", WIKI, "7",
                        "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                        "Mali-G57 MC2",
                        note="Wikipedia: Dimensity 700 renamed."),
    "Dimensity 6080": E("MT6833", WIKI, "6",
                        "2x2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                        "Mali-G57 MC2",
                        note="Wikipedia: Dimensity 810 renamed."),
    "Dimensity 6100+": E("MT6835", WIKI, "6",
                         "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                         "Mali-G57 MC2",
                         "MT6835, MT6835V/ZA, MT8755V/TZB"),
    "Dimensity 6100 Plus": E("MT6835", WIKI, "6",
                             "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                             "Mali-G57 MC2",
                             "MT6835, MT6835V/ZA, MT8755V/TZB",
                             note="'Plus' is the spelled-out form of '+'."),
    "Dimensity 6300": E("MT6835", WIKI, "6",
                        "2x2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                        "Mali-G57 MC2", "MT6835, MT6835T, MT6835V/TZB"),
    "Dimensity 6360 Max": E("MT6835",
                            "DeviceInfo.app (Dimensity 6360 Max reports as "
                            "MT6835c; 6nm, 2x2.4 GHz Cortex-A76 + 6x2.0 GHz "
                            "Cortex-A55); Wikipedia lists Dimensity 6360 "
                            "with no part number", "6",
                            "2x2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                            variant="MT6835c",
                            note="Wikipedia 6360 row has no part number; "
                            "the Max variant's reported model code MT6835c "
                            "settles the family."),
    "Dimensity 6400": E("MT6835",
                        WIKI + "; NanoReview (6400 GPU Mali-G57 MP2)", "6",
                        "2x2.5 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                        "Mali-G57 MC2", "MT6835, MT6835V/TTZB"),
    "Dimensity 6400 Max": E("MT6835",
                            WIKI + "; Gizinfo/MyMobileGuru spec match "
                            "(6400 Max: 2x2.5 GHz Cortex-A76 + 6x2.0 GHz "
                            "Cortex-A55, Mali-G57 MC2, 6nm — identical to "
                            "Dimensity 6400)", "6",
                            "2x2.5 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                            "Mali-G57 MC2", "MT6835, MT6835V/TTZB"),
    # ---- Dimensity 7000 ----
    "Dimensity 7020": E("MT6855", WIKI, "6",
                        "2x2.2 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        "IMG BXM-8-256",
                        note="Wikipedia: Dimensity 930 renamed."),
    "Dimensity 7025": E("MT6855", WIKI, "6",
                        "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        variant="MT6855V/ATZA, MT6855V_A/ATZA",
                        note="Wikipedia 7025 row lists no GPU."),
    "Dimensity 7025 Ultra": E("MT6855",
                              "91mobiles (Dimensity 7025 Ultra Model No "
                              "MT6855); " + WIKI, "6",
                              "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                              variant="MT6855V/ATZA, MT6855V_A/ATZA"),
    "Dimensity 7030": E("MT6879", WIKI, "6",
                        "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        "Mali-G610 MC3",
                        note="Wikipedia: Dimensity 1050 renamed (= MT6879)."),
    "Dimensity 7050": E("MT6877", WIKI, "6",
                        "2x2.6 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                        "Mali-G68 MC4",
                        note="Wikipedia: Dimensity 1080 renamed."),
    "Dimensity 7100": E("MT6858", WIKI, "6",
                        "4x2.4 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G610 MC2", "MT6858, MT6858V/ZA"),
    "Dimensity 7200": E("MT6886", WIKI, "4",
                        "2x2.8 GHz Cortex-A715 + 6x2.0 GHz Cortex-A510",
                        "Mali-G610 MC4",
                        "MT6886, MT6886V_A/CZA, MT6886V_B/CZA"),
    "Dimensity 7200 Pro": E("MT6886",
                            "USPTO patent filing table (Daedalus Prime v. "
                            "MediaTek: Dimensity 7200 Pro = MT6886) + "
                            "91mobiles (Model No MT6886) + Android Multi "
                            "Tool log on Nothing Phone (2a): ChipId MT6886",
                            "4",
                            "2x2.8 GHz Cortex-A715 + 6x2.0 GHz Cortex-A510",
                            "Mali-G610 MC4",
                            note="CONFLICT: DB string embeds (MT6878) — "
                            "wrong; 7200 Pro is MT6886 (3 sources)."),
    "Dimensity 7200 Ultra": E("MT6886",
                              "Once Human official requirements (Dimensity "
                              "7200 Ultra = MT6886/64-bit); " + WIKI, "4",
                              "2x2.8 GHz Cortex-A715 + 6x2.0 GHz Cortex-A510",
                              "Mali-G610 MC4"),
    "Dimensity 7300": E("MT6878", WIKI, "4",
                        "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G615 MC2",
                        "MT6878, MT6878V/ZA, MT6878V_A/ZA, MT6878V_B/ZA, "
                        "MT6878V_E/ZA, MT8775"),
    "Dimensity 7300e": E("MT6858", WIKI, "6",
                         "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                         "Mali-G610 MC2", "MT6858T, MT6858V/TZA",
                         note="7300e is NOT MT6878 — it is the MT6858 "
                         "part (same family as Dimensity 7100)."),
    "Dimensity 7300 Energy": E("MT6878",
                               "91mobiles (7300 Energy Model No MT6878) + "
                               "F64 Ultra Suite log on OPPO Reno12 Pro 5G "
                               "(Dimensity 7300-Energy, SoC mt6878); " + WIKI,
                               "4",
                               "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                               "Mali-G615 MC2"),
    "Dimensity 7300 Pro": E("MT6878",
                            "91mobiles (7300 Pro Model No MT6878); " + WIKI,
                            "4",
                            "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                            "Mali-G615 MC2"),
    "Dimensity 7300 Ultimate": E("MT6878", SUFFIX_PATTERN, "4",
                                 "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                                 "Mali-G615 MC2"),
    "Dimensity 7300 Ultra": E("MT6878", SUFFIX_PATTERN, "4",
                              "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                              "Mali-G615 MC2"),
    "Dimensity 7350 Pro": E("MT6886",
                            "91mobiles (7350 Pro Model No MT6886V) + "
                            "DeviceInfo.app (reports as MT6886c); "
                            "Wikipedia Dimensity 7350 = MT6886V/TCZA", "4",
                            "2x3.0 GHz Cortex-A715 + 6x2.0 GHz Cortex-A510",
                            "Mali-G610 MC4", "MT6886V/TCZA"),
    "Dimensity 7360 Max": E("MT6878",
                            "Wikipedia Dimensity 7360 (MT6878V_G/ZA) + "
                            "Smartprix spec match (7360 Max: 4x2.5 GHz "
                            "Cortex-A78 + 4x2.0 GHz Cortex-A55, Mali-G615, "
                            "4nm)", "4",
                            "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                            "Mali-G615 MC2", "MT6878V_G/ZA"),
    "Dimensity 7360 Super": E("MT6878",
                              "Wikipedia Dimensity 7360 (MT6878V_G/ZA) + "
                              "GSMArena-spec listings (7360 Super: 4nm, "
                              "Mali-G615, same 7360 platform)", "4",
                              "4x2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                              "Mali-G615 MC2", "MT6878V_G/ZA"),
    "Dimensity 7400": E("MT6878", WIKI, "4",
                        "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G615 MC2",
                        "MT6878V/TZA, MT6878V_B/TZA, MT6878V_C/TZA",
                        "CONFLICT RESOLVED: mtk_2026_coverage.py said "
                        "MT6879 — wrong; Wikipedia lists 7400 as MT6878 "
                        "variants and MT6879 as Dimensity 1050. DB note "
                        "(X6876) saying MT6878 was correct."),
    "Dimensity 7400 Turbo": E("MT6878",
                              "Geekbench listing (Vivo V80 FE, Dimensity "
                              "7400-Turbo = MT6878) + DeviceInfo.app "
                              "(reports as MT6878k); " + WIKI, "4",
                              "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                              "Mali-G615 MC2", "MT6878k"),
    "Dimensity 7400 Ultimate": E("MT6878", SUFFIX_PATTERN, "4",
                                 "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                                 "Mali-G615 MC2"),
    "Dimensity 7400 Ultra": E("MT6878", SUFFIX_PATTERN, "4",
                              "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                              "Mali-G615 MC2"),
    "Dimensity 7500 Turbo": E("MT6881",
                              "91mobiles (7500 Turbo Model No MT6881); "
                              "Wikipedia Dimensity 7500 = MT6881", "4",
                              "4x2.6 GHz C1-Pro + 4x2.0 GHz C1-Nano",
                              "Mali-G625 MC2"),
    # ---- Dimensity 8000 ----
    "Dimensity 8000": E("MT6895", WIKI, "5",
                        "4x2.75 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G610 MC6", "MT6895, MT6895Z/CZA"),
    "Dimensity 8000 Max": E("MT6895",
                            "Once Human official requirements (Dimensity "
                            "8000 Max = MT6895/64-bit); " + WIKI, "5",
                            "4x2.75 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                            "Mali-G610 MC6"),
    "Dimensity 8020": E("MT6891", WIKI, "6",
                        "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G77 MC9",
                        note="Wikipedia: Dimensity 1100 renamed."),
    "Dimensity 8050": E("MT6893", WIKI, "6",
                        "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                        "4x2.0 GHz Cortex-A55", "Mali-G77 MC9",
                        note="Wikipedia: Dimensity 1300 renamed (= MT6893). "
                        "CONFLICT: DB notes (X6710/CK8n/CK9n/AD11) assume "
                        "'D8050/MT6896 class' — wrong per Wikipedia."),
    "Dimensity 8100": E("MT6895", WIKI, "5",
                        "4x2.85 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                        "Mali-G610 MC6",
                        "MT6895, MT6895Z/TCZA, MT6895Z_A/TCZA, "
                        "MT6895Z_B/TCZA, MT6895ZB, MT8795Z/TNZA"),
    "Dimensity 8100 Max": E("MT6895",
                            "Once Human official requirements (Dimensity "
                            "8100 Max = MT6895/64-bit); " + WIKI, "5",
                            "4x2.85 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                            "Mali-G610 MC6"),
    "Dimensity 8100 Ultra": E("MT6895",
                              "DeviceInfo.app (8100 Ultra reports as "
                              "MT6895a); " + WIKI, "5",
                              "4x2.85 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                              "Mali-G610 MC6", "MT6895a"),
    "Dimensity 8200": E("MT6896", WIKI, "4",
                        "1x3.1 GHz Cortex-A78 + 3x3.0 GHz Cortex-A78 + "
                        "4x2.0 GHz Cortex-A55", "Mali-G610 MC6",
                        "MT6896, MT6896Z/CZA, MT6896Z_B/CZA",
                        "CONFLICT: mtk_2026_coverage.py maps 8200 to "
                        "MT6895 and 8000/8100 to MT6896 — Wikipedia has "
                        "it the other way round (8200 = MT6896, 8000/8100 "
                        "= MT6895). DB note PHV110 already flagged this "
                        "as a naming conflict."),
    "Dimensity 8200 Ultimate": E("MT6896", SUFFIX_PATTERN, "4",
                                 "1x3.1 GHz Cortex-A78 + 3x3.0 GHz Cortex-A78 "
                                 "+ 4x2.0 GHz Cortex-A55", "Mali-G610 MC6"),
    "Dimensity 8200 Ultra": E("MT6896",
                              "Once Human official requirements (Dimensity "
                              "8200 Ultra = MT6896ZB/64-bit); " + WIKI, "4",
                              "1x3.1 GHz Cortex-A78 + 3x3.0 GHz Cortex-A78 + "
                              "4x2.0 GHz Cortex-A55", "Mali-G610 MC6",
                              "MT6896ZB"),
    "Dimensity 8250": E("MT6896", WIKI, "4",
                        "1x3.1 GHz Cortex-A78 + 3x3.0 GHz Cortex-A78 + "
                        "4x2.0 GHz Cortex-A55", "Mali-G610 MC6",
                        "MT6896Z_C/CZA"),
    "Dimensity 8300": E("MT6897", WIKI, "4",
                        "1x3.35 GHz Cortex-A715 + 3x3.2 GHz Cortex-A715 + "
                        "4x2.2 GHz Cortex-A510", "Mali-G615 MC6",
                        "MT6897, MT6897Z/ZA, MT6897Z_A/ZA, MT8792Z/CA, "
                        "MT8792Z/NB"),
    "Dimensity 8300 Ultra": E("MT6897",
                              "Once Human official requirements (Dimensity "
                              "8300 Ultra = MT6897/64-bit); " + WIKI, "4",
                              "1x3.35 GHz Cortex-A715 + 3x3.2 GHz Cortex-A715 "
                              "+ 4x2.2 GHz Cortex-A510", "Mali-G615 MC6"),
    "Dimensity 8350": E("MT6897", WIKI, "4",
                        "1x3.35 GHz Cortex-A715 + 3x3.2 GHz Cortex-A715 + "
                        "4x2.2 GHz Cortex-A510", "Mali-G615 MC6",
                        "MT6897, MT6897Z_B/ZA, MT6897Z_D/ZA, MT6897Z_E/ZA, "
                        "MT6897Z_F/ZA, MT8792Z/NA"),
    "Dimensity 8350 Extreme": E("MT6897",
                                "91mobiles (8350 Extreme Edition Model No "
                                "MT6897); " + WIKI, "4",
                                "1x3.35 GHz Cortex-A715 + 3x3.2 GHz "
                                "Cortex-A715 + 4x2.2 GHz Cortex-A510",
                                "Mali-G615 MC6"),
    "Dimensity 8350 Ultimate": E("MT6897", SUFFIX_PATTERN, "4",
                                 "1x3.35 GHz Cortex-A715 + 3x3.2 GHz "
                                 "Cortex-A715 + 4x2.2 GHz Cortex-A510",
                                 "Mali-G615 MC6"),
    "Dimensity 8350 Ultra": E("MT6897", SUFFIX_PATTERN, "4",
                              "1x3.35 GHz Cortex-A715 + 3x3.2 GHz Cortex-A715 "
                              "+ 4x2.2 GHz Cortex-A510", "Mali-G615 MC6"),
    "Dimensity 8400": E("MT6899", WIKI, "4",
                        "1x3.25 GHz Cortex-A725 + 3x3.0 GHz Cortex-A725 + "
                        "4x2.1 GHz Cortex-A725", "Mali-G720 MC7",
                        "MT6899, MT6899Z/ZA, MT6899Z_A/ZA, MT6899Z_B/ZA, "
                        "MT6899Z_C/ZA, MT6899Z_E/ZA"),
    "Dimensity 8400 Max": E("MT6899",
                            WIKI + "; Gizinfo/MyMobileGuru spec match "
                            "(8400 Max: 1x3.25 + 3x3.0 + 4x2.1 GHz "
                            "Cortex-A725, Mali-G720 MC7, 4nm — identical "
                            "to Dimensity 8400)", "4",
                            "1x3.25 GHz Cortex-A725 + 3x3.0 GHz Cortex-A725 "
                            "+ 4x2.1 GHz Cortex-A725", "Mali-G720 MC7"),
    "Dimensity 8400 Ultra": E("MT6899",
                              WIKI + "; NanoReview ('Dimensity 8400 Ultra "
                              "is the same chip as Dimensity 8400')", "4",
                              "1x3.25 GHz Cortex-A725 + 3x3.0 GHz Cortex-A725 "
                              "+ 4x2.1 GHz Cortex-A725", "Mali-G720 MC7"),
    "Dimensity 8450": E("MT6899", WIKI, "4",
                        "1x3.25 GHz Cortex-A725 + 3x3.0 GHz Cortex-A725 + "
                        "4x2.1 GHz Cortex-A725", "Mali-G720 MC7",
                        "MT6899Z_D/ZA"),
    "Dimensity 8500": E("MT6899", WIKI, "4",
                        "1x3.4 GHz Cortex-A725 + 3x3.2 GHz Cortex-A725 + "
                        "4x2.2 GHz Cortex-A725", "Mali-G720 MC8",
                        "MT6899, MT6899Z_A/TZA"),
    "Dimensity 8500 Super": E("MT6899",
                              WIKI + "; GSMArena-spec listings (8500 Super: "
                              "1x3.4 + 3x3.2 + 4x2.2 GHz Cortex-A725, 4nm "
                              "— identical to Dimensity 8500)", "4",
                              "1x3.4 GHz Cortex-A725 + 3x3.2 GHz Cortex-A725 "
                              "+ 4x2.2 GHz Cortex-A725", "Mali-G720 MC8"),
    "Dimensity 8550": E("MT6899", WIKI, "4",
                        "1x3.4 GHz Cortex-A725 + 3x3.2 GHz Cortex-A725 + "
                        "4x2.2 GHz Cortex-A725", "Mali-G720 MC8",
                        "MT6899, MT6899Z_T/TZA"),
    "Dimensity 8550 Super": E("MT6899",
                              WIKI + "; GSMArena-spec listings (8550 Super: "
                              "1x3.4 + 3x3.2 + 4x2.2 GHz Cortex-A725, 4nm "
                              "— identical to Dimensity 8500/8550)", "4",
                              "1x3.4 GHz Cortex-A725 + 3x3.2 GHz Cortex-A725 "
                              "+ 4x2.2 GHz Cortex-A725", "Mali-G720 MC8"),
    # ---- Dimensity 9000 ----
    "Dimensity 9000": E("MT6983", WIKI, "4",
                        "1x3.05 GHz Cortex-X2 + 3x2.85 GHz Cortex-A710 + "
                        "4x1.8 GHz Cortex-A510", "Mali-G710 MC10",
                        "MT6983, MT6983Z/CZA, MT8798, MT8798Z/CNZA"),
    "Dimensity 9000+": E("MT6983", WIKI, "4",
                         "1x3.2 GHz Cortex-X2 + 3x2.85 GHz Cortex-A710 + "
                         "4x1.8 GHz Cortex-A510", "Mali-G710 MC10",
                         "MT6983, MT6983W/CZA, MT8798, MT8798Z/TNZA"),
    "Dimensity 9200": E("MT6985", WIKI, "4",
                        "1x3.05 GHz Cortex-X3 + 3x2.85 GHz Cortex-A715 + "
                        "4x1.8 GHz Cortex-A510", "Immortalis-G715 MC11",
                        "MT6985, MT6985W/CZA"),
    "Dimensity 9200+": E("MT6985", WIKI, "4",
                         "1x3.35 GHz Cortex-X3 + 3x3.0 GHz Cortex-A715 + "
                         "4x2.0 GHz Cortex-A510", "Immortalis-G715 MC11",
                         "MT6985, MT6985W/TCZA"),
    "Dimensity 9300": E("MT6989", WIKI, "4",
                        "1x3.25 GHz Cortex-X4 + 3x2.85 GHz Cortex-X4 + "
                        "4x2.0 GHz Cortex-A720", "Immortalis-G720 MC12",
                        "MT6989, MT6989W/CZA, MT8796W/CNZA"),
    "Dimensity 9300+": E("MT6989", WIKI, "4",
                         "1x3.4 GHz Cortex-X4 + 3x2.85 GHz Cortex-X4 + "
                         "4x2.0 GHz Cortex-A720", "Immortalis-G720 MC12",
                         "MT6989, MT6989W/TCZA, MT8796W/TNZA"),
    "Dimensity 9400e": E("MT6989", WIKI, "4", variant="MT6989T_e",
                         gpu="Immortalis-G720 MC12",
                         note="Wikipedia 9400e row lists no CPU; it is a "
                         "9300-family part (MT6989T_e)."),
    "Dimensity 9400": E("MT6991", WIKI, "3",
                        "1x3.62 GHz Cortex-X925 + 3x3.3 GHz Cortex-X4 + "
                        "4x2.4 GHz Cortex-A720", "Immortalis-G925 MC12",
                        "MT6991, MT6991Z/CZA, MT6991Z/CZB, MT6991W/CZA"),
    "Dimensity 9400+": E("MT6991", WIKI, "3",
                         "1x3.73 GHz Cortex-X925 + 3x3.3 GHz Cortex-X4 + "
                         "4x2.4 GHz Cortex-A720", "Immortalis-G925 MC12",
                         "MT6991, MT6991Z/TCZA, MT6991Z/TCZB, MT8799Z/TNZB"),
    "Dimensity 9400 Plus": E("MT6991", WIKI, "3",
                             "1x3.73 GHz Cortex-X925 + 3x3.3 GHz Cortex-X4 + "
                             "4x2.4 GHz Cortex-A720", "Immortalis-G925 MC12",
                             "MT6991, MT6991Z/TCZA, MT6991Z/TCZB, "
                             "MT8799Z/TNZB",
                             note="'Plus' is the spelled-out form of '+'."),
    "Dimensity 9500s": E("MT6991", WIKI, "3",
                         gpu="Immortalis-G925 MC11/MC12",
                         variant="MT6991Z/SCZB, MT6991Z/ECZB, MT8799Z/ECZB",
                         note="Wikipedia 9500s row lists no CPU."),
    "Dimensity 9500": E("MT6993",
                        WIKI + "; NanoReview (9500 CPU: 1x4.21 GHz "
                        "C1-Ultra + 3x3.5 GHz C1-Premium + 4x2.7 GHz "
                        "C1-Pro)", "3",
                        "1x4.21 GHz C1-Ultra + 3x3.5 GHz C1-Premium + "
                        "4x2.7 GHz C1-Pro", "Mali G1-Ultra MC12",
                        "MT6993, MT6993W/CZA"),
    "Dimensity 9600M": E("MT6994",
                         "NanoReview + 91mobiles (9600M Model No MT6994); "
                         "Wikipedia lists Dimensity 9600M with no part "
                         "number", "3",
                         "1x4.21 GHz C1-Ultra + 3x3.5 GHz C1-Premium + "
                         "4x2.7 GHz C1-Pro", "Mali-G1 Ultra MC12",
                         note="CONFLICT: some sources (OTON Technology, "
                         "SiliconCat) claim 9600M is a rebadged Dimensity "
                         "9500 die (MT6993). Mapped to MT6994 on the "
                         "majority of spec aggregators (NanoReview x3, "
                         "91mobiles x4) plus the MT6993/6994/6995 "
                         "sequence; flagged for re-check."),
    "Dimensity 9600 Pro": E("MT6995", WIKI, "2",
                            "2x4.55 GHz C2-Ultra + 3x4.35 GHz C2-Pro + "
                            "3x3.1 GHz C2-Pro", "Mali G2-Ultra NX MC12",
                            "MT6995, MT6995Z/CZB"),
    # ---- bare MT parts (old ARMv7/ARMv8 + self-maps) ----
    "MT6580": E("MT6580", WIKI, "28", "4x1.3 GHz Cortex-A7",
                "Mali-400 MP1"),
    "MT6580A": E("MT6580A", DBSELF, note="CONFLICT in DB string: "
                "MobileWithDrivers claims MT6580P for this model — "
                "primary token MT6580A kept."),
    "MT6580M": E("MT6580M", DBSELF),
    "MT6580P": E("MT6580P", DBSELF),
    "MT6580W": E("MT6580W", DBSELF),
    "MT6582": E("MT6582", WIKI, "28", gpu="Mali-400 MP2",
                note="Wikipedia MT6582 row lists no CPU clock."),
    "MT6582M": E("MT6582M", WIKI, "28", gpu="Mali-400 MP2"),
    "MT6589": E("MT6589", WIKI, "28", "4x1.3 GHz Cortex-A7",
                "PowerVR SGX544MP"),
    "MT6592": E("MT6592", WIKI, "28", "8x1.7-2.0 GHz Cortex-A7",
                "Mali-450 MP4"),
    "MT6735": E("MT6735", WIKI, "28", "4x1.3 GHz Cortex-A53",
                "Mali-T720 MP2"),
    "MT6735P": E("MT6735P", WIKI, "28", "4x1.0 GHz Cortex-A53",
                 "Mali-T720 MP2"),
    "MT6737": E("MT6737", WIKI, "28", "4x1.1-1.3 GHz Cortex-A53",
                "Mali-T720 MP2"),
    "MT6737M": E("MT6737M", DBSELF),
    "MT6737T": E("MT6737T", WIKI, "28", "4x1.5 GHz Cortex-A53",
                 "Mali-T720 MP2"),
    "MT6739": E("MT6739", WIKI, "28", gpu="PowerVR GE8100",
                note="Wikipedia MT6739 row lists no CPU clock."),
    "MT6739WA": E("MT6739WA", DBSELF),
    "MT6739WW": E("MT6739WW", DBSELF),
    "MT6750": E("MT6750", WIKI, "28",
                "4x1.5 GHz Cortex-A53 + 4x1.0 GHz Cortex-A53",
                "Mali-T860 MP2"),
    "MT6750T": E("MT6750T", WIKI, "28",
                 "4x1.5 GHz Cortex-A53 + 4x1.0 GHz Cortex-A53",
                 "Mali-T860 MP2"),
    "MT6752": E("MT6752", WIKI, "28", "8x1.7 GHz Cortex-A53",
                "Mali-T760 MP2"),
    "MT6753": E("MT6753", WIKI, "28",
                "4x1.5 GHz Cortex-A53 + 4x1.3 GHz Cortex-A53",
                "Mali-T720 MP3"),
    "MT6753T": E("MT6753T", DBSELF),
    "MT6755": E("MT6755", WIKI, "28",
                "4x2.0 GHz Cortex-A53 + 4x1.2 GHz Cortex-A53",
                "Mali-T860 MP2", note="Helio P10 part."),
    "MT6757": E("MT6757", WIKI, "16",
                "4x2.3 GHz Cortex-A53 + 4x1.6 GHz Cortex-A53",
                "Mali-T880 MP2", note="Helio P20 part."),
    "MT6761": E("MT6761", WIKI, "12", "4x2.0 GHz Cortex-A53",
                "PowerVR GE8300", note="Helio A22 part."),
    "MT6762": E("MT6762", WIKI, "12",
                "4x2.0 GHz Cortex-A53 + 4x1.5 GHz Cortex-A53",
                "PowerVR GE8320", note="Helio P22 part."),
    "MT6763": E("MT6763", WIKI, "16",
                "4x2.3/2.5 GHz Cortex-A53 + 4x1.65 GHz Cortex-A53",
                "Mali-G71 MP2", note="Helio P23 part."),
    "MT6765": E("MT6765", WIKI, "12",
                "4x2.3 GHz Cortex-A53 + 4x1.8 GHz Cortex-A53",
                "PowerVR GE8320", note="Helio P35 part."),
    "MT6768": E("MT6768", WIKI, "12",
                "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                "Mali-G52 MC2", note="Helio P65 part."),
    "MT6769": E("MT6769", WIKI, "12",
                "2x2.0 GHz Cortex-A75 + 6x1.7/1.8 GHz Cortex-A55",
                "Mali-G52 MC2",
                note="Helio G70/G80/G81/G85/G88/G91/G92 family part."),
    "MT6771": E("MT6771", WIKI, "12",
                "4x2.0/2.1 GHz Cortex-A73 + 4x2.0 GHz Cortex-A53",
                "Mali-G72 MP3", note="Helio P60/P70 part."),
    "MT6779": E("MT6779", WIKI, "12",
                "2x2.2 GHz Cortex-A75 + 6x2.0 GHz Cortex-A55",
                "PowerVR GM9446", note="Helio P90/P95 part."),
    "MT6781": E("MT6781", WIKI, "12",
                "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                "Mali-G57 MC2", note="Helio G96 part."),
    "MT6785": E("MT6785", WIKI, "12",
                "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                "Mali-G76 MC4", note="Helio G90/G90T/G95 part."),
    "MT6789": E("MT6789", WIKI, "6",
                "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                "Mali-G57 MC2", note="Helio G99/G200 part."),
    "MT6789H": E("MT6789H", WIKI, "6",
                 "2x2.2 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                 "Mali-G57 MC2", note="Helio G100 part."),
    "MT6833": E("MT6833", WIKI, "7",
                "2x2.2/2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                "Mali-G57 MC2",
                note="Dimensity 700/810/6020/6080 family part."),
    "MT6835": E("MT6835", WIKI, "6", gpu="Mali-G57 MC2",
                note="Dimensity 6100+/6300/6360/6400 family part; CPU "
                "clock varies by chip (2.2/2.4/2.5 GHz), so no single "
                "CPU string is given."),
    "MT6853": E("MT6853", WIKI, "7",
                "2x2.0/2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                "Mali-G57 MC3", note="Dimensity 720/800U part."),
    "MT6855": E("MT6855", WIKI, "6",
                "2x2.2/2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                "IMG BXM-8-256", note="Dimensity 930/7020/7025 part."),
    "MT6858": E("MT6858", WIKI, "6",
                "4x2.4/2.5 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                "Mali-G610 MC2", note="Dimensity 7100/7300e part."),
    "MT6873": E("MT6873", WIKI, "7",
                "4x2.0 GHz Cortex-A76 + 4x2.0 GHz Cortex-A55",
                "Mali-G57 MC4", note="Dimensity 800 part."),
    "MT6875": E("MT6875", WIKI, "7",
                "4x2.6 GHz Cortex-A76 + 4x2.0 GHz Cortex-A55",
                "Mali-G57 MC5", note="Dimensity 820 part."),
    "MT6877": E("MT6877", WIKI, "6",
                "2x2.4/2.5/2.6 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                "Mali-G68 MC4",
                note="Dimensity 900/920/1080/7050 family part."),
    "MT6878": E("MT6878", WIKI, "4", gpu="Mali-G615 MC2",
                note="Dimensity 7300/7360/7400 family part; CPU clock "
                "varies by chip (2.5/2.6 GHz), so no single CPU string "
                "is given."),
    "MT6879": E("MT6879", WIKI, "6",
                "2x2.5 GHz Cortex-A78 + 6x2.0 GHz Cortex-A55",
                "Mali-G610 MC3",
                note="Dimensity 1050/7030 part — NOT Dimensity 7400."),
    "MT6881": E("MT6881", WIKI, "4",
                "4x2.6 GHz C1-Pro + 4x2.0 GHz C1-Nano",
                "Mali-G625 MC2", note="Dimensity 7500 part."),
    "MT6885": E("MT6885", WIKI, "7",
                "4x2.2 GHz Cortex-A77 + 4x2.0 GHz Cortex-A55",
                "Mali-G77 MC7", note="Dimensity 1000L part."),
    "MT6886": E("MT6886", WIKI, "4",
                "2x2.8/3.0 GHz Cortex-A715 + 6x2.0 GHz Cortex-A510",
                "Mali-G610 MC4",
                note="Dimensity 7200/7350 family part."),
    "MT6889": E("MT6889", WIKI, "7",
                "4x2.6 GHz Cortex-A77 + 4x2.0 GHz Cortex-A55",
                "Mali-G77 MC9", note="Dimensity 1000/1000+ part."),
    "MT6891": E("MT6891", WIKI, "6",
                "4x2.6 GHz Cortex-A78 + 4x2.0 GHz Cortex-A55",
                "Mali-G77 MC9", note="Dimensity 1100/8020 part."),
    "MT6893": E("MT6893", WIKI, "6",
                "1x3.0 GHz Cortex-A78 + 3x2.6 GHz Cortex-A78 + "
                "4x2.0 GHz Cortex-A55", "Mali-G77 MC9",
                note="Dimensity 1200/1300/8050 part."),
    "MT6895": E("MT6895", WIKI, "5", gpu="Mali-G610 MC6",
                note="Dimensity 8000/8100 family part; CPU clock varies "
                "by chip (2.75/2.85 GHz), so no single CPU string is "
                "given."),
    "MT6896": E("MT6896", WIKI, "4",
                "1x3.1 GHz Cortex-A78 + 3x3.0 GHz Cortex-A78 + "
                "4x2.0 GHz Cortex-A55", "Mali-G610 MC6",
                note="Dimensity 8200/8250 part."),
    "MT6897": E("MT6897", WIKI, "4",
                "1x3.35 GHz Cortex-A715 + 3x3.2 GHz Cortex-A715 + "
                "4x2.2 GHz Cortex-A510", "Mali-G615 MC6",
                note="Dimensity 8300/8350 part."),
    "MT6899": E("MT6899", WIKI, "4",
                "1x3.25/3.4 GHz Cortex-A725 + 3x3.0/3.2 GHz Cortex-A725 "
                "+ 4x2.1/2.2 GHz Cortex-A725", "Mali-G720 MC7/MC8",
                note="Dimensity 8400/8450/8500/8550 family part."),
    "MT6983": E("MT6983", WIKI, "4",
                "1x3.05/3.2 GHz Cortex-X2 + 3x2.85 GHz Cortex-A710 + "
                "4x1.8 GHz Cortex-A510", "Mali-G710 MC10",
                note="Dimensity 9000/9000+ part."),
    "MT6985": E("MT6985", WIKI, "4",
                "1x3.05/3.35 GHz Cortex-X3 + 3x2.85/3.0 GHz Cortex-A715 "
                "+ 4x1.8/2.0 GHz Cortex-A510", "Immortalis-G715 MC11",
                note="Dimensity 9200/9200+ part."),
    "MT6989": E("MT6989", WIKI, "4",
                "1x3.25/3.4 GHz Cortex-X4 + 3x2.85 GHz Cortex-X4 + "
                "4x2.0 GHz Cortex-A720", "Immortalis-G720 MC12",
                note="Dimensity 9300/9300+/9400e part."),
    "MT6991": E("MT6991", WIKI, "3",
                "1x3.62/3.73 GHz Cortex-X925 + 3x3.3 GHz Cortex-X4 + "
                "4x2.4 GHz Cortex-A720", "Immortalis-G925 MC12",
                note="Dimensity 9400/9400+/9500s part."),
    "MT6993": E("MT6993", WIKI, "3",
                "1x4.21 GHz C1-Ultra + 3x3.5 GHz C1-Premium + "
                "4x2.7 GHz C1-Pro", "Mali G1-Ultra MC12",
                note="Dimensity 9500 part."),
    "MT6994": E("MT6994",
                "NanoReview + 91mobiles (9600M Model No MT6994)", "3",
                "1x4.21 GHz C1-Ultra + 3x3.5 GHz C1-Premium + "
                "4x2.7 GHz C1-Pro", "Mali-G1 Ultra MC12",
                note="Dimensity 9600M part (see 9600M conflict note)."),
    "MT6995": E("MT6995", WIKI, "2",
                "2x4.55 GHz C2-Ultra + 3x4.35 GHz C2-Pro + "
                "3x3.1 GHz C2-Pro", "Mali G2-Ultra NX MC12",
                note="Dimensity 9600 Pro part."),
}

# ------------------------------------------------- per-string special cases
# value: ("map", BASE-key) | ("map_entry", entry-dict) | ("unverified", reason)
SPECIAL = {
    # variant splits that agree on one MT number -> mapped
    "Dimensity 720 / Dimensity 800U (variants)": (
        "map_entry", E("MT6853", WIKI, "7",
                       "2x2.0/2.4 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                       "Mali-G57 MC3",
                       note="Variant split, but both chips are MT6853.")),
    "Helio P60 (Global) / Helio P70 (India)": (
        "map_entry", E("MT6771", WIKI, "12",
                       "4x2.0/2.1 GHz Cortex-A73 + 4x2.0 GHz Cortex-A53",
                       "Mali-G72 MP3",
                       note="Variant split, but both chips are MT6771.")),
    "MediaTek Helio G95 (PH variant reported G90T)": (
        "map_entry", E("MT6785", WIKI, "12",
                       "2x2.05 GHz Cortex-A76 + 6x2.0 GHz Cortex-A55",
                       "Mali-G76 MC4", "MT6785V/CD",
                       note="PH variant reported as G90T, but G90T is "
                       "also MT6785 — same MT either way.")),
    # embedded-MT conflicts / odd strings -> mapped with note
    "Helio P20 (MT6757CD)": (
        "map_entry", E("MT6757", WIKI, "16",
                       "4x2.3 GHz Cortex-A53 + 4x1.6 GHz Cortex-A53",
                       "Mali-T880 MP2", "MT6757CD",
                       note="CONFLICT: string says P20 but embeds "
                       "MT6757CD, which is the P25 part (P20 = MT6757). "
                       "Base MT6757 either way.")),
    "Helio G37 (MT6765)": (
        "map_entry", E("MT6765", WIKI, "12",
                       "4x2.3 GHz Cortex-A53 + 4x1.8 GHz Cortex-A53",
                       "PowerVR GE8320",
                       note="String embeds the base MT6765 token; "
                       "Wikipedia lists G37's part as MT6765H.")),
    "MT6768 Helio G70": (
        "map_entry", E("MT6768", WIKI, "12",
                       "2x2.0 GHz Cortex-A75 + 6x1.7 GHz Cortex-A55",
                       "Mali-G52 MC2",
                       note="CONFLICT: explicit MT token is MT6768 "
                       "(Helio P65), but the label says Helio G70 "
                       "(MT6769 per Wikipedia). Mapped to the explicit "
                       "MT token; the G70 label disagrees.")),
    "MT6580A (MT6580P per MobileWithDrivers — Conflict 3)": (
        "map_entry", E("MT6580A", DBSELF,
                       note="CONFLICT in DB string: MobileWithDrivers "
                       "claims MT6580P for this model — primary token "
                       "MT6580A kept.")),
    "MT6737 (MT6737W per Spec411)": (
        "map_entry", E("MT6737", WIKI, "28",
                       "4x1.1-1.3 GHz Cortex-A53", "Mali-T720 MP2",
                       note="CONFLICT in DB string: Spec411 claims "
                       "MT6737W — primary token MT6737 kept.")),
    # ambiguous / variant-split strings -> unverified
    "Helio A22 (MT6761, 2 GB) / Helio A25 (MT6762D, 3–4 GB)":
        ("unverified", "Variant split: MT6761 (A22) vs MT6762 (A25) — "
         "no single MT number."),
    "Helio A22 (MT6761, 2 GB) / Helio P22 (MT6762, 4 GB)":
        ("unverified", "Variant split: MT6761 (A22) vs MT6762 (P22) — "
         "no single MT number."),
    "Helio G25 (MT6762G) / Helio A22 (MT6761)":
        ("unverified", "Variant split: MT6762G (G25) vs MT6761 (A22) — "
         "no single MT number."),
    "Helio G37 (MT6765V/CB, X6816) / Unisoc T610 (X6816C)":
        ("unverified", "Variant split: MediaTek MT6765 vs Unisoc T610 — "
         "mixed vendors, no single MT number."),
    "Helio P35 / Kirin 710A (variants)":
        ("unverified", "Variant split: MediaTek Helio P35 (MT6765) vs "
         "HiSilicon Kirin 710A — mixed vendors."),
    "MediaTek Dimensity 1300 (China) / 6020 (India variant) — variant split":
        ("unverified", "Variant split: Dimensity 1300 (MT6893) vs "
         "Dimensity 6020 (MT6833) — no single MT number."),
    "MediaTek MT6737M / MT6580M":
        ("unverified", "Variant split: MT6737M vs MT6580M — no single "
         "MT number."),
    "MediaTek MT6580 (1 GB ver.) / Helio A22 (2 GB ver.) — see conflict":
        ("unverified", "Variant split: MT6580 vs Helio A22 (MT6761) — "
         "no single MT number."),
    "Unisoc SC9863A (version 1) / MediaTek Helio A22 (version 2) — dual-chipset model, per GSMArena":
        ("unverified", "Dual-chipset model: Unisoc SC9863A vs MediaTek "
         "Helio A22 (MT6761) — mixed vendors."),
    "Unisoc T606 (variant-reported; Helio G25 also reported)":
        ("unverified", "Variant-reported: Unisoc T606 vs Helio G25 "
         "(MT6762G) — mixed vendors."),
    "Snapdragon 8 Gen 1 (China: Dimensity 9000, per W-O text)":
        ("unverified", "Region variant: Snapdragon 8 Gen 1 vs Dimensity "
         "9000 (MT6983) — mixed vendors."),
    "Snapdragon 8 Gen 1 or Dimensity 9000 by region/variant":
        ("unverified", "Region variant: Snapdragon 8 Gen 1 vs Dimensity "
         "9000 (MT6983) — mixed vendors."),
    "MediaTek Helio P22 (Helio A22 in African version)":
        ("unverified", "Region variant: Helio P22 (MT6762) vs Helio A22 "
         "(MT6761) in the African version — no single MT number."),
    "Unknown": ("unverified", "No chipset information in the DB."),
    "unknown": ("unverified", "No chipset information in the DB."),
    "Helio G99+": ("unverified", "Wikipedia lists Helio G99+ (Q3 2026, "
        "LPDDR5X) with NO part number, and no web source gives one "
        "(MediaTek product page lists it with no MT number). Likely "
        "MT6789-family but NOT confirmed — not guessed."),
}

MT_SUFFIXES = [" Ultimate", " Ultra", " Max", " Pro", " Plus", " Turbo",
               " Energy", " Super", " Extreme", " AI"]


def clean_chip_name(s):
    """Strip vendor prefix, parentheticals, footnote marks, em-dash notes."""
    t = s.strip()
    for p in ("MediaTek ", "Qualcomm ", "Samsung "):
        if t.startswith(p):
            t = t[len(p):]
            break
    # trailing parenthetical(s) FIRST (an em-dash note may sit inside them)
    while True:
        m = re.search(r"\s*\([^()]*\)\s*$", t)
        if not m:
            break
        t = t[:m.start()].rstrip()
    # em-dash / hyphen notes at the end
    for sep in (" — ", " – "):
        if sep in t:
            t = t.split(sep, 1)[0].rstrip()
    t = t.rstrip("*").rstrip()
    return t


def classify(s):
    """Return ("mapped", entry) | ("non_mtk", entry) | ("unverified", reason)."""
    if s in SPECIAL:
        kind, val = SPECIAL[s]
        if kind == "map_entry":
            return "mapped", val
        return "unverified", val

    cleaned = clean_chip_name(s)

    # MTK? (Helio / Dimensity / MT token / Kompanio)
    is_mtk = (
        cleaned.startswith(("Helio ", "Dimensity ", "MT"))
        or re.search(r"\bMT\d{4}", s)
        or s.startswith("MediaTek ")
    )
    if is_mtk and " / " not in s and " or " not in s.lower():
        if cleaned in BASE:
            return "mapped", BASE[cleaned]
        # try stripping one marketing suffix, then look up again
        for suf in MT_SUFFIXES:
            if cleaned.endswith(suf):
                base_name = cleaned[:-len(suf)]
                if base_name in BASE:
                    return "mapped", BASE[base_name]
        # bare MT token embedded in the string (self-map)
        m = re.search(r"\b(MT\d{4}[A-Z]*)", s)
        if m:
            tok = m.group(1)
            if tok in BASE:
                return "mapped", BASE[tok]
            return "mapped", E(tok, DBSELF)
        return "unverified", ("MediaTek chip not found on Wikipedia and "
                              "no confirming source: " + s)

    if is_mtk:
        return "unverified", ("Variant/region split involving MediaTek — "
                              "no single MT number: " + s)

    # ---- non-MediaTek ----
    vendors = []
    if "Exynos" in s:
        vendors.append("Samsung")
    if "Snapdragon" in s or s.startswith("Qualcomm"):
        vendors.append("Qualcomm")
    if "Kirin" in s or "HiSilicon" in s:
        vendors.append("HiSilicon")
    if "Tensor" in s:
        vendors.append("Google")
    if "Unisoc" in s or "Tiger" in s or s.strip() == "SC9863A":
        vendors.append("Unisoc")
    if "Spreadtrum" in s:
        vendors.append("Spreadtrum")
    if "Tegra" in s:
        vendors.append("NVIDIA")
    if "Surge" in s:
        vendors.append("Xiaomi")
    if "OMAP" in s:
        vendors.append("Texas Instruments")
    if "Marvell" in s:
        vendors.append("Marvell")
    if not vendors:
        return "unverified", "No identifiable chipset vendor: " + s
    # order vendors by first appearance in the string
    order = {"Samsung": s.find("Exynos"), "Qualcomm": s.find("Snapdragon"),
             "HiSilicon": min(x for x in (s.find("Kirin"), s.find("HiSilicon"))
                              if x >= 0) if ("Kirin" in s or "HiSilicon" in s)
             else -1,
             "Google": s.find("Tensor"),
             "Unisoc": min(x for x in (s.find("Unisoc"), s.find("Tiger"))
                           if x >= 0) if ("Unisoc" in s or "Tiger" in s)
             else (0 if s.strip() == "SC9863A" else -1),
             "Spreadtrum": s.find("Spreadtrum"),
             "NVIDIA": s.find("Tegra"), "Xiaomi": s.find("Surge"),
             "Texas Instruments": s.find("OMAP"),
             "Marvell": s.find("Marvell")}
    vendors.sort(key=lambda v: order.get(v, 999))
    chip = s
    for p in ("Qualcomm ", "Samsung ", "MediaTek "):
        if chip.startswith(p):
            chip = chip[len(p):]
            break
    return "non_mtk", {"vendor": " / ".join(vendors), "chip": chip}


def normalized_keys(s, entry, is_mtk):
    """Extra lookup keys for one DB string (exact key handled by caller)."""
    keys = {}
    cleaned = clean_chip_name(s)
    if cleaned and cleaned != s:
        keys[cleaned] = entry
    # strip marketing suffixes from the cleaned name
    base = cleaned
    if is_mtk:
        for suf in MT_SUFFIXES:
            if base.endswith(suf):
                base = base[:-len(suf)]
                break
        if base.endswith(" 5G"):
            base = base[:-3]
        if base.endswith(" Plus"):
            base = base[:-5] + "+"
    else:
        for suf in (" for Galaxy", " 4G", " 5G", " AE",
                    " Accelerated Edition"):
            if base.endswith(suf):
                base = base[:-len(suf)]
                break
    if base and base != cleaned and base != s:
        keys[base] = entry
    # "Dimensity 6100 Plus" -> "Dimensity 6100+"
    if cleaned.endswith(" Plus"):
        keys[cleaned[:-5] + "+"] = entry
    return keys


def main():
    data = json.loads(DB.read_text(encoding="utf-8"))
    chipsets = sorted({m.get("chipset", "") for m in data["models"]})
    print(f"distinct chipset strings: {len(chipsets)}")

    mapped, non_mtk, unverified = {}, {}, []
    unverified_reasons = {}
    for s in chipsets:
        kind, val = classify(s)
        if kind == "mapped":
            mapped[s] = val
        elif kind == "non_mtk":
            non_mtk[s] = val
        else:
            unverified.append(s)
            unverified_reasons[s] = val

    # normalized lookup keys (never overwrite an exact DB string's entry)
    norm_added, norm_skipped = 0, []
    for s, entry in list(mapped.items()):
        for k, v in normalized_keys(s, entry, True).items():
            if k in mapped or k in non_mtk:
                if k in mapped and mapped[k].get("mt") != v.get("mt"):
                    norm_skipped.append((k, "mapped", mapped[k]["mt"],
                                         v["mt"]))
                continue
            mapped[k] = v
            norm_added += 1
    for s, entry in list(non_mtk.items()):
        for k, v in normalized_keys(s, entry, False).items():
            if k in mapped or k in non_mtk:
                continue
            non_mtk[k] = v
            norm_added += 1

    # ---- verification ----
    exact_mapped = [s for s in chipsets if s in mapped]
    exact_non = [s for s in chipsets if s in non_mtk]
    assert len(exact_mapped) + len(exact_non) + len(unverified) == len(chipsets)
    assert not (set(exact_mapped) & set(exact_non))
    assert not (set(unverified) & set(exact_mapped) & set(exact_non))
    for s, e in mapped.items():
        assert e.get("mt") and e.get("source"), s
    # anchors
    anchors = {
        "Helio G100 Ultimate": "MT6789H",
        "Helio G81 Ultimate": "MT6769",
        "Helio G200 Ultimate": "MT6789",
        "Helio G200": "MT6789",
    }
    for k, mt in anchors.items():
        assert mapped[k]["mt"] == mt, (k, mapped[k]["mt"])
    print("anchors OK:", anchors)

    out = {"mapped": mapped, "non_mtk": non_mtk, "unverified": unverified}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"mapped (exact DB strings): {len(exact_mapped)}")
    print(f"non_mtk (exact DB strings): {len(exact_non)}")
    print(f"unverified (exact DB strings): {len(unverified)}")
    print(f"total mapped keys incl. normalized: {len(mapped)}")
    print(f"total non_mtk keys incl. normalized: {len(non_mtk)}")
    print(f"normalized keys added: {norm_added}")
    print(f"normalized collisions skipped: {norm_skipped}")
    print("unverified list:")
    for s in unverified:
        print("  -", repr(s), "=>", unverified_reasons[s])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
