import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pandas as pd
import requests
from bs4 import BeautifulSoup

PRESHOW_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMMARY_CSV = os.path.join(PRESHOW_DIR, "data/summary/compare.csv")
FIELDS_CSV = os.path.join(PRESHOW_DIR, "data/summary/fields_coverage.csv")
SOURCES_JSON = os.path.join(PRESHOW_DIR, "data/summary/sources.json")
ACCESS_CSV = os.path.join(PRESHOW_DIR, "data/summary/access_methods.csv")

DBS = ["DBAASP", "APD3", "DRAMP", "dbAMP"]

def safe_get(url: str, timeout: float = 15) -> Optional[requests.Response]:
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r
    except Exception:
        pass
    return None

def parse_dbaasp() -> Dict[str, Any]:
    info = {"total_entries": None, "latest_version": "", "latest_update_date": "", "download": "", "api": "", "license": "", "bulk_download": "", "notes": ""}
    # Heuristic parsing from homepage; refine as needed
    resp = safe_get("https://dbaasp.org/")
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        # try to find counts or version info in page text
        for token in text.split():
            t = token.strip().lower()
            if t.startswith("v") and any(ch.isdigit() for ch in t[1:]):
                info["latest_version"] = token
                break
            if t.startswith("version"):
                parts = token.split(":")
                info["latest_version"] = parts[-1] if parts else token
                break
        # download/bulk
        info["download"] = "https://dbaasp.org/download"
        info["bulk_download"] = "1"
    # API unknown
    info["api"] = ""
    return info

def parse_apd3() -> Dict[str, Any]:
    info = {"total_entries": None, "latest_version": "", "latest_update_date": "", "download": "", "api": "", "license": "", "bulk_download": "", "notes": ""}
    resp = safe_get("https://aps.unmc.edu/")
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        # APD3: keep placeholders; exact selectors may vary
        info["download"] = "https://aps.unmc.edu/AP/database/query_download.php"
        info["bulk_download"] = "1"
    info["api"] = ""
    return info

def parse_dramp() -> Dict[str, Any]:
    info = {"total_entries": None, "latest_version": "", "latest_update_date": "", "download": "", "api": "", "license": "", "bulk_download": "", "notes": ""}
    resp = safe_get("http://dramp.cpu-bioinfor.org/")
    if resp:
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        info["download"] = "http://dramp.cpu-bioinfor.org/browse/All_Information/download/"
        info["bulk_download"] = "1"
        # try parse news page for update date
        n = safe_get("http://dramp.cpu-bioinfor.org/news.php")
        if n:
            from bs4 import BeautifulSoup as BS
            import re
            nt = BS(n.text, "html.parser").get_text(" ", strip=True)
            m = re.search(r"(20\\d{2}[-/]\\d{1,2}([-/]\\d{1,2})?)", nt)
            if m:
                info["latest_update_date"] = m.group(1)
    info["api"] = ""
    return info

def parse_dbamp() -> Dict[str, Any]:
    info = {"total_entries": None, "latest_version": "", "latest_update_date": "", "download": "", "api": "", "license": "", "bulk_download": "", "notes": ""}
    resp = safe_get("https://awi.cuhk.edu.cn/dbAMP/")
    if resp:
        info["download"] = "https://awi.cuhk.edu.cn/dbAMP/download"
        info["bulk_download"] = "1"
    info["api"] = ""
    return info

PARSERS = {"DBAASP": parse_dbaasp, "APD3": parse_apd3, "DRAMP": parse_dramp, "dbAMP": parse_dbamp}

def update_sources_json(results: Dict[str, Dict[str, Any]]):
    if os.path.exists(SOURCES_JSON):
        with open(SOURCES_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {db: {} for db in DBS}
        meta["_meta"] = {}
    for db, info in results.items():
        entry = meta.get(db, {})
        for k, v in info.items():
            if k in ("download", "api", "latest_version", "latest_update_date", "notes"):
                entry[k] = v
        meta[db] = entry
    meta["_meta"]["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    with open(SOURCES_JSON, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def fill_compare_csv(results: Dict[str, Dict[str, Any]]):
    comp = pd.read_csv(SUMMARY_CSV, dtype={"database": str, "total_entries": "string", "avg_field_completeness_pct": "string", "updates_last_3y": "string", "latest_version": "string", "latest_update_date": "string", "ai_score_0_5": "string", "notes": "string"})
    comp["database"] = comp["database"].str.strip()
    for i, row in comp.iterrows():
        db = row["database"]
        if db in results:
            if (pd.isna(row.get("latest_version", None))) or (str(row.get("latest_version", "")).strip() == ""):
                comp.at[i, "latest_version"] = str(results[db].get("latest_version", ""))
            if (pd.isna(row.get("latest_update_date", None))) or (str(row.get("latest_update_date", "")).strip() == ""):
                comp.at[i, "latest_update_date"] = str(results[db].get("latest_update_date", ""))
            # leave numeric fields for manual/secondary parsing unless confidently derivable
    comp.to_csv(SUMMARY_CSV, index=False)

def fill_access_csv(results: Dict[str, Dict[str, Any]]):
    acc = pd.read_csv(ACCESS_CSV, dtype={"database": str, "api_available": "Int64", "bulk_download": "Int64", "license": "string", "mirror_or_doi": "string"})
    acc["database"] = acc["database"].str.strip()
    for i, row in acc.iterrows():
        db = row["database"]
        if db in results:
            acc.at[i, "api_available"] = int(1 if results[db].get("api") else 0)
            acc.at[i, "bulk_download"] = int(1 if results[db].get("download") else 0)
            acc.at[i, "license"] = str(results[db].get("license", ""))
            acc.at[i, "mirror_or_doi"] = str(results[db].get("notes", ""))
    acc.to_csv(ACCESS_CSV, index=False)

def main():
    results: Dict[str, Dict[str, Any]] = {}
    for db in DBS:
        try:
            info = PARSERS[db]()
            results[db] = info
        except Exception as e:
            results[db] = {"notes": f"parser_error: {e}"}
    update_sources_json(results)
    fill_compare_csv(results)
    fill_access_csv(results)
    print("Fetch attempted; sources.json/compare.csv/access_methods.csv updated with available info.")

if __name__ == "__main__":
    main()