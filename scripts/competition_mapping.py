import argparse
import re
import time
import sqlite3
from pathlib import Path
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE = "https://www.transfermarkt.de"
URL_TM = BASE + "/jumplist/startseite/wettbewerb/{code}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
}

RE_COUNTRY_ID = re.compile(r"/wettbewerbe/national/wettbewerbe/(\d+)")
RE_TIER_NUM = re.compile(r"(\d+)")


def extract_country_id(html: str):
    m = RE_COUNTRY_ID.search(html)
    return int(m.group(1)) if m else None


def extract_tier(soup: BeautifulSoup):
    # Find the label span that contains "Ligahöhe:" and then its nested content span
    for lab in soup.select("span.data-header__label"):
        lab_text = lab.get_text(" ", strip=True).replace("\xa0", " ")
        if "Ligahöhe" in lab_text:
            content = lab.select_one("span.data-header__content")
            if not content:
                return None
            val = content.get_text(" ", strip=True).replace("\xa0", " ")
            if "Jugendliga" in val:
                return "Youth"
            if "Reserveliga" in val:
                return "Reserve"
            if "Staatsmeisterschaft" in val:
                return "StateChampionship"
            if "Playoff" in val or "Relegation" in val:
                return "PlayoffRelegation"
            m = RE_TIER_NUM.search(val)  # "1.Liga" -> 1
            return int(m.group(1)) if m else None
    return None


def fetch_comp_meta(code: str, session: requests.Session, sleep_s: float = 0.8) -> dict:
    url = URL_TM.format(code=code)
    r = session.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # league_name: usually the H1 on the page
    h1 = soup.find("h1")
    league_name = h1.get_text(strip=True) if h1 else None

    # tier: parse from the "Ligahöhe" label block
    tier = extract_tier(soup)

    # country_id: find the link to /wettbewerbe/national/wettbewerbe/<id>
    country_id = extract_country_id(r.text)

    time.sleep(sleep_s)  # be polite

    return {
        "competition_id": code,
        "league_name": league_name,
        "country_id": country_id,
        "tier": tier,
        "source_url": url,
    }


def build_mapping(codes: List[str], sleep_s: float) -> pd.DataFrame:
    codes = [str(c).strip() for c in codes if str(c).strip()]
    codes = sorted(set(codes))  # unique

    rows = []
    with requests.Session() as session:
        for code in tqdm(codes, desc="Fetching competitions"):
            try:
                rows.append(fetch_comp_meta(code, session=session, sleep_s=sleep_s))
            except requests.HTTPError as e:
                rows.append({
                    "competition_id": code,
                    "league_name": None,
                    "country_id": None,
                    "tier": None,
                    "source_url": URL_TM.format(code=code),
                    "error": f"HTTPError: {e}",
                })
            except Exception as e:
                rows.append({
                    "competition_id": code,
                    "league_name": None,
                    "country_id": None,
                    "tier": None,
                    "source_url": URL_TM.format(code=code),
                    "error": f"Error: {e}",
                })

    df = pd.DataFrame(rows)
    return df


def load_competition_ids(db_path: Path) -> List[str]:
    conn = sqlite3.connect(db_path)
    try:
        query = """
        SELECT transferSource_competitionId AS competition_id FROM tu_data_transfers
        UNION
        SELECT transferDestination_competitionId AS competition_id FROM tu_data_transfers;
        """
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    return df["competition_id"].dropna().astype(str).tolist()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build competition mapping from Transfermarkt")
    parser.add_argument("--db", default="data/tu_data.db", help="Path to SQLite database")
    parser.add_argument("--out", default="data/competition_mapping.csv", help="Output CSV path")
    parser.add_argument("--sleep", type=float, default=0.8, help="Sleep between requests (seconds)")
    args = parser.parse_args()

    db_path = Path(args.db)
    out_path = Path(args.out)

    codes = load_competition_ids(db_path)
    df = build_mapping(codes, sleep_s=args.sleep)

    # Normalize dtypes before writing
    if "country_id" in df.columns:
        df["country_id"] = pd.to_numeric(df["country_id"], errors="coerce").astype("Int64")
    if "tier" in df.columns:
        # tier can be numeric or labels (e.g., Youth/Reserve/StateChampionship)
        df["tier"] = df["tier"].astype("string")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path.resolve()}")


if __name__ == "__main__":
    main()
