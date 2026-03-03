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

# Generic fallback demo odds (h2h only)
DEMO_ODDS = [
    {"bookmaker": "Bet365",        "home": 2.50, "draw": 3.40, "away": 2.80},
    {"bookmaker": "William Hill",  "home": 2.45, "draw": 3.30, "away": 2.90},
    {"bookmaker": "Sky Bet",       "home": 2.55, "draw": 3.25, "away": 2.85},
    {"bookmaker": "Betfair",       "home": 2.62, "draw": 3.45, "away": 2.75},
    {"bookmaker": "Paddy Power",   "home": 2.50, "draw": 3.50, "away": 2.80},
]

# Full per-fixture, per-bookmaker, per-market demo odds
# Keys: home, draw, away, btts (Yes price), over25 (Over 2.5 price)
FIXTURE_DEMO_ODDS_FULL = {
    1001: {  # Arsenal vs Chelsea
        "Bet365":       {"home": 2.20, "draw": 3.60, "away": 3.40, "btts": 1.72, "over25": 1.85},
        "William Hill": {"home": 2.15, "draw": 3.50, "away": 3.50, "btts": 1.70, "over25": 1.80},
        "Sky Bet":      {"home": 2.25, "draw": 3.60, "away": 3.30, "btts": 1.75, "over25": 1.88},
        "Betfair":      {"home": 2.28, "draw": 3.65, "away": 3.35, "btts": 1.74, "over25": 1.87},
        "Paddy Power":  {"home": 2.20, "draw": 3.55, "away": 3.45, "btts": 1.72, "over25": 1.85},
        "Ladbrokes":    {"home": 2.15, "draw": 3.50, "away": 3.40, "btts": 1.68, "over25": 1.82},
    },
    1002: {  # Liverpool vs Man City
        "Bet365":       {"home": 2.10, "draw": 3.80, "away": 3.20, "btts": 1.80, "over25": 1.90},
        "William Hill": {"home": 2.05, "draw": 3.70, "away": 3.30, "btts": 1.77, "over25": 1.87},
        "Sky Bet":      {"home": 2.15, "draw": 3.75, "away": 3.10, "btts": 1.83, "over25": 1.92},
        "Betfair":      {"home": 2.18, "draw": 3.85, "away": 3.15, "btts": 1.82, "over25": 1.91},
        "Paddy Power":  {"home": 2.12, "draw": 3.80, "away": 3.20, "btts": 1.80, "over25": 1.90},
        "Ladbrokes":    {"home": 2.05, "draw": 3.70, "away": 3.25, "btts": 1.75, "over25": 1.86},
    },
    1003: {  # Man Utd vs Tottenham
        "Bet365":       {"home": 2.80, "draw": 3.40, "away": 2.50, "btts": 1.83, "over25": 1.95},
        "William Hill": {"home": 2.75, "draw": 3.30, "away": 2.55, "btts": 1.80, "over25": 1.91},
        "Sky Bet":      {"home": 2.85, "draw": 3.40, "away": 2.45, "btts": 1.85, "over25": 1.97},
        "Betfair":      {"home": 2.90, "draw": 3.50, "away": 2.50, "btts": 1.84, "over25": 1.96},
        "Paddy Power":  {"home": 2.80, "draw": 3.35, "away": 2.55, "btts": 1.83, "over25": 1.95},
        "Ladbrokes":    {"home": 2.70, "draw": 3.30, "away": 2.60, "btts": 1.78, "over25": 1.90},
    },
    1004: {  # Real Madrid vs Barcelona
        "Bet365":       {"home": 2.30, "draw": 3.50, "away": 2.90, "btts": 1.85, "over25": 1.95},
        "William Hill": {"home": 2.25, "draw": 3.40, "away": 3.00, "btts": 1.83, "over25": 1.92},
        "Sky Bet":      {"home": 2.35, "draw": 3.50, "away": 2.85, "btts": 1.87, "over25": 1.97},
        "Betfair":      {"home": 2.38, "draw": 3.60, "away": 2.88, "btts": 1.86, "over25": 1.96},
        "Paddy Power":  {"home": 2.30, "draw": 3.50, "away": 2.95, "btts": 1.85, "over25": 1.95},
        "Ladbrokes":    {"home": 2.25, "draw": 3.40, "away": 2.90, "btts": 1.80, "over25": 1.90},
    },
    1005: {  # Bayern Munich vs Dortmund
        "Bet365":       {"home": 1.60, "draw": 4.10, "away": 5.50, "btts": 1.90, "over25": 1.75},
        "William Hill": {"home": 1.57, "draw": 4.00, "away": 5.75, "btts": 1.87, "over25": 1.72},
        "Sky Bet":      {"home": 1.62, "draw": 4.10, "away": 5.40, "btts": 1.92, "over25": 1.77},
        "Betfair":      {"home": 1.65, "draw": 4.20, "away": 5.50, "btts": 1.91, "over25": 1.76},
        "Paddy Power":  {"home": 1.60, "draw": 4.00, "away": 5.60, "btts": 1.90, "over25": 1.75},
        "Ladbrokes":    {"home": 1.57, "draw": 4.00, "away": 5.75, "btts": 1.85, "over25": 1.70},
    },
    1006: {  # AC Milan vs Inter
        "Bet365":       {"home": 2.60, "draw": 3.30, "away": 2.60, "btts": 1.80, "over25": 1.95},
        "William Hill": {"home": 2.55, "draw": 3.20, "away": 2.70, "btts": 1.77, "over25": 1.92},
        "Sky Bet":      {"home": 2.65, "draw": 3.30, "away": 2.55, "btts": 1.83, "over25": 1.97},
        "Betfair":      {"home": 2.70, "draw": 3.40, "away": 2.60, "btts": 1.82, "over25": 1.96},
        "Paddy Power":  {"home": 2.62, "draw": 3.35, "away": 2.65, "btts": 1.80, "over25": 1.95},
        "Ladbrokes":    {"home": 2.55, "draw": 3.25, "away": 2.70, "btts": 1.75, "over25": 1.90},
    },
    1007: {  # Newcastle vs West Ham
        "Bet365":       {"home": 2.00, "draw": 3.60, "away": 3.60, "btts": 1.85, "over25": 2.00},
        "William Hill": {"home": 1.95, "draw": 3.50, "away": 3.75, "btts": 1.83, "over25": 1.97},
        "Sky Bet":      {"home": 2.05, "draw": 3.55, "away": 3.60, "btts": 1.87, "over25": 2.02},
        "Betfair":      {"home": 2.08, "draw": 3.65, "away": 3.55, "btts": 1.86, "over25": 2.01},
        "Paddy Power":  {"home": 2.00, "draw": 3.60, "away": 3.65, "btts": 1.85, "over25": 2.00},
        "Ladbrokes":    {"home": 1.95, "draw": 3.50, "away": 3.70, "btts": 1.80, "over25": 1.95},
    },
    1008: {  # Atletico Madrid vs Valencia
        "Bet365":       {"home": 1.75, "draw": 3.80, "away": 4.80, "btts": 1.95, "over25": 2.10},
        "William Hill": {"home": 1.72, "draw": 3.70, "away": 5.00, "btts": 1.92, "over25": 2.07},
        "Sky Bet":      {"home": 1.78, "draw": 3.80, "away": 4.70, "btts": 1.97, "over25": 2.12},
        "Betfair":      {"home": 1.80, "draw": 3.90, "away": 4.75, "btts": 1.96, "over25": 2.11},
        "Paddy Power":  {"home": 1.76, "draw": 3.85, "away": 4.80, "btts": 1.95, "over25": 2.10},
        "Ladbrokes":    {"home": 1.72, "draw": 3.75, "away": 4.90, "btts": 1.90, "over25": 2.05},
    },
    1009: {  # Bayer Leverkusen vs RB Leipzig
        "Bet365":       {"home": 1.90, "draw": 3.60, "away": 4.20, "btts": 1.87, "over25": 1.95},
        "William Hill": {"home": 1.85, "draw": 3.50, "away": 4.40, "btts": 1.85, "over25": 1.92},
        "Sky Bet":      {"home": 1.93, "draw": 3.60, "away": 4.10, "btts": 1.89, "over25": 1.97},
        "Betfair":      {"home": 1.95, "draw": 3.70, "away": 4.20, "btts": 1.88, "over25": 1.96},
        "Paddy Power":  {"home": 1.90, "draw": 3.65, "away": 4.25, "btts": 1.87, "over25": 1.95},
        "Ladbrokes":    {"home": 1.87, "draw": 3.55, "away": 4.30, "btts": 1.82, "over25": 1.90},
    },
    1010: {  # Juventus vs Napoli
        "Bet365":       {"home": 2.30, "draw": 3.40, "away": 3.00, "btts": 1.80, "over25": 1.95},
        "William Hill": {"home": 2.25, "draw": 3.30, "away": 3.10, "btts": 1.77, "over25": 1.92},
        "Sky Bet":      {"home": 2.35, "draw": 3.40, "away": 2.95, "btts": 1.83, "over25": 1.97},
        "Betfair":      {"home": 2.38, "draw": 3.50, "away": 3.00, "btts": 1.82, "over25": 1.96},
        "Paddy Power":  {"home": 2.30, "draw": 3.45, "away": 3.05, "btts": 1.80, "over25": 1.95},
        "Ladbrokes":    {"home": 2.25, "draw": 3.35, "away": 3.10, "btts": 1.75, "over25": 1.90},
    },
    1011: {  # PSG vs Lyon
        "Bet365":       {"home": 1.40, "draw": 5.00, "away": 7.50, "btts": 2.10, "over25": 1.90},
        "William Hill": {"home": 1.38, "draw": 4.80, "away": 8.00, "btts": 2.05, "over25": 1.87},
        "Sky Bet":      {"home": 1.42, "draw": 5.00, "away": 7.00, "btts": 2.12, "over25": 1.92},
        "Betfair":      {"home": 1.45, "draw": 5.20, "away": 7.50, "btts": 2.11, "over25": 1.91},
        "Paddy Power":  {"home": 1.40, "draw": 5.00, "away": 7.50, "btts": 2.10, "over25": 1.90},
        "Ladbrokes":    {"home": 1.38, "draw": 4.80, "away": 8.00, "btts": 2.05, "over25": 1.85},
    },
    1012: {  # Marseille vs Lille
        "Bet365":       {"home": 2.10, "draw": 3.40, "away": 3.40, "btts": 1.83, "over25": 1.97},
        "William Hill": {"home": 2.05, "draw": 3.30, "away": 3.50, "btts": 1.80, "over25": 1.94},
        "Sky Bet":      {"home": 2.15, "draw": 3.40, "away": 3.35, "btts": 1.85, "over25": 1.99},
        "Betfair":      {"home": 2.18, "draw": 3.50, "away": 3.35, "btts": 1.84, "over25": 1.98},
        "Paddy Power":  {"home": 2.10, "draw": 3.45, "away": 3.40, "btts": 1.83, "over25": 1.97},
        "Ladbrokes":    {"home": 2.05, "draw": 3.35, "away": 3.50, "btts": 1.78, "over25": 1.93},
    },
}

