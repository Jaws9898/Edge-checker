from flask import Blueprint, render_template, request, jsonify

from .services.football import FootballService, LEAGUES, form_stats
from .services.odds import OddsService, SPORT_KEYS, implied_probability

main = Blueprint("main", __name__)

_football = FootballService()
_odds = OddsService()


@main.route("/")
def index():
    try:
        league_id = int(request.args.get("league", 39))
    except (TypeError, ValueError):
        league_id = 39

    fixtures = _football.get_upcoming_fixtures(league_id)
    return render_template(
        "index.html",
        fixtures=fixtures,
        leagues=LEAGUES,
        selected_league=league_id,
        demo_mode=_football.demo_mode,
    )


@main.route("/match/<int:fixture_id>")
def match_detail(fixture_id):
    fixture = _football.get_fixture(fixture_id)
    if not fixture:
        return render_template("404.html"), 404

    home = fixture["teams"]["home"]
    away = fixture["teams"]["away"]
    league_id = fixture["league"]["id"]

    home_form = _football.get_team_form(home["id"], league_id)
    away_form = _football.get_team_form(away["id"], league_id)
    h2h = _football.get_h2h(home["id"], away["id"])
    standings = _football.get_standings(league_id)

    home_stats = form_stats(home_form)
    away_stats = form_stats(away_form)

    sport_key = SPORT_KEYS.get(league_id)
    odds = _odds.get_match_odds(home["name"], away["name"], sport_key)

    # Build simple verdict based on form + h2h
    verdict = _build_verdict(home["name"], away["name"], home_stats, away_stats, h2h, odds)

    return render_template(
        "match.html",
        fixture=fixture,
        home=home,
        away=away,
        home_form=home_form,
        away_form=away_form,
        home_stats=home_stats,
        away_stats=away_stats,
        h2h=h2h,
        standings=standings,
        odds=odds,
        verdict=verdict,
        leagues=LEAGUES,
        league_id=league_id,
        demo_mode=_football.demo_mode,
        implied_probability=implied_probability,
    )


def _build_verdict(home_name, away_name, hs, aws, h2h, odds) -> dict:
    """Generate a data-driven edge verdict."""
    home_score = hs["wins"] * 3 + hs["draws"]
    away_score = aws["wins"] * 3 + aws["draws"]
    h2h_total = h2h["home_wins"] + h2h["draws"] + h2h["away_wins"]

    # Add h2h weighting
    if h2h_total > 0:
        home_score += (h2h["home_wins"] / h2h_total) * 5
        away_score += (h2h["away_wins"] / h2h_total) * 5

    total = home_score + away_score
    if total == 0:
        home_pct, away_pct, draw_pct = 40, 40, 20
    else:
        home_pct = round((home_score / total) * 70)
        away_pct = round((away_score / total) * 70)
        draw_pct = 100 - home_pct - away_pct

    # Determine best bet suggestion
    if home_pct >= 50:
        tip = f"{home_name} Win"
        tip_confidence = "High" if home_pct >= 60 else "Medium"
    elif away_pct >= 50:
        tip = f"{away_name} Win"
        tip_confidence = "High" if away_pct >= 60 else "Medium"
    else:
        tip = "Draw"
        tip_confidence = "Medium"

    # BTTS assessment
    avg_gf = (hs["avg_gf"] + aws["avg_gf"]) / 2
    avg_ga = (hs["avg_ga"] + aws["avg_ga"]) / 2
    btts_likely = avg_gf >= 1.2 and avg_ga >= 0.8

    # Over 2.5 assessment
    avg_goals = hs["avg_gf"] + aws["avg_gf"]
    over25_likely = avg_goals >= 2.5

    # Value check vs implied odds probability
    best_home_odds = odds["best"]["home"] if odds else None
    value_tip = None
    if best_home_odds and home_pct > implied_probability(best_home_odds):
        value_tip = f"Potential value: {home_name} Win at {best_home_odds}"
    elif odds and away_pct > implied_probability(odds["best"]["away"] or 0):
        value_tip = f"Potential value: {away_name} Win at {odds['best']['away']}"

    return {
        "home_pct": home_pct,
        "away_pct": away_pct,
        "draw_pct": draw_pct,
        "tip": tip,
        "tip_confidence": tip_confidence,
        "btts_likely": btts_likely,
        "over25_likely": over25_likely,
        "value_tip": value_tip,
    }
