#!/usr/bin/env python3
"""MEER Chip Check v1.0 — replace the APK release asset in place (same
release, same download link). DELETE via raw urllib (204 empty body crashes
gh_bulk_upload.api_request's JSON parser), upload via gh_release.py, verify
size via API + SHA-256 via the public download link."""
import hashlib
import os
import subprocess
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/hamza-tool-pro/rebuild")
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from gh_bulk_upload import api_request  # noqa: E402
from dynamic_credentials import add_surrogate_to_request  # noqa: E402

REPO = "Hamzaagsm/chipcheck"
TAG = "v1.0"
RELEASE_ID = 449764937
OLD_ASSET_ID = 762770886
APK = "/home/hatch/workspace/chipcheck/MEERChipCheck-v1.0.apk"
NAME = "MEERChipCheck-v1.0.apk"
GH_RELEASE = "/home/hatch/workspace/custom-connectors/custom.legacy-github/bin/gh_release.py"
CRED = "custom.github"
ALLOWED = ("api.github.com", "uploads.github.com")
DL = f"https://github.com/{REPO}/releases/download/{TAG}/{NAME}"


def delete_asset(asset_id):
    url = f"https://api.github.com/repos/{REPO}/releases/assets/{asset_id}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "muse-github-skill/1.0")
    add_surrogate_to_request(req, CRED, allowed_hosts=ALLOWED)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def main():
    expect_size = os.path.getsize(APK)
    h = hashlib.sha256()
    with open(APK, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    expect_hash = h.hexdigest()
    print(f"local APK: {expect_size} B sha256={expect_hash}", flush=True)

    s = delete_asset(OLD_ASSET_ID)
    print(f"delete old asset {OLD_ASSET_ID}: {s}", flush=True)
    assert s == 204, f"delete failed: {s}"

    env = dict(os.environ)
    env["PYTHONPATH"] = "/opt/muse/skills/custom-connector-setup/bin"
    r = subprocess.run(
        [sys.executable, GH_RELEASE, "upload", "--repo", REPO,
         "--tag", TAG, "--file", APK, "--asset-name", NAME],
        capture_output=True, text=True, timeout=600, env=env)
    print(f"upload: rc={r.returncode} {r.stdout.strip()}", flush=True)
    assert r.returncode == 0, f"upload failed: {r.stderr}"

    s, j = api_request("GET", f"https://api.github.com/repos/{REPO}/releases/{RELEASE_ID}")
    assert s == 200, f"release read failed: {s}"
    matches = [a for a in j["assets"] if a["name"] == NAME]
    assert len(matches) == 1, f"asset {NAME} count {len(matches)}"
    print(f"api verify: new asset id={matches[0]['id']} size={matches[0]['size']} expect={expect_size}", flush=True)
    assert matches[0]["size"] == expect_size, "size mismatch"

    h2 = hashlib.sha256()
    with urllib.request.urlopen(DL, timeout=120) as resp:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            h2.update(chunk)
    print(f"download-link sha256: {h2.hexdigest()}", flush=True)
    assert h2.hexdigest() == expect_hash, "download hash mismatch"
    print("APK SHIPPED + VERIFIED", flush=True)


if __name__ == "__main__":
    main()
