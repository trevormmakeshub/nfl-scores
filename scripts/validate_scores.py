"""Check the completed NFL score file. No model and no odds."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "completed_games.csv"


def main() -> int:
    with PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    problems = 0
    if not rows:
        print("fail empty file")
        return 1
    dates = [row["date"] for row in rows]
    teams = {row["away"] for row in rows} | {row["home"] for row in rows}
    keys = [(row["date"], row["away"], row["home"]) for row in rows]
    if len(keys) != len(set(keys)):
        print("fail duplicate game")
        problems += 1
    if max(dates) > date.today().isoformat():
        print(f"fail date {max(dates)} is after today")
        problems += 1
    missing = sum(1 for row in rows if row["away_score"] == "" or row["home_score"] == "")
    if missing:
        print(f"fail {missing} rows lack scores")
        problems += 1
    if len(teams) != 32:
        print(f"fail team count {len(teams)}")
        problems += 1
    print(f"rows {len(rows)}")
    print(f"min {min(dates)}")
    print(f"max {max(dates)}")
    print(f"teams {len(teams)}")
    if problems:
        print(f"validation fail {problems}")
        return 1
    print("validation pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
