#!/usr/bin/env python3
"""MEER Chip Check — build index.html from mdm-models.json + verified MT mapping.

Row: [brand, name, code, chipset, mt, nm, cpu, gpu, route, year, verified,
      android, key, mtk]
  mt  = MediaTek MT number (e.g. MT6789H) or None
  key = compare key: mt if present; else normalized chipset name for non-MTK;
        None when unknown/unverified
  mtk = 1 if MediaTek-family chip, else 0
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone

MT_RE = re.compile(r"^MT\d{4}[A-Z]?$", re.I)
ANDROID_RE = re.compile(r"Android (\d+)")


def norm_key(s):
    """Normalize a chipset string for mapping lookup."""
    s = (s or "").strip()
    s = re.sub(r"^(MediaTek|Qualcomm)\s+", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s)
    return s.strip().upper()


def norm_cmp(s):
    """Normalize a chipset string for non-MTK compare keys."""
    s = (s or "").strip().lower()
    s = re.sub(r"^(mediatek|qualcomm)\s+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def build_lookup(mapping):
    """Build {NORMALIZED: entry} from the mapping's mapped section."""
    look = {}
    for k, v in mapping.get("mapped", {}).items():
        look[norm_key(k)] = v
        # also index without the " ULTIMATE" suffix, both ways
        base = re.sub(r"\s+ULTIMATE$", "", norm_key(k))
        look.setdefault(base, v)
    return look


def build_db(models, mapping):
    look = build_lookup(mapping)
    non_mtk = {norm_key(k) for k in mapping.get("non_mtk", {}).keys()}
    rows = {}
    order = []
    for m in models:
        brand = (m.get("brand") or "").strip()
        name = (m.get("name") or m.get("model") or "").strip()
        code = (m.get("code") or "").strip() or "unknown"
        chipset = (m.get("chipset") or "").strip() or "unknown"
        tags = [str(t) for t in (m.get("tags") or [])]

        mt = nm = cpu = gpu = None
        mtk = 0
        key = None
        nk = norm_key(chipset)
        if chipset != "unknown" and MT_RE.match(chipset.strip()):
            mt = chipset.strip().upper()
            mtk = 1
            key = mt
        elif nk in look:
            e = look[nk]
            mt = e.get("mt")
            nm = e.get("nm")
            cpu = e.get("cpu")
            gpu = e.get("gpu")
            mtk = 1
            key = mt
        elif nk in non_mtk:
            mtk = 0
            key = norm_cmp(chipset)
        else:
            # Unverified: MediaTek family or not?
            low = chipset.lower()
            if ("helio" in low or "dimensity" in low or "mediatek" in low
                    or "MediaTek" in tags):
                mtk = 1
                key = None  # MT unknown -> cannot compare
            elif chipset == "unknown":
                mtk = 0
                key = None
            else:
                mtk = 0
                key = norm_cmp(chipset)

        route = m.get("route")
        if m.get("route_unknown") or not route or route == "unknown":
            route = None
        year = m.get("year")
        verified = 1 if m.get("verified") else 0
        note = m.get("note") or ""
        am = ANDROID_RE.search(note)
        android = am.group(1) if am else None

        row = [brand, name, code, chipset, mt, nm, cpu, gpu, route, year,
               verified, android, key, mtk]

        # Dedupe: prefer verified row, then row with a note.
        dk = code.lower() if code != "unknown" else (brand + "|" + name).lower()
        if dk in rows:
            old = rows[dk]
            old_m = old[14]
            score = (verified, 1 if note else 0)
            old_score = (old_m.get("verified") or 0,
                         1 if (old_m.get("note") or "") else 0)
            if score <= old_score:
                continue
            rows[dk] = row + [m]
        else:
            rows[dk] = row + [m]
            order.append(dk)

    db = [rows[k][:14] for k in order]
    db.sort(key=lambda r: ((r[0] or "").lower(), (r[1] or "").lower()))
    return db


def mt_base(mt):
    return re.sub(r"^MT", "", mt or "", flags=re.I).rstrip(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def compare(a, b):
    ka, kb = a[12], b[12]
    if not ka or not kb:
        return "UNKNOWN"
    if ka == kb:
        return "MATCH"
    if a[13] == 1 and b[13] == 1 and a[4] and b[4] and mt_base(a[4]) == mt_base(b[4]):
        return "FAMILY"
    return "NO_MATCH"


def self_checks(db):
    by_code = {}
    for r in db:
        by_code.setdefault(r[2].upper(), r)
    fails = []

    def check(code, chipset, mt):
        r = by_code.get(code.upper())
        if not r:
            fails.append(f"{code}: NOT FOUND in DB")
            return
        if r[3] != chipset:
            fails.append(f"{code}: chipset {r[3]!r} != {chipset!r}")
        if r[4] != mt:
            fails.append(f"{code}: mt {r[4]!r} != {mt!r}")

    check("KM6", "Helio G100 Ultimate", "MT6789H")
    check("X6840", "Helio G81 Ultimate", "MT6769")
    check("CN5c", "Helio G200 Ultimate", "MT6789")
    check("X6885", "Helio G200", "MT6789")

    def cmp_check(c1, c2, want):
        a, b = by_code.get(c1.upper()), by_code.get(c2.upper())
        if not a or not b:
            fails.append(f"compare {c1} vs {c2}: model missing")
            return
        got = compare(a, b)
        if got != want:
            fails.append(f"compare {c1} vs {c2}: {got} != {want}")

    cmp_check("KM6", "X6840", "NO_MATCH")
    cmp_check("CN5c", "X6885", "MATCH")
    cmp_check("KM6", "KM7", "FAMILY")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="/home/hatch/workspace/hamza-tool-pro/tools/mdm-models.json")
    ap.add_argument("--mapping", default="/home/hatch/workspace/chipcheck/mt-mapping.json")
    ap.add_argument("--template", default="/home/hatch/workspace/chipcheck/template.html")
    ap.add_argument("--out", default="/home/hatch/workspace/chipcheck/index.html")
    ap.add_argument("--stamp", default=None)
    args = ap.parse_args()

    with open(args.models) as f:
        models = json.load(f)["models"]
    with open(args.mapping) as f:
        mapping = json.load(f)

    db = build_db(models, mapping)
    fails = self_checks(db)
    if fails:
        print("SELF-CHECK FAILURES:")
        for fl in fails:
            print("  -", fl)
        sys.exit(1)

    with open(args.template) as f:
        tpl = f.read()
    stamp = args.stamp or datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC")
    html = (tpl.replace("__DB_JSON__", json.dumps(db, ensure_ascii=False, separators=(",", ":")))
            .replace("__MODEL_COUNT__", f"{len(db):,}")
            .replace("__BUILD_STAMP__", stamp))
    with open(args.out, "w") as f:
        f.write(html)

    n_mt = sum(1 for r in db if r[4])
    n_unk = sum(1 for r in db if r[13] == 1 and not r[4])
    n_nonmtk = sum(1 for r in db if r[13] == 0 and r[12])
    n_nokey = sum(1 for r in db if not r[12])
    print(f"models in: {len(models)}  rows out: {len(db)}")
    print(f"with MT number: {n_mt} | MTK unverified: {n_unk} | "
          f"non-MTK keyed: {n_nonmtk} | no compare key: {n_nokey}")
    print(f"wrote {args.out} ({len(html):,} bytes)")
    print("SELF-CHECKS: all 7 PASS")


if __name__ == "__main__":
    main()
