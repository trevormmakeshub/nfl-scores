"""Write completed 2026 NFL games from the public nflverse schedule.

Scores only. Games without both scores are left out. No odds and no model.
"""

from __future__ import annotations

import csv
import urllib.request
from pathlib import Path

URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "completed_games.csv"
GAME_TYPES = {"REG", "WC", "DIV", "CON", "SB"}


def main() -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "nfl-scores/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        text = response.read().decode("utf-8")
    rows = []
    for game in csv.DictReader(text.splitlines()):
        if str(game.get("season")) != "2026":
            continue
        if game.get("game_type") not in GAME_TYPES:
            continue
        away_score = (game.get("away_score") or "").strip()
        home_score = (game.get("home_score") or "").strip()
        game_date = (game.get("gameday") or "").strip()
        away = (game.get("away_team") or "").strip()
        home = (game.get("home_team") or "").strip()
        if not game_date or not away or not home or not away_score or not home_score:
            continue
        rows.append(
            {
                "date": game_date,
                "away": away,
                "home": home,
                "away_score": int(float(away_score)),
                "home_score": int(float(home_score)),
            }
        )
    rows.sort(key=lambda row: (row["date"], row["away"], row["home"]))
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "away", "home", "away_score", "home_score"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows {len(rows)}")
    print(f"min date {rows[0]['date']}")
    print(f"max date {rows[-1]['date']}")


if __name__ == "__main__":
    main()
