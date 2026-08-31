# SpecWise Market - Implementation Report

## Overview

This implementation adds a complete price collection and comparison system for Canadian RAM and SSD products. The system supports both automated data collection (Newegg) and manual entry for other retailers, with automatic category winner calculation.

---

## 1. How to Add Manual Offers

### Interactive Mode

Run the manual entry tool:

```bash
cd /workspace
python scripts/manual_entry.py
```

The tool will guide you through:
1. Selecting product type (RAM DDR4/DDR5 or SSD)
2. Selecting capacity
3. Selecting retailer (Amazon.ca, Canada Computers, Memory Express, Newegg Canada, PC-Canada)
4. Entering product name, brand, price, and URL

After entering offers, the tool automatically:
- Adds them to `market-products.json`
- Recalculates category winners
- Regenerates `ram-prices.json`

### Batch Mode

Create a JSON file with multiple offers:

```json
{
  "offers": [
    {
      "category": "ram-ddr5-32",
      "productName": "Corsair Vengeance 32GB (2x16GB) DDR5-6000",
      "brand": "Corsair",
      "retailer": "Amazon.ca",
      "price": 115.99,
      "url": "https://www.amazon.ca/dp/EXAMPLE"
    },
    {
      "category": "ssd-1000",
      "productName": "Samsung 980 Pro 1TB NVMe SSD",
      "brand": "Samsung",
      "retailer": "Canada Computers",
      "price": 129.99,
      "url": "https://www.canadacomputers.com/product_info.php?item_id=EXAMPLE"
    }
  ]
}
```

Then run:

```bash
python scripts/manual_entry.py --batch my-offers.json
```

---

## 2. Running the Local Manual Tool

```bash
# Navigate to project directory
cd /workspace

# Run interactive mode
python scripts/manual_entry.py

# Or batch mode
python scripts/manual_entry.py --batch input.json
```

No additional setup required - it imports functions from `collect_prices.py`.

---

## 3. Do You Need to Edit JSON Directly?

**No.** The manual entry tool handles all JSON updates automatically. However, you CAN edit `market-products.json` directly if needed - just ensure:

- Each offer has: `id`, `category`, `productName`, `retailer`, `price`, `currency`, `url`, `source`, `verifiedAt`
- After manual edits, run: `python scripts/collect_prices.py` to regenerate winners

---

## 4. How Automated Newegg Discovery Works

The Newegg collector (`scripts/collect_prices.py`):

1. **Searches predefined categories**: DDR4/DDR5 RAM at various capacities (16GB, 32GB, 48GB, etc.) and SSDs (512GB, 1TB, 2TB, 4TB, 8TB)

2. **Parses HTML with BeautifulSoup**: Extracts product name, price, and URL from search results

3. **Validates products**: 
   - RAM: Checks capacity matches search, verifies DDR generation, rejects laptop memory
   - SSD: Extracts capacity, validates against standard sizes

4. **Classifies into categories**: e.g., `ram-ddr5-32`, `ssd-1000`

5. **Adds to product pool**: Each discovered offer is added to `market-products.json`

6. **Graceful failure**: If Newegg blocks requests (403/429/503), collection stops but existing data is preserved

---

## 5. What Happens When Newegg is Blocked

When Newegg returns HTTP 403, 429, or 503:

1. Collection logs the error: `[Newegg] Blocked or rate-limited (403) - stopping collection`
2. Existing `market-products.json` data is NOT overwritten
3. Previously collected offers remain valid
4. Category winners are recalculated using available data
5. `ram-prices.json` is regenerated with existing valid offers

**Result**: Your website continues showing the last-known-good prices until Newegg becomes accessible again.

---

## 6. How the Cheapest Category Winner is Calculated

The price engine (`compute_category_winners()` in `collect_prices.py`):

1. **Groups all offers by category**: e.g., all `ram-ddr5-32` offers together

2. **Filters by freshness**: By default, only considers offers verified within `FRESHNESS_DAYS` (7 days configurable)

3. **Sorts by price**: Lowest price first

4. **Selects winner**: The cheapest fresh offer becomes the category winner

5. **Stores alternatives**: Top 3 offers are kept for reference

Example output in `ram-prices.json`:

```json
"ram-ddr5-32": {
  "price": 109,
  "retailer": "Newegg Canada",
  "productName": "TeamGroup T-Force Vulcan 32GB (2x16GB) DDR5-6000",
  "url": "https://www.newegg.ca/...",
  "source": "newegg-direct",
  "verifiedAt": "2026-08-31T00:27:37Z",
  "alternatives": [
    {"price": 115, "retailer": "Amazon.ca", "productName": "..."},
    {"price": 119, "retailer": "Canada Computers", "productName": "..."}
  ]
}
```

