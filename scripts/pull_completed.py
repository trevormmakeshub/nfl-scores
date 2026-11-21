"""Write completed 2026 NFL games from the public nflverse schedule.

Scores only. Games without both scores are left out. No odds and no model.
"""

from __future__ import annotations

import csv
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "completed_games.csv"
README = ROOT / "README.md"
NOTES = ROOT / "NOTES.md"
GAME_TYPES = {"REG", "WC", "DIV", "CON", "SB"}


def download_schedule() -> str:
    request = urllib.request.Request(URL, headers={"User-Agent": "nfl-scores/1.0"})
    last = "not tried"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            if exc.code in {404, 410}:
                break
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < 2:
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"schedule download failed: {last}")


def main() -> None:
    text = download_schedule()
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
    write_docs(rows)
    print(f"rows {len(rows)}")
    print(f"min date {rows[0]['date']}")
    print(f"max date {rows[-1]['date']}")
    log_path = ROOT / "refresh.log"
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            f"{datetime.now().isoformat(timespec='seconds')} rows {len(rows)} "
            f"min {rows[0]['date']} max {rows[-1]['date']}\n"
        )
    import subprocess
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_scores.py")], cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def write_docs(rows: list[dict]) -> None:
    """Keep the score notes on the same rows the script just wrote."""
    teams = {row["away"] for row in rows} | {row["home"] for row in rows}
    ties = [
        row for row in rows
        if row["away_score"] == row["home_score"]
    ]
    if ties:
        tie_text = "; ".join(
            f"{row['date']} {row['away']} at {row['home']} {row['away_score']}-{row['home_score']}"
            for row in ties
        )
        tie_sentence = f"Tied games: {len(ties)} ({tie_text}). A tie is not a win or a loss."
    else:
        tie_sentence = "There are no ties."
    min_date = rows[0]["date"]
    max_date = rows[-1]["date"]
    README.write_text(
        "# NFL scores 2026\n\n"
        f"Completed 2026 games from the public nflverse schedule, {min_date} through {max_date}. "
        "Scores only. No model. No odds.\n",
        encoding="utf-8",
        newline="\n",
    )
    NOTES.write_text(
        "Completed 2026 NFL games from the public nflverse schedule "
        "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv.\n"
        f"The file was downloaded on {date.today().isoformat()}. "
        f"completed_games.csv has {len(rows)} games. "
        f"Min date is {min_date}. Max date is {max_date}.\n"
        "Columns are date, away, home, away_score, and home_score. "
        "Games without both scores were left out. "
        f"All {len(teams)} teams have at least one decision. "
        f"{tie_sentence} There is no model and there are no odds.\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
