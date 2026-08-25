# Specwise · PC Consulting

Premium workstation consulting — workload analysis, component recommendation, performance explorer & configurator.

**Live demo:** https://YOUR_USERNAME.github.io/specwise-workstation/ *(after enabling Pages)*

## Quick start (local)

No build step. Just serve over HTTP (required for \am-prices.json\ fetch):

\\\ash
# any static server
npx serve deploy
# or
python -m http.server --directory deploy 8000
\\\

Open http://localhost:3000 or http://localhost:8000

## Deploy to GitHub Pages (drag-and-drop, no CLI)

1. Create a new public repo on https://github.com/new — e.g. \specwise-workstation\
2. Click **Add file → Upload files** → drag **all files from the \deploy/\ folder** in this zip (\index.html\ + \am-prices.json\) to the repo root
3. Commit, then go to **Settings → Pages** → **Source: Deploy from branch** → **Branch: main / (root)** → Save
4. Wait 1–2 min → your site is live at \https://<you>.github.io/specwise-workstation/\

### Via git

\\\ash
git init
git add index.html ram-prices.json
git commit -m "ship specwise"
git branch -M main
git remote add origin https://github.com/<you>/specwise-workstation.git
git push -u origin main
# then enable Pages as above
\\\

## What is inside

- \index.html\ — full site, self-contained (347 KB, no external build, Apple design system)
- \am-prices.json\ — live CAD price floors (DDR4/DDR5 kits + SSD tiers, refreshed May 13 2026 check). Fetched client-side; falls back to built-in prices if offline.
- \PC-Consultant-Database.xlsx\ — source component database (reference, not required at runtime)
- \.nojekyll\ — disables Jekyll processing so Pages serves correctly

## Notes

- Prices are CAD floors across Amazon.ca / Newegg.ca / Canada Computers / Memory Express — NAND/DDR5 tightness priced in.
- Report: Step 03 → Generate report → Print → Save as PDF
- Contact form uses FormSubmit to \iamjz23130302@gmail.com\ — activate once via inbox email.

Built with the Apple-inspired editorial design system. No tracker, no framework.
