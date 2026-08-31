# SpecWise Market Price System — Implementation Summary

## Overview

The SpecWise Market tab now uses a **semi-automated category-level price discovery system** that updates **weekly** (every Sunday at 06:00 UTC).

---

## How It Works

### Architecture

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  GitHub Actions     │────▶│  collect_prices.py   │────▶│ market-products │
│  (Weekly Cron)      │     │  - Newegg collector  │     │ .json           │
└─────────────────────┘     │  - HomeGadgets API   │     └────────┬────────┘
                            │  - Manual entries    │              │
                            └──────────────────────┘              ▼
                                                          ┌─────────────────┐
                                                          │  compute winners │
                                                          │  for each       │
                                                          │  category       │
                                                          └────────┬────────┘
                                                                   │
                                                                   ▼
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Cloudflare Pages   │◀────│  ram-prices.json     │◀────│  generate JSON  │
│  Auto-deploy        │     │  (frontend data)     │     │  output         │
└─────────────────────┘     └──────────────────────┘     └─────────────────┘
```

### Key Principles

1. **Category-Level Discovery**: For each category (e.g., "DDR5 32GB"), the system discovers multiple competing products and selects the cheapest valid offer.

2. **Semi-Automated**: 
   - Newegg.ca: Automated collection (when accessible)
   - Other retailers: Manual entry via tool

3. **Transparent Data States**:
   - `source: "newegg-direct"` — Automatically collected
   - `source: "manual"` — Manually verified and entered
   - `source: "seed"` — Initial fallback data

4. **No Simulated Fluctuations**: Prices only change when actual data is collected, not every 5 seconds.

---

## Files Created/Modified

| File | Status | Purpose |
|------|--------|---------|
| `scripts/collect_prices.py` | Enhanced | Main price collector with BeautifulSoup HTML parsing |
| `scripts/manual_entry.py` | NEW | Interactive tool for manual price entry |
| `market-products.json` | NEW | Persistent database of all product offers |
| `ram-prices.json` | Modified | Frontend data with computed winners |
| `index.html` | Modified | Disabled simulated fluctuations, weekly refresh |
| `.github/workflows/update-market-prices.yml` | Modified | Weekly cron (Sunday 06:00 UTC) |

---

## How to Add Manual Offers

### Option 1: Interactive Mode

```bash
cd /workspace
python scripts/manual_entry.py
```

The tool will guide you through:
1. Selecting product type (RAM/SSD)
2. Selecting capacity and generation
3. Selecting retailer
4. Entering product name, price, URL
5. Validating category match
6. Saving and recalculating winners

### Option 2: Batch Mode

Create a JSON file with multiple offers:

```json
{
  "offers": [
    {
      "category": "ram-ddr5-32",
      "productName": "TeamGroup T-Force Vulcan 32GB (2x16GB) DDR5-6000",
      "retailer": "Canada Computers",
      "price": 89.99,
      "url": "https://www.canadacomputers.com/..."
    }
  ]
}
```

Then run:
```bash
python scripts/manual_entry.py --batch offers.json
```

### After Adding Offers

Commit and push to trigger Cloudflare deployment:
```bash
git add market-products.json ram-prices.json
git commit -m "Update market prices"
git push
```

---

## Automated Collection (Newegg)

The `collect_prices.py` script attempts to:
1. Search Newegg.ca for each RAM/SSD category
2. Parse product listings using BeautifulSoup
3. Extract: product name, price, URL
4. Validate: capacity, generation, desktop-only
5. Reject: SO-DIMM, laptop memory, invalid capacities

**When Newegg blocks requests** (403/429/timeout):
- Script logs the failure
- Existing data is preserved
- No empty results overwrite valid data
- Other retailers' data remains usable

---

## Category Winners Calculation

For each of the 15 categories:

1. **DDR4 RAM**: 16GB, 32GB, 64GB, 128GB
2. **DDR5 RAM**: 16GB, 32GB, 48GB, 64GB, 96GB, 128GB
3. **SSD**: 512GB, 1TB, 2TB, 4TB, 8TB

The system:
1. Gathers all offers in the category
2. Filters out stale offers (>7 days old, configurable)
3. Filters out unavailable products
4. Sorts by CAD price
5. Selects cheapest valid offer as winner
6. Stores up to 3 alternatives for fallback

---

## What "Last Verified" Means

Every displayed price shows when it was last confirmed:

- **Direct source**: Date/time when automated collector retrieved it
- **Manual source**: Date/time when you entered it
- **Seed data**: Original timestamp from initial dataset

The UI displays: `Last verified [date]`

This is **honest labeling** — not claiming "live" prices unless actually retrieved recently.

---

## GitHub Actions Workflow

### Schedule
- **When**: Every Sunday at 06:00 UTC (Saturday night PST/PDT)
- **Trigger**: Automatic cron + manual `workflow_dispatch`

### Steps
1. Checkout repository
2. Set up Python 3.12
3. Run `collect_prices.py`
4. Detect changes in JSON files
5. Commit and push if changed
6. Generate workflow summary

### Manual Trigger
1. Go to GitHub → Actions → "Update Market Prices"
2. Click "Run workflow"
3. Optionally select "Force refresh"
4. Wait for completion (~2-5 minutes)

---

## Retailer Coverage

| Retailer | Method | Status |
|----------|--------|--------|
| Amazon.ca | Manual | Requires manual entry |
| Canada Computers | Manual | Requires manual entry |
| Memory Express | Manual | Requires manual entry |
| Newegg Canada | Automated | Works when not blocked |
| PC-Canada | Manual | Requires manual entry |

**Note**: Direct scraping of most Canadian retailers is blocked by anti-bot measures. The system gracefully handles this by preserving existing data and allowing manual updates.

---

## Data Freshness

- **FRESHNESS_DAYS**: 7 (configurable in `collect_prices.py`)
- Offers older than 7 days are marked stale
- Stale offers are excluded from winner calculation
- Stale offers are NOT deleted (preserved for history)

---

## Accuracy Expectations

- **Within 3% of actual**: Achievable with weekly manual updates
- **Automated only**: May drift if Newegg is frequently blocked
- **Best practice**: Manual update high-volume categories weekly

---

## Future Extension Points

The architecture supports adding new sources without changing UI:

1. **Official retailer APIs** (if available)
2. **Affiliate feeds**
3. **Product data feeds**
4. **Additional price comparison services**

New sources simply add offers to `market-products.json` — the price engine handles the rest.

---

## Testing Locally

```bash
# Test collector
python scripts/collect_prices.py