# Legacy list format — derived from full data for backward compatibility
FIXTURE_DEMO_ODDS = {
    fid: [
        {"bookmaker": bk, "home": v["home"], "draw": v["draw"], "away": v["away"]}
        for bk, v in bks.items()
    ]
    for fid, bks in FIXTURE_DEMO_ODDS_FULL.items()
}


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
        fixture_id: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Returns best odds and per-bookmaker breakdown for a given match.
        Structure: {"home_team": str, "away_team": str, "bookmakers": [...], "best": {...}}
        """
        if self.demo_mode or not sport_key:
            demo_bks = FIXTURE_DEMO_ODDS.get(fixture_id, DEMO_ODDS)
            return _build_result(home_team, away_team, demo_bks)

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

    def get_fixture_odds_full(
        self,
        fixture_id: int,
        home_team: str,
        away_team: str,
        sport_key: Optional[str] = None,
    ) -> dict:
        """
        Returns per-bookmaker odds for ALL markets (home/draw/away/btts/over25).
        Used by the acca engine to compare combined odds across bookmakers.

        Returns: { "Bet365": {"home": x, "draw": x, "away": x, "btts": x, "over25": x}, ... }
        """
        if self.demo_mode or not sport_key:
            return FIXTURE_DEMO_ODDS_FULL.get(fixture_id, _generic_full_odds())

        # Real API: fetch h2h + btts + totals in one call
        try:
            resp = requests.get(
                f"{self.BASE_URL}/sports/{sport_key}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": "uk",
                    "markets": "h2h,both_teams_to_score,totals",
                    "oddsFormat": "decimal",
                },
                timeout=10,
            )
            resp.raise_for_status()
            events = resp.json()
        except Exception:
            return FIXTURE_DEMO_ODDS_FULL.get(fixture_id, _generic_full_odds())

        event = _find_event(events, home_team, away_team)
        if not event:
            return FIXTURE_DEMO_ODDS_FULL.get(fixture_id, _generic_full_odds())

        home_name = event["home_team"]
        away_name = event["away_team"]
        result = {}

        for bk in event.get("bookmakers", []):
            bk_name = bk["title"]
            entry = {}
            for market in bk.get("markets", []):
                key = market["key"]
                prices = {o["name"]: o["price"] for o in market["outcomes"]}
                if key == "h2h":
                    entry["home"] = prices.get(home_name)
                    entry["draw"] = prices.get("Draw")
                    entry["away"] = prices.get(away_name)
                elif key == "both_teams_to_score":
                    entry["btts"] = prices.get("Yes")
                elif key == "totals":
                    for o in market["outcomes"]:
                        if o["name"] == "Over" and abs(o.get("point", 0) - 2.5) < 0.1:
                            entry["over25"] = o["price"]
            if entry:
                result[bk_name] = entry

        return result or FIXTURE_DEMO_ODDS_FULL.get(fixture_id, _generic_full_odds())


def _generic_full_odds() -> dict:
    """Generic per-bookmaker full-market odds when fixture has no specific data."""
    return {
        "Bet365":       {"home": 2.50, "draw": 3.40, "away": 2.80, "btts": 1.80, "over25": 1.95},
        "William Hill": {"home": 2.45, "draw": 3.30, "away": 2.90, "btts": 1.77, "over25": 1.92},
        "Sky Bet":      {"home": 2.55, "draw": 3.25, "away": 2.85, "btts": 1.83, "over25": 1.97},
        "Betfair":      {"home": 2.62, "draw": 3.45, "away": 2.75, "btts": 1.82, "over25": 1.96},
        "Paddy Power":  {"home": 2.50, "draw": 3.50, "away": 2.80, "btts": 1.80, "over25": 1.95},
    }


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
