# KaceChat
Minimal starter for a CVE watcher + local patch-check scaffold.

## What it does (minimal)
- Pulls recent CVEs from NVD (API) and known exploited CVEs from CISA KEV.
- Writes a combined JSON file to `data/cves.json`.
- Includes a placeholder patch-check module you can extend for Windows.

## Quick start
1) Create a virtualenv (optional)
2) Install deps:
   `pip install -r requirements.txt`
3) Run:
   `python src/main.py`

## Notes
- NVD API key is optional but recommended. Set `NVD_API_KEY` env var.
- Patch checks are stubs. We need to decide mapping from CVE -> KB for Windows.
