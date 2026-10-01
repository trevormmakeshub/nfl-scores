"""Print each team's 2026 wins, losses, and win rate from completed_games.csv.

No odds and no model. A tie is not a win or a loss. Win rate is wins divided by
wins plus losses. The rate is left blank when a team has no decision.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

GAMES = Path(__file__).resolve().parents[1] / "completed_games.csv"


def main() -> None:
    wins: dict[str, int] = defaultdict(int)
    losses: dict[str, int] = defaultdict(int)
    ties: dict[str, int] = defaultdict(int)
    teams: set[str] = set()
    with GAMES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not str(row["date"]).startswith("2026"):
                continue
            away = row["away"].strip()
            home = row["home"].strip()
            away_score = int(row["away_score"])
            home_score = int(row["home_score"])
            teams.add(away)
            teams.add(home)
            if home_score > away_score:
                wins[home] += 1
                losses[away] += 1
            elif away_score > home_score:
                wins[away] += 1
                losses[home] += 1
            else:
                ties[home] += 1
                ties[away] += 1
    for team in sorted(teams):
        won = wins[team]
        lost = losses[team]
        decisions = won + lost
        rate = "" if decisions == 0 else f"{won / decisions:.3f}"
        print(f"{team} wins={won} losses={lost} win_rate={rate}")
        if ties[team]:
            print(f"{team} ties={ties[team]}")


if __name__ == "__main__":
    main()
