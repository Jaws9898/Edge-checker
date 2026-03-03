"""
Acca Engine — core accumulator analysis logic.

Given a list of acca legs and per-fixture bookmaker odds, this module:
  1. Enriches each leg with per-bookmaker prices for its specific market
  2. Calculates combined odds per bookmaker across all legs
  3. Ranks bookmakers — best full-coverage price first
  4. Detects correlated legs and emits warnings
"""

from functools import reduce
from typing import List, Dict, Optional


# Market pairs that are statistically correlated when from the same fixture
_CORRELATED_PAIRS = [
    ("btts",   "over25",  "high",   "BTTS and Over 2.5 are strongly correlated — both need goals. Consider keeping just one."),
    ("home",   "over25",  "medium", "Home win and Over 2.5 can conflict — a comfortable home win often has fewer goals."),
    ("away",   "over25",  "medium", "Away win and Over 2.5 can conflict — a comfortable away win often has fewer goals."),
    ("home",   "btts",    "medium", "Home win and BTTS require the away team to score, which reduces the home win probability."),
    ("away",   "btts",    "medium", "Away win and BTTS require the home team to score, which reduces the away win probability."),
]

# Severity label mapping
_SEVERITY_LABEL = {
    "high":   "High correlation",
    "medium": "Moderate correlation",
    "low":    "Same-game multi",
}


def analyse_acca(legs: List[Dict], odds_by_fixture: Dict) -> Dict:
    """
    Core acca analysis.

    Args:
        legs: List of leg dicts — keys: fixtureId, market, marketLabel,
              odds, ourPct, matchName, league, date
        odds_by_fixture: Dict mapping fixtureId (int) ->
              { bookmaker_name: { market: price, ... }, ... }

    Returns dict with:
        legs_enriched       — legs with added bookmaker_prices per leg
        bookmaker_comparison — ranked list of bookmakers with combined odds
        best_bookmaker      — top bookmaker with full coverage (or best available)
        correlations        — list of correlation warning dicts
        summary             — headline numbers
    """
    if not legs:
        return _empty_result()

    # ── 1. Enrich legs with per-bookmaker prices ──────────────────────────
    legs_enriched = []
    for leg in legs:
        fid    = leg["fixtureId"]
        market = leg["market"]
        bk_map = odds_by_fixture.get(fid, {})

        bookmaker_prices = {}
        for bk_name, markets in bk_map.items():
            price = markets.get(market)
            if price and price > 1.0:
                bookmaker_prices[bk_name] = round(float(price), 2)

        legs_enriched.append({**leg, "bookmaker_prices": bookmaker_prices})

    # ── 2. Build per-bookmaker combined odds ──────────────────────────────
    all_bookmakers = set()
    for leg in legs_enriched:
        all_bookmakers.update(leg["bookmaker_prices"].keys())

    bookmaker_comparison = []
    for bk in sorted(all_bookmakers):
        prices      = []
        missing     = []
        leg_details = []

        for leg in legs_enriched:
            price = leg["bookmaker_prices"].get(bk)
            if price:
                prices.append(price)
                leg_details.append({"label": leg["marketLabel"], "odds": price})
            else:
                missing.append(leg["marketLabel"])

        if not prices:
            continue

        combined = round(reduce(lambda a, b: a * b, prices), 2)
        bookmaker_comparison.append({
            "bookmaker":     bk,
            "combined_odds": combined,
            "legs_priced":   len(prices),
            "legs_total":    len(legs_enriched),
            "missing":       missing,
            "leg_details":   leg_details,
            "full_coverage": len(missing) == 0,
        })

    # Sort: full coverage first, then by combined odds descending
    bookmaker_comparison.sort(
        key=lambda x: (not x["full_coverage"], -x["combined_odds"])
    )

    # ── 3. Best bookmaker ─────────────────────────────────────────────────
    full_coverage = [b for b in bookmaker_comparison if b["full_coverage"]]
    best = full_coverage[0] if full_coverage else (bookmaker_comparison[0] if bookmaker_comparison else None)

    # ── 4. Correlation detection ──────────────────────────────────────────
    correlations = _detect_correlations(legs_enriched)

    # ── 5. Summary ────────────────────────────────────────────────────────
    best_combined = best["combined_odds"] if best else None
    worst_combined = bookmaker_comparison[-1]["combined_odds"] if bookmaker_comparison else None
    price_spread = round(best_combined - worst_combined, 2) if best_combined and worst_combined else None

    return {
        "legs_enriched":       legs_enriched,
        "bookmaker_comparison": bookmaker_comparison,
        "best_bookmaker":      best,
        "correlations":        correlations,
        "summary": {
            "best_combined_odds":  best_combined,
            "worst_combined_odds": worst_combined,
            "price_spread":        price_spread,
            "bookmakers_checked":  len(bookmaker_comparison),
            "full_coverage_count": len(full_coverage),
            "correlation_count":   len(correlations),
        },
    }


def _detect_correlations(legs: List[Dict]) -> List[Dict]:
    """Detect correlated legs and return warning objects."""
    correlations = []

    # Group legs by fixture
    by_fixture: Dict[int, List[Dict]] = {}
    for leg in legs:
        fid = leg["fixtureId"]
        by_fixture.setdefault(fid, []).append(leg)

    for fid, flegs in by_fixture.items():
        if len(flegs) < 2:
            continue

        markets    = [l["market"] for l in flegs]
        match_name = flegs[0]["matchName"]
        flagged    = set()

        # Check specific correlated pairs
        for m1, m2, severity, message in _CORRELATED_PAIRS:
            if m1 in markets and m2 in markets:
                flagged.update([m1, m2])
                correlations.append({
                    "type":      "correlated",
                    "severity":  severity,
                    "label":     _SEVERITY_LABEL[severity],
                    "matchName": match_name,
                    "markets":   [m1, m2],
                    "message":   message,
                })

        # General SGM warning for any remaining same-game legs
        remaining = [m for m in markets if m not in flagged]
        if len(remaining) >= 2:
            correlations.append({
                "type":      "sgm",
                "severity":  "low",
                "label":     _SEVERITY_LABEL["low"],
                "matchName": match_name,
                "markets":   remaining,
                "message":   (
                    f"Multiple legs from {match_name}. Same-game multis "
                    "are correlated — the combined probability is lower than the product suggests."
                ),
            })

    return correlations


def _empty_result() -> Dict:
    return {
        "legs_enriched":        [],
        "bookmaker_comparison": [],
        "best_bookmaker":       None,
        "correlations":         [],
        "summary": {
            "best_combined_odds":  None,
            "worst_combined_odds": None,
            "price_spread":        None,
            "bookmakers_checked":  0,
            "full_coverage_count": 0,
            "correlation_count":   0,
        },
    }
