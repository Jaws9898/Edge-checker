import os
import requests
from difflib import SequenceMatcher
from typing import Optional


# Maps API-Football league IDs to The Odds API sport keys
SPORT_KEYS = {
    39:  "soccer_epl",
    140: "soccer_spain_la_liga",
    78:  "soccer_germany_bundesliga",
    135: "soccer_italy_serie_a",
    61:  "soccer_france_ligue_one",
}

# Demo odds data for when no API key is set
DEMO_ODDS = [
    {"bookmaker": "Bet365",        "home": 2.50, "draw": 3.40, "away": 2.80},
    {"bookmaker": "William Hill",  "home": 2.45, "draw": 3.30, "away": 2.90},
    {"bookmaker": "Sky Bet",       "home": 2.55, "draw": 3.25, "away": 2.85},
    {"bookmaker": "Betfair",       "home": 2.62, "draw": 3.45, "away": 2.75},
    {"bookmaker": "Paddy Power",   "home": 2.50, "draw": 3.50, "away": 2.80},
    {"bookmaker": "Ladbrokes",     "home": 2.40, "draw": 3.20, "away": 2.90},
    {"bookmaker": "Coral",         "home": 2.45, "draw": 3.30, "away": 2.88},
]


class OddsService:
    BASE_URL = "https://api.the-odds-api.com/v4"
    SPORT_KEYS = SPORT_KEYS

    def __init__(self):
        self.api_key = os.environ.get("ODDS_API_KEY")

    @property
    def demo_mode(self) -> bool:
        return not self.api_key

    def get_match_odds(
        self,
        home_team: str,
        away_team: str,
        sport_key: Optional[str],
    ) -> Optional[dict]:
        """
        Returns best odds and per-bookmaker breakdown for a given match.
        Structure: {"home_team": str, "away_team": str, "bookmakers": [...], "best": {...}}
        """
        if self.demo_mode or not sport_key:
            return _build_result(home_team, away_team, DEMO_ODDS)

        try:
            resp = requests.get(
                f"{self.BASE_URL}/sports/{sport_key}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": "uk",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                },
                timeout=10,
            )
            resp.raise_for_status()
            events = resp.json()
        except Exception:
            return _build_result(home_team, away_team, DEMO_ODDS)

        event = _find_event(events, home_team, away_team)
        if not event:
            return _build_result(home_team, away_team, DEMO_ODDS)

        home_name = event["home_team"]
        away_name = event["away_team"]
        bookmakers = []
        for bk in event.get("bookmakers", []):
            for market in bk.get("markets", []):
                if market["key"] != "h2h":
                    continue
                prices = {o["name"]: o["price"] for o in market["outcomes"]}
                bookmakers.append({
                    "bookmaker": bk["title"],
                    "home": prices.get(home_name),
                    "draw": prices.get("Draw"),
                    "away": prices.get(away_name),
                })

        return _build_result(home_name, away_name, bookmakers)


def _find_event(events: list, home: str, away: str) -> Optional[dict]:
    def similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    for event in events:
        if (
            similarity(event.get("home_team", ""), home) > 0.6
            and similarity(event.get("away_team", ""), away) > 0.6
        ):
            return event
    return None


def _build_result(home_team: str, away_team: str, bookmakers: list) -> dict:
    valid = [b for b in bookmakers if b.get("home") and b.get("draw") and b.get("away")]
    best_home = max((b["home"] for b in valid), default=None)
    best_draw = max((b["draw"] for b in valid), default=None)
    best_away = max((b["away"] for b in valid), default=None)
    return {
        "home_team": home_team,
        "away_team": away_team,
        "bookmakers": valid,
        "best": {"home": best_home, "draw": best_draw, "away": best_away},
    }


def implied_probability(decimal_odds: float) -> int:
    """Convert decimal odds to implied probability %."""
    if not decimal_odds or decimal_odds <= 1:
        return 0
    return round((1 / decimal_odds) * 100)