---

## 7. What "Last Verified" Means

The UI displays "Last verified [date]" which comes from:

- **DIRECT sources** (`newegg-direct`, `homegadgets`): Timestamp when the automated collector retrieved the price
- **MANUAL sources**: Timestamp when you entered the offer via the manual tool
- **SEED sources**: Original timestamp from initial data (May 2026)

**Freshness threshold**: Prices older than `FRESHNESS_DAYS` (default: 7) are marked as stale but still displayed if no fresher alternative exists.

---

## 8. Files Created or Modified

### New Files

| File | Purpose |
|------|---------|
| `scripts/collect_prices.py` | Main price collector (Newegg + HomeGadgets API) |
| `scripts/manual_entry.py` | Interactive manual entry tool |
| `market-products.json` | Source-of-truth product database |

### Modified Files

| File | Changes |
|------|---------|
| `index.html` | Updated Market tab to display real data with source attribution and verification dates |
| `ram-prices.json` | Now generated automatically with `_winners` containing full offer details |

### Unchanged

| File | Notes |
|------|-------|
| `.github/workflows/update-market-prices.yml` | Existing daily workflow still works |

---

## 9. How the Daily GitHub Action Works

The workflow (`.github/workflows/update-market-prices.yml`) runs daily at 06:00 UTC:

1. **Checkout repository**
2. **Set up Python 3.12**
3. **Run price collector**: `python scripts/collect_prices.py`
   - Attempts Newegg collection
   - Queries HomeGadgets API (up to 10 requests/day)
   - Merges with existing offers
   - Computes category winners
   - Generates `ram-prices.json`
4. **Detects changes**: Compares new `ram-prices.json` with existing
5. **Commits if changed**: Only commits if data actually changed
6. **Pushes to repository**

Manual trigger available via GitHub Actions UI with optional "force_refresh" parameter.

---

## 10. How to Manually Trigger a Price Update

### Option A: GitHub Actions UI

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Update Market Prices" workflow
4. Click "Run workflow" dropdown
5. Optionally check "Force refresh even if no changes detected"
6. Click "Run workflow"

### Option B: Local Execution

```bash
cd /workspace
python scripts/collect_prices.py

# Then commit and push
git add market-products.json ram-prices.json
git commit -m "Update market prices $(date -u '+%Y-%m-%d %H:%M UTC')"
git push
```

---

## Architecture Summary

```
┌─────────────────────┐     ┌─────────────────────┐
│  Newegg Collector   │     │   Manual Entry      │
│  (automated)        │     │   (interactive)     │
└─────────┬───────────┘     └─────────┬───────────┘
          │                           │
          ▼                           ▼
┌─────────────────────────────────────────────┐
│         market-products.json                │
│  (all discovered + manually entered offers) │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  Price Engine   │
            │  (winner calc)  │
            └────────┬────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│           ram-prices.json                   │
│  (category winners for frontend display)    │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │   index.html    │
            │  (Market tab)   │
            └─────────────────┘
```

---

## Adding New Data Sources in the Future

To add a new retailer/source without changing the UI:

1. **Add collection logic** in `scripts/collect_prices.py`:
   ```python
   def collect_retailer_x_products() -> List[Dict]:
       # Fetch and parse data
       return [{
           "id": generate_product_id(...),
           "category": "ram-ddr5-32",
           "productName": "...",
           "retailer": "Retailer X",
           "price": 99.99,
           "currency": "CAD",
           "url": "...",
           "source": "retailer-x",
           "verifiedAt": datetime.now(timezone.utc).isoformat()
       }]
   ```

2. **Add to main() function**:
   ```python
   new_offers = collect_retailer_x_products()
   all_products.extend(new_offers)
   ```

3. **That's it!** The price engine automatically includes new offers in winner calculation, and the UI displays them without modification.

---

## Key Design Principles

1. **Source-independent price engine**: Collectors just add offers; the engine picks winners
2. **Graceful degradation**: Failed collectors don't break existing data
3. **Category-level competition**: Any qualifying product can win, regardless of brand
4. **Transparent data attribution**: UI shows source and verification date
5. **Minimal file footprint**: Only essential files added
6. **No secrets in frontend**: Manual entry is local Python tool, not web-based

