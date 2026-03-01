// Edge Checker — main.js

// Animate probability bars on page load
document.addEventListener("DOMContentLoaded", () => {
  // Trigger bar animations after a short delay
  const bars = document.querySelectorAll(".prob-bar");
  bars.forEach((bar) => {
    const target = bar.style.width;
    bar.style.width = "0";
    setTimeout(() => {
      bar.style.width = target;
    }, 100);
  });

  // Highlight best odds column header on hover
  const oddsTable = document.querySelector(".odds-table");
  if (oddsTable) {
    oddsTable.querySelectorAll("tbody tr").forEach((row) => {
      row.addEventListener("mouseenter", () => {
        row.style.cursor = "pointer";
      });
    });
  }

  // Coming-soon bet buttons
  document.querySelectorAll(".bet-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.textContent = "Coming Soon!";
      setTimeout(() => {
        btn.textContent = "Bet Now ↗";
      }, 1500);
    });
  });
});
