#!/usr/bin/env python3
"""MEER Chip Check — verify a built/live page.

Fetches the page HTML (URL or local file), extracts its embedded DB + its OWN
<script> logic, and runs the 7 self-checks in node against the page's own
functions (findByCode / compareVerdict / searchModels). Also asserts the
firmware warning + verdict labels are present in the HTML.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import os

NODE_TEST = """
const asserts = [];
function eq(name, got, want) {
  const ok = got === want;
  asserts.push((ok ? "PASS" : "FAIL") + " | " + name + " | got=" + JSON.stringify(got) + " want=" + JSON.stringify(want));
  if (!ok) process.exitCode = 1;
}
const km6 = findByCode("KM6");
const x6840 = findByCode("X6840");
const cn5c = findByCode("CN5c");
const x6885 = findByCode("X6885");
const km7 = findByCode("KM7");
eq("KM6 chipset", km6 && km6[3], "Helio G100 Ultimate");
eq("KM6 mt", km6 && km6[4], "MT6789H");
eq("X6840 chipset", x6840 && x6840[3], "Helio G81 Ultimate");
eq("X6840 mt", x6840 && x6840[4], "MT6769");
eq("CN5c chipset", cn5c && cn5c[3], "Helio G200 Ultimate");
eq("CN5c mt", cn5c && cn5c[4], "MT6789");
eq("X6885 chipset", x6885 && x6885[3], "Helio G200");
eq("X6885 mt", x6885 && x6885[4], "MT6789");
eq("KM6 vs X6840", compareVerdict(km6, x6840).v, "NO_MATCH");
eq("CN5c vs X6885", compareVerdict(cn5c, x6885).v, "MATCH");
eq("KM6 vs KM7", compareVerdict(km6, km7).v, "FAMILY");
eq("search KM6 first", (searchModels("KM6")[0] || [])[2], "KM6");
eq("DB rows > 2000", DB.length > 2000, true);
console.log(asserts.join("\\n"));
console.log("DB rows: " + DB.length);
"""


def fetch(url=None, path=None):
    if path:
        with open(path) as f:
            return f.read()
    r = subprocess.run(["curl", "-sL", "--max-time", "60", url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("curl failed:", r.stderr[:500])
        sys.exit(2)
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None)
    ap.add_argument("--file", default=None)
    args = ap.parse_args()
    html = fetch(args.url, args.file)
    print(f"page bytes: {len(html):,}")

    fails = []
    # Static content checks
    for needle, label in [
        ("MEER Chip Check", "title"),
        ("Firmware hamesha apne model ki", "firmware warning"),
        ("NO MATCH", "NO MATCH label"),
        ("MALOOM NAHI", "MALOOM NAHI label"),
        ("compareVerdict", "compare logic present"),
    ]:
        if needle not in html:
            fails.append(f"missing in HTML: {label} ({needle!r})")

    m = re.search(r"<script>(.*?)</script>", html, re.S)
    if not m:
        print("FAIL: no <script> block found")
        sys.exit(1)
    script = m.group(1)
    if "const DB = " not in script:
        print("FAIL: embedded DB not found in script")
        sys.exit(1)

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(script)
        f.write("\n" + NODE_TEST)
        tmp = f.name
    try:
        r = subprocess.run(["node", tmp], capture_output=True, text=True,
                           timeout=120)
    finally:
        os.unlink(tmp)
    print(r.stdout)
    if r.stderr:
        print("node stderr:", r.stderr[:2000])
    if r.returncode != 0:
        fails.append("node self-checks failed (see above)")

    if fails:
        print("VERIFY FAILURES:")
        for fl in fails:
            print("  -", fl)
        sys.exit(1)
    print("VERIFY: all checks PASS")


if __name__ == "__main__":
    main()