# Test manual entry (interactive)
python scripts/manual_entry.py

# Test batch mode
python scripts/manual_entry.py --batch test-offers.json

# Verify JSON validity
python -c "import json; json.load(open('ram-prices.json'))"
python -c "import json; json.load(open('market-products.json'))"
```

---

## Troubleshooting

### Newegg Collection Fails
- Check workflow logs for HTTP status codes
- 403/429 = rate limiting (expected, data preserved)
- Timeout = network issue (retry next week)

### Manual Entry Validation Fails
- Ensure product name contains capacity (e.g., "32GB")
- Desktop memory only (no SO-DIMM/laptop)
- Price must be numeric CAD

### Website Shows Old Prices
- Check Cloudflare deployment completed
- Hard refresh browser (Ctrl+Shift+R)
- Verify `ram-prices.json` updated in repo

---

## Cost

- **GitHub Actions**: Free tier (2000 minutes/month) — sufficient for weekly runs
- **HomeGadgets API**: Free tier (10 requests/day)
- **Hosting**: $0 (existing Cloudflare Pages)
- **Total**: $0/month

---

## Summary

✅ **Automated where possible** (Newegg)  
✅ **Manual where blocked** (other retailers)  
✅ **Category-level discovery** (not predefined SKUs)  
✅ **Transparent data freshness** ("Last verified" timestamps)  
✅ **No 24/7 server required**  
✅ **No paid infrastructure**  
✅ **Weekly updates** (Sunday 06:00 UTC)  
✅ **Graceful failure handling** (preserves working data)  
✅ **Extensible architecture** (add sources easily)  
