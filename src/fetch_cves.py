import json
import os
from datetime import datetime, timedelta, timezone
from dateutil.parser import isoparse
import requests

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CISA_KEV = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def fetch_nvd_recent(days=7, max_results=200):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    params = {
        "pubStartDate": start.isoformat(),
        "pubEndDate": end.isoformat(),
        "resultsPerPage": max_results,
    }
    headers = {}
    api_key = os.getenv("NVD_API_KEY")
    if api_key:
        headers["apiKey"] = api_key

    r = requests.get(NVD_API, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    out = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        out.append({
            "id": cve.get("id"),
            "source": "NVD",
            "published": cve.get("published"),
            "lastModified": cve.get("lastModified"),
            "description": _first_desc(cve),
        })
    return out


def fetch_cisa_kev():
    r = requests.get(CISA_KEV, timeout=30)
    r.raise_for_status()
    data = r.json()

    out = []
    for item in data.get("vulnerabilities", []):
        out.append({
            "id": item.get("cveID"),
            "source": "CISA-KEV",
            "published": item.get("dateAdded"),
            "lastModified": item.get("dateAdded"),
            "description": item.get("shortDescription"),
            "product": item.get("product"),
            "vendor": item.get("vendorProject"),
        })
    return out


def _first_desc(cve):
    descs = cve.get("descriptions", [])
    for d in descs:
        if d.get("lang") == "en":
            return d.get("value")
    if descs:
        return descs[0].get("value")
    return None


def merge_cves(*lists):
    by_id = {}
    for lst in lists:
        for item in lst:
            cid = item.get("id")
            if not cid:
                continue
            existing = by_id.get(cid, {})
            merged = {**existing, **item}
            by_id[cid] = merged
    return list(by_id.values())


def sort_by_date(items):
    def parse_dt(x):
        v = x.get("published") or ""
        try:
            return isoparse(v)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)
    return sorted(items, key=parse_dt, reverse=True)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    nvd = fetch_nvd_recent(days=7, max_results=200)
    kev = fetch_cisa_kev()
    merged = merge_cves(nvd, kev)
    merged = sort_by_date(merged)
    write_json("data/cves.json", merged)
    print(f"Wrote {len(merged)} CVEs to data/cves.json")
