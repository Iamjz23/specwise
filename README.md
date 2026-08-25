# Specwise — PC Consulting

Premium workstation consulting — workload analysis, component recommendation, performance explorer & configurator.

**Live demo:** `https://YOUR_USERNAME.github.io/specwise-workstation/` *(after enabling Pages)*

## Quick start (local)

No build step. Just serve over HTTP (required for `ram-prices.json` fetch):

```bash
# any static server
npx serve deploy
# or
python -m http.server --directory deploy 8000
```

Open http://localhost:3000 or http://localhost:8000

## Deploy to GitHub Pages (drag-and-drop, no CLI)

1. Create a new public repo on https://github.com/new — e.g. `specwise-workstation`
2. Click **Add file → Upload files** → drag **all files from the `deploy/` folder** in this zip (`index.html` + `ram-prices.json`) to the repo root
3. Commit, then go to **Settings → Pages** → **Source: Deploy from branch** → **Branch: main / (root)** → Save
4. Wait 1-2 min → your site is live at `https://<you>.github.io/specwise-workstation/`

### Via git

```bash
git init
git add index.html ram-prices.json .nojekyll
git commit -m "ship specwise — budget-aware build"
git branch -M main
git remote add origin https://github.com/<you>/specwise-workstation.git
git push -u origin main
# then enable Pages as above
```

## What is inside

- `index.html` — full site, self-contained (~355 KB, no external build, Apple design system)
- `ram-prices.json` — live CAD price floors (DDR4/DDR5 kits + SSD tiers, refreshed May 13 2026). Fetched client-side; falls back to built-in prices if offline.
- `PC-Consultant-Database.xlsx` — source component database (112 GPUs + 112 CPUs, reference, not required at runtime)
- `.nojekyll` — disables Jekyll processing so Pages serves correctly

## Engine — Aug 25 2026 update

- **Street pricing (Aug 21 2026 tracker):** `RTX 5090 $5299 / 5080 $2100 / 5070 Ti $1249 / 5070 $849` CAD — GPUprix + Best Buy / Canada Computers lows (GDDR7 shortage +46% vs MSRP). NAND/DDR5 tightness priced in.
- **Budget-aware picker:** GPUs/CPUs ranked by real `TimeSpy / CB23 / FPS` per dollar, then tested against *total* build cost (`GPU+CPU+RAM+storage+platform`) vs `budgetMax + tiered headroom` ($1000→+40, $1500→+60, $2000→+80, $3000→+110) — fixes low-end “wayyy over” and high-end random picks. $3000+ now surfaces `R7 9800X3D / R7 9700X / Ultra 7 265K` and `RTX 5080` correctly; $1000-1500 surfaces `B580 / RTX 4060 + R5 5600/7600` on perf-per-dollar.
- **Modern pref:** Blackwell/RDNA 4 and Zen 5/Arrow Lake boosted at $2000+; older Pascal/Vega/Turing i9-era flagships penalized when a 2024 R5 beats them on `CB23`/`FPS` per dollar.

## Notes

- Prices are CAD floors across Amazon.ca / Newegg.ca / Canada Computers / Memory Express — NAND/DDR5 tightness priced in. Live market refreshed in `ram-prices.json`.
- Report: Step 03 → Generate report → Print → Save as PDF
- Contact form uses FormSubmit — activate once via inbox email.

Built with the Apple-inspired editorial design system. No tracker, no framework.
