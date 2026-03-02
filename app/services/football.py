import os
import requests
from datetime import datetime, timezone
from typing import Optional


LEAGUES = {
    39:  {"name": "Premier League",  "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "country": "England"},
    140: {"name": "La Liga",          "flag": "🇪🇸", "country": "Spain"},
    78:  {"name": "Bundesliga",       "flag": "🇩🇪", "country": "Germany"},
    135: {"name": "Serie A",          "flag": "🇮🇹", "country": "Italy"},
    61:  {"name": "Ligue 1",          "flag": "🇫🇷", "country": "France"},
}

DEMO_FIXTURES = [
    # ── Premier League ──────────────────────────────────────────────────
    {
        "fixture": {"id": 1001, "date": "2026-03-08T15:00:00+00:00", "venue": {"name": "Emirates Stadium"}},
        "league": {"id": 39, "name": "Premier League", "round": "Round 29"},
        "teams": {
            "home": {"id": 42, "name": "Arsenal",         "logo": "https://media.api-sports.io/football/teams/42.png", "winner": None},
            "away": {"id": 49, "name": "Chelsea",         "logo": "https://media.api-sports.io/football/teams/49.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1002, "date": "2026-03-08T17:30:00+00:00", "venue": {"name": "Anfield"}},
        "league": {"id": 39, "name": "Premier League", "round": "Round 29"},
        "teams": {
            "home": {"id": 40, "name": "Liverpool",       "logo": "https://media.api-sports.io/football/teams/40.png", "winner": None},
            "away": {"id": 50, "name": "Manchester City", "logo": "https://media.api-sports.io/football/teams/50.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1003, "date": "2026-03-09T14:00:00+00:00", "venue": {"name": "Old Trafford"}},
        "league": {"id": 39, "name": "Premier League", "round": "Round 29"},
        "teams": {
            "home": {"id": 33, "name": "Manchester United", "logo": "https://media.api-sports.io/football/teams/33.png", "winner": None},
            "away": {"id": 47, "name": "Tottenham",          "logo": "https://media.api-sports.io/football/teams/47.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1007, "date": "2026-03-07T12:30:00+00:00", "venue": {"name": "St. James' Park"}},
        "league": {"id": 39, "name": "Premier League", "round": "Round 29"},
        "teams": {
            "home": {"id": 34, "name": "Newcastle",       "logo": "https://media.api-sports.io/football/teams/34.png", "winner": None},
            "away": {"id": 48, "name": "West Ham",        "logo": "https://media.api-sports.io/football/teams/48.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    # ── La Liga ─────────────────────────────────────────────────────────
    {
        "fixture": {"id": 1004, "date": "2026-03-07T20:00:00+00:00", "venue": {"name": "Santiago Bernabéu"}},
        "league": {"id": 140, "name": "La Liga", "round": "Round 27"},
        "teams": {
            "home": {"id": 541, "name": "Real Madrid",    "logo": "https://media.api-sports.io/football/teams/541.png", "winner": None},
            "away": {"id": 529, "name": "Barcelona",      "logo": "https://media.api-sports.io/football/teams/529.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1008, "date": "2026-03-08T19:00:00+00:00", "venue": {"name": "Metropolitano"}},
        "league": {"id": 140, "name": "La Liga", "round": "Round 27"},
        "teams": {
            "home": {"id": 530, "name": "Atletico Madrid", "logo": "https://media.api-sports.io/football/teams/530.png", "winner": None},
            "away": {"id": 532, "name": "Valencia",         "logo": "https://media.api-sports.io/football/teams/532.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    # ── Bundesliga ──────────────────────────────────────────────────────
    {
        "fixture": {"id": 1005, "date": "2026-03-07T19:30:00+00:00", "venue": {"name": "Allianz Arena"}},
        "league": {"id": 78, "name": "Bundesliga", "round": "Round 25"},
        "teams": {
            "home": {"id": 157, "name": "Bayern Munich",      "logo": "https://media.api-sports.io/football/teams/157.png", "winner": None},
            "away": {"id": 165, "name": "Borussia Dortmund",  "logo": "https://media.api-sports.io/football/teams/165.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1009, "date": "2026-03-08T17:30:00+00:00", "venue": {"name": "BayArena"}},
        "league": {"id": 78, "name": "Bundesliga", "round": "Round 25"},
        "teams": {
            "home": {"id": 168, "name": "Bayer Leverkusen", "logo": "https://media.api-sports.io/football/teams/168.png", "winner": None},
            "away": {"id": 173, "name": "RB Leipzig",        "logo": "https://media.api-sports.io/football/teams/173.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    # ── Serie A ─────────────────────────────────────────────────────────
    {
        "fixture": {"id": 1006, "date": "2026-03-08T19:45:00+00:00", "venue": {"name": "San Siro"}},
        "league": {"id": 135, "name": "Serie A", "round": "Round 27"},
        "teams": {
            "home": {"id": 489, "name": "AC Milan", "logo": "https://media.api-sports.io/football/teams/489.png", "winner": None},
            "away": {"id": 505, "name": "Inter",    "logo": "https://media.api-sports.io/football/teams/505.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1010, "date": "2026-03-09T19:45:00+00:00", "venue": {"name": "Juventus Stadium"}},
        "league": {"id": 135, "name": "Serie A", "round": "Round 27"},
        "teams": {
            "home": {"id": 496, "name": "Juventus", "logo": "https://media.api-sports.io/football/teams/496.png", "winner": None},
            "away": {"id": 492, "name": "Napoli",   "logo": "https://media.api-sports.io/football/teams/492.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    # ── Ligue 1 ─────────────────────────────────────────────────────────
    {
        "fixture": {"id": 1011, "date": "2026-03-08T20:00:00+00:00", "venue": {"name": "Parc des Princes"}},
        "league": {"id": 61, "name": "Ligue 1", "round": "Round 26"},
        "teams": {
            "home": {"id": 85, "name": "Paris Saint-Germain", "logo": "https://media.api-sports.io/football/teams/85.png", "winner": None},
            "away": {"id": 80, "name": "Lyon",                 "logo": "https://media.api-sports.io/football/teams/80.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
    {
        "fixture": {"id": 1012, "date": "2026-03-09T19:00:00+00:00", "venue": {"name": "Stade Vélodrome"}},
        "league": {"id": 61, "name": "Ligue 1", "round": "Round 26"},
        "teams": {
            "home": {"id": 81, "name": "Marseille", "logo": "https://media.api-sports.io/football/teams/81.png", "winner": None},
            "away": {"id": 79, "name": "Lille",     "logo": "https://media.api-sports.io/football/teams/79.png", "winner": None},
        },
        "goals": {"home": None, "away": None},
    },
]

DEMO_FORM = {
    # Premier League
    "Arsenal":             [("W", 3, 1), ("W", 2, 0), ("D", 1, 1), ("W", 1, 0), ("L", 0, 2)],
    "Chelsea":             [("W", 2, 1), ("L", 0, 1), ("W", 3, 0), ("D", 2, 2), ("W", 1, 0)],
    "Liverpool":           [("W", 2, 0), ("W", 3, 1), ("W", 2, 1), ("D", 1, 1), ("W", 4, 0)],
    "Manchester City":     [("W", 3, 0), ("W", 2, 1), ("L", 1, 2), ("W", 3, 1), ("D", 2, 2)],
    "Manchester United":   [("L", 0, 2), ("D", 1, 1), ("W", 2, 0), ("L", 1, 3), ("D", 0, 0)],
    "Tottenham":           [("W", 2, 1), ("W", 1, 0), ("L", 0, 2), ("W", 3, 2), ("D", 1, 1)],
    "Newcastle":           [("W", 1, 0), ("D", 2, 2), ("W", 2, 1), ("W", 3, 0), ("L", 0, 1)],
    "West Ham":            [("L", 0, 2), ("D", 1, 1), ("L", 1, 3), ("W", 2, 0), ("D", 0, 0)],
    # La Liga
    "Real Madrid":         [("W", 4, 1), ("W", 2, 0), ("W", 3, 0), ("D", 1, 1), ("W", 2, 1)],
    "Barcelona":           [("W", 3, 1), ("D", 2, 2), ("W", 2, 0), ("W", 3, 1), ("L", 0, 1)],
    "Atletico Madrid":     [("W", 1, 0), ("D", 0, 0), ("W", 2, 1), ("L", 0, 1), ("W", 1, 0)],
    "Valencia":            [("L", 0, 2), ("D", 1, 1), ("L", 1, 2), ("W", 2, 0), ("D", 0, 0)],
    # Bundesliga
    "Bayern Munich":       [("W", 3, 0), ("W", 4, 1), ("W", 2, 1), ("D", 2, 2), ("W", 3, 0)],
    "Borussia Dortmund":   [("D", 1, 1), ("W", 2, 1), ("L", 0, 1), ("W", 3, 0), ("W", 2, 0)],
    "Bayer Leverkusen":    [("W", 2, 1), ("W", 3, 0), ("D", 1, 1), ("W", 2, 0), ("L", 0, 1)],
    "RB Leipzig":          [("W", 2, 1), ("L", 1, 2), ("W", 3, 1), ("D", 0, 0), ("W", 2, 0)],
    # Serie A
    "AC Milan":            [("W", 2, 1), ("D", 0, 0), ("W", 1, 0), ("L", 1, 2), ("W", 3, 1)],
    "Inter":               [("W", 3, 0), ("W", 2, 1), ("D", 1, 1), ("W", 2, 0), ("W", 3, 1)],
    "Juventus":            [("W", 1, 0), ("D", 1, 1), ("W", 2, 0), ("L", 0, 1), ("W", 2, 1)],
    "Napoli":              [("W", 3, 1), ("W", 2, 0), ("D", 1, 1), ("L", 0, 2), ("W", 1, 0)],
    # Ligue 1
    "Paris Saint-Germain": [("W", 4, 0), ("W", 3, 1), ("W", 2, 0), ("W", 5, 1), ("W", 2, 0)],
    "Lyon":                [("D", 1, 1), ("W", 2, 0), ("L", 0, 2), ("D", 0, 0), ("W", 1, 0)],
    "Marseille":           [("W", 2, 1), ("D", 1, 1), ("W", 3, 0), ("L", 1, 2), ("W", 2, 0)],
    "Lille":               [("W", 1, 0), ("W", 2, 1), ("D", 0, 0), ("L", 0, 1), ("W", 2, 0)],
}

DEMO_H2H = {
    (42, 49):   {"home_wins": 4, "draws": 3, "away_wins": 3, "recent": [("W", 2, 1), ("D", 1, 1), ("L", 0, 2), ("W", 3, 0), ("D", 2, 2)]},
    (40, 50):   {"home_wins": 3, "draws": 2, "away_wins": 5, "recent": [("L", 1, 2), ("W", 3, 1), ("L", 0, 1), ("W", 2, 0), ("L", 1, 3)]},
    (33, 47):   {"home_wins": 6, "draws": 2, "away_wins": 2, "recent": [("W", 2, 0), ("W", 1, 0), ("D", 1, 1), ("W", 3, 1), ("L", 0, 2)]},
    (34, 48):   {"home_wins": 5, "draws": 2, "away_wins": 3, "recent": [("W", 2, 0), ("D", 1, 1), ("W", 3, 1), ("L", 0, 2), ("W", 1, 0)]},
    (541, 529): {"home_wins": 5, "draws": 2, "away_wins": 3, "recent": [("W", 3, 1), ("L", 0, 2), ("W", 2, 1), ("D", 2, 2), ("W", 1, 0)]},
    (530, 532): {"home_wins": 6, "draws": 2, "away_wins": 2, "recent": [("W", 1, 0), ("D", 0, 0), ("W", 2, 1), ("W", 1, 0), ("L", 0, 1)]},
    (157, 165): {"home_wins": 7, "draws": 1, "away_wins": 2, "recent": [("W", 3, 0), ("W", 2, 1), ("L", 1, 2), ("W", 4, 0), ("W", 2, 0)]},
    (168, 173): {"home_wins": 4, "draws": 3, "away_wins": 3, "recent": [("W", 2, 1), ("D", 1, 1), ("L", 0, 1), ("W", 3, 2), ("D", 0, 0)]},
    (489, 505): {"home_wins": 3, "draws": 4, "away_wins": 3, "recent": [("D", 1, 1), ("L", 0, 1), ("W", 2, 0), ("D", 2, 2), ("W", 1, 0)]},
    (496, 492): {"home_wins": 4, "draws": 3, "away_wins": 3, "recent": [("W", 1, 0), ("D", 1, 1), ("L", 0, 2), ("W", 2, 1), ("D", 0, 0)]},
    (85, 80):   {"home_wins": 8, "draws": 1, "away_wins": 1, "recent": [("W", 3, 0), ("W", 4, 1), ("W", 2, 0), ("D", 1, 1), ("W", 5, 0)]},
    (81, 79):   {"home_wins": 4, "draws": 3, "away_wins": 3, "recent": [("W", 2, 1), ("D", 1, 1), ("L", 0, 1), ("W", 2, 0), ("D", 0, 0)]},
}


class FootballService:
    BASE_URL = "https://v3.football.api-sports.io"
    LEAGUES = LEAGUES
    SEASON = 2025  # 2025/26 season

    def __init__(self):
        self.api_key = os.environ.get("API_FOOTBALL_KEY")
        self._cache: dict = {}

    @property
    def demo_mode(self) -> bool:
        return not self.api_key

    def _get(self, endpoint: str, params: dict) -> Optional[dict]:
        if self.demo_mode:
            return None
        cache_key = f"{endpoint}:{tuple(sorted(params.items()))}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            resp = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                headers={"x-apisports-key": self.api_key},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            self._cache[cache_key] = data
            return data
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def get_upcoming_fixtures(self, league_id: int, count: int = 10) -> list:
        if self.demo_mode:
            return [f for f in DEMO_FIXTURES if f["league"]["id"] == league_id] or DEMO_FIXTURES[:6]
        data = self._get("fixtures", {"league": league_id, "season": self.SEASON, "next": count})
        return data.get("response", []) if data else []

    def get_fixture(self, fixture_id: int) -> Optional[dict]:
        if self.demo_mode:
            for f in DEMO_FIXTURES:
                if f["fixture"]["id"] == fixture_id:
                    return f
            return None
        data = self._get("fixtures", {"id": fixture_id})
        resp = data.get("response", []) if data else []
        return resp[0] if resp else None

    def get_team_form(self, team_id: int, league_id: int) -> list:
        """Returns list of (result, goals_for, goals_against) tuples, newest first."""
        if self.demo_mode:
            # Find a fixture with this team ID and return demo form
            for f in DEMO_FIXTURES:
                for side in ("home", "away"):
                    if f["teams"][side]["id"] == team_id:
                        name = f["teams"][side]["name"]
                        return DEMO_FORM.get(name, [("D", 1, 1)] * 5)
            return [("D", 1, 1)] * 5

        data = self._get("fixtures", {
            "team": team_id, "league": league_id,
            "season": self.SEASON, "last": 5, "status": "FT",
        })
        if not data:
            return []
        results = []
        for match in data.get("response", []):
            home_id = match["teams"]["home"]["id"]
            is_home = home_id == team_id
            gf = match["goals"]["home"] if is_home else match["goals"]["away"]
            ga = match["goals"]["away"] if is_home else match["goals"]["home"]
            home_win = match["teams"]["home"].get("winner")
            if home_win is None:
                r = "D"
            elif (is_home and home_win) or (not is_home and not home_win):
                r = "W"
            else:
                r = "L"
            results.append((r, gf or 0, ga or 0))
        return results

    def get_h2h(self, home_id: int, away_id: int) -> dict:
        if self.demo_mode:
            key = (home_id, away_id)
            rev = (away_id, home_id)
            if key in DEMO_H2H:
                return DEMO_H2H[key]
            if rev in DEMO_H2H:
                d = DEMO_H2H[rev]
                return {
                    "home_wins": d["away_wins"],
                    "draws": d["draws"],
                    "away_wins": d["home_wins"],
                    "recent": [(_flip(r), ga, gf) for r, gf, ga in d["recent"]],
                }
            return {"home_wins": 4, "draws": 3, "away_wins": 3, "recent": []}

        data = self._get("fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": 10})
        if not data:
            return {"home_wins": 0, "draws": 0, "away_wins": 0, "recent": []}
        home_w = draws = away_w = 0
        recent = []
        for match in data.get("response", []):
            hw = match["teams"]["home"].get("winner")
            gf = match["goals"]["home"] or 0
            ga = match["goals"]["away"] or 0
            mid = match["teams"]["home"]["id"]
            if hw is None:
                draws += 1
                r = "D"
            elif hw:
                if mid == home_id:
                    home_w += 1
                    r = "W"
                else:
                    away_w += 1
                    r = "L"
            else:
                if mid == home_id:
                    away_w += 1
                    r = "L"
                else:
                    home_w += 1
                    r = "W"
            recent.append((r, gf, ga))
        return {"home_wins": home_w, "draws": draws, "away_wins": away_w, "recent": recent[:5]}

    def get_standings(self, league_id: int) -> list:
        if self.demo_mode:
            return []
        data = self._get("standings", {"league": league_id, "season": self.SEASON})
        if not data:
            return []
        try:
            return data["response"][0]["league"]["standings"][0]
        except (KeyError, IndexError):
            return []


def _flip(r: str) -> str:
    return {"W": "L", "L": "W", "D": "D"}[r]


def form_stats(form: list) -> dict:
    """Summarise a form list into useful stats."""
    if not form:
        return {"wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0, "btts": 0}
    wins = sum(1 for r, _, __ in form if r == "W")
    draws = sum(1 for r, _, __ in form if r == "D")
    losses = sum(1 for r, _, __ in form if r == "L")
    gf = sum(g for _, g, __ in form)
    ga = sum(g for _, __, g in form)
    btts = sum(1 for _, gf_, ga_ in form if gf_ > 0 and ga_ > 0)
    return {
        "wins": wins, "draws": draws, "losses": losses,
        "gf": gf, "ga": ga, "btts": btts,
        "avg_gf": round(gf / len(form), 1),
        "avg_ga": round(ga / len(form), 1),
    }
