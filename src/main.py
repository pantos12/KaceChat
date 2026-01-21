from fetch_cves import fetch_nvd_recent, fetch_cisa_kev, merge_cves, sort_by_date, write_json


def main():
    nvd = fetch_nvd_recent(days=7, max_results=200)
    kev = fetch_cisa_kev()
    merged = sort_by_date(merge_cves(nvd, kev))
    write_json("data/cves.json", merged)
    print(f"Wrote {len(merged)} CVEs to data/cves.json")


if __name__ == "__main__":
    main()
