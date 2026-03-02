// Edge Checker — Accumulator Manager
// Manages the bet slip in localStorage and keeps the UI in sync.
;(function (win) {
  'use strict';

  var STORE_KEY = 'ec_acca_v1';

  /* ── Storage ────────────────────────────────────── */
  function load() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || []; }
    catch (e) { return []; }
  }

  function persist(legs) {
    localStorage.setItem(STORE_KEY, JSON.stringify(legs));
    syncBadge();
    if (typeof renderAccaPage === 'function') renderAccaPage();
  }

  function legKey(fixtureId, market) {
    return String(fixtureId) + '_' + market;
  }

  /* ── Public API ─────────────────────────────────── */
  win.Acca = {
    add: function (leg) {
      // leg: { fixtureId, matchName, league, date, market, marketLabel, odds, ourPct }
      var legs  = load();
      var key   = legKey(leg.fixtureId, leg.market);
      var idx   = -1;
      for (var i = 0; i < legs.length; i++) { if (legs[i].id === key) { idx = i; break; } }

      if (idx >= 0) {
        // Update existing leg (new odds or re-added)
        legs[idx].odds   = leg.odds;
        legs[idx].ourPct = leg.ourPct;
      } else {
        var entry = { id: key, addedAt: Date.now() };
        var props = ['fixtureId','matchName','league','date','market','marketLabel','odds','ourPct'];
        for (var p = 0; p < props.length; p++) entry[props[p]] = leg[props[p]];
        legs.push(entry);
      }
      persist(legs);
      return legs.length;
    },

    remove: function (id) {
      persist(load().filter(function (l) { return l.id !== id; }));
    },

    clear: function () { persist([]); },

    count: function () { return load().length; },

    has: function (fixtureId, market) {
      var key = legKey(fixtureId, market);
      var legs = load();
      for (var i = 0; i < legs.length; i++) { if (legs[i].id === key) return true; }
      return false;
    },

    legs: load,

    stats: function () {
      var legs = load();
      if (!legs.length) return null;
      var combinedOdds = 1;
      var combinedProb = 1;
      var valueLegs    = 0;
      for (var i = 0; i < legs.length; i++) {
        combinedOdds *= legs[i].odds;
        combinedProb *= legs[i].ourPct / 100;
        if (legs[i].ourPct > (100 / legs[i].odds)) valueLegs++;
      }
      combinedOdds = Math.round(combinedOdds * 100) / 100;
      var winProb  = Math.round(combinedProb * 1000) / 10;
      var ev       = Math.round((combinedProb * combinedOdds - 1) * 1000) / 10;
      return { legs: legs, combinedOdds: combinedOdds, winProb: winProb, ev: ev, valueLegs: valueLegs };
    }
  };

  /* ── Badge sync ─────────────────────────────────── */
  function syncBadge() {
    var n   = load().length;
    var el  = document.getElementById('acca-badge');
    if (!el) return;
    el.textContent = n;
    el.style.display = n ? '' : 'none';
  }

  document.addEventListener('DOMContentLoaded', syncBadge);

}(window));
