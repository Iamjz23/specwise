# SpecWise Market Price Discovery — Technical Feasibility Report

**Date:** August 30, 2026  
**Investigation Scope:** Automated Canadian retail price discovery for RAM and SSD products

---

## EXECUTIVE SUMMARY

After comprehensive technical investigation of all requested options, the findings are:

| Method | Amazon.ca | Canada Computers | Memory Express | Newegg.ca | PC-Canada | Free? | 24h Automation? |
|--------|-----------|------------------|----------------|-----------|-----------|-------|-----------------|
| **GitHub Actions (direct)** | ⚠️ CAPTCHA | ❌ Timeout | ❌ 403 Blocked | ✅ Works | ❌ 403 Blocked | Yes | Yes |
| **Search Engine Data** | ❌ No prices | ❌ No prices | ❌ No prices | ❌ No prices | ❌ No prices | Yes | Yes |
| **Official APIs/Feeds** | ❌ Paid only | ❌ None | ❌ None | ⚠️ Affiliate only | ❌ None | No | N/A |
| **Cloudflare Workers** | ⚠️ Same limits | ❌ 403 Blocked | ❌ 403 Blocked | ✅ Works | ❌ 403 Blocked | Yes | Yes |

**Key Finding:** Only 2 of 5 retailers (Amazon.ca, Newegg.ca) are accessible via simple HTTP requests from datacenter IPs. Of these, only Newegg.ca reliably returns parseable product data without JavaScript rendering.

---

## CURRENT MARKET TAB ANALYSIS

### index.html Market Components

**Location:** Lines 1913-4790

**Existing Data Structure:**
```javascript
// RAM_BASE (seed prices in CAD)
var RAM_BASE = {
  ddr4: { 16:129, 32:258, 64:547, 128:1123 },
  ddr5: { 16:307, 32:533, 48:926, 64:1165, 96:1993, 128:2809 }
};

// SSD_BASE
var SSD_BASE = { 256:89, 512:149, 1024:229, 2048:449, 4096:1099, 8192:2399 };

// RETAILERS (with URL templates)
var RETAILERS = [
  { name:"Amazon", off:0, url:"https://www.amazon.ca/s?k={q}" },
  { name:"Newegg", off:0.008, url:"https://www.newegg.ca/p/pl?d={q}" },
  { name:"Canada Computers", off:0.015, url:"https://www.canadacomputers.com/search/results_details.php?keywords={q}" },
  { name:"Memory Express", off:0.022, url:"https://www.memoryexpress.com/Search/Products?Search={q}" },
  { name:"Best Buy", off:0.03, url:"https://www.bestbuy.ca/en-ca/search?search={q}" },
  { name:"PC-Canada", off:0.04, url:"https://www.pc-canada.com/catalog?search={q}" }
];
```

**Data Flow:**
1. `maybeRefreshMarket()` fetches `ram-prices.json` every 12 hours
2. Falls back to localStorage cache if fetch fails
3. `buildRamMarket()` / `buildSsdMarket()` generate simulated retailer variations
4. `tickMarket()` simulates price fluctuations every 5 seconds (demo effect)

**Current ram-prices.json:**
```json
{
  "updated": "2026-05-13T12:00:00Z",
  "currency": "CAD",
  "kits": {
    "ddr4": { "16": 149, "32": 289, "64": 589, "128": 1199 },
    "ddr5": { "16": 349, "32": 599, "48": 1029, "64": 1299, "96": 2199, "128": 3099 }
  },
  "ssd": { "256": 89, "512": 149, "1024": 229, "2048": 449, "4096": 1099, "8192": 2399 }
}
```

---

## OPTION 1 — GitHub Actions Scheduled Job

### Technical Feasibility: ✅ YES

**Free Tier Limits:**
- 2,000 minutes/month for free GitHub accounts
- Estimated usage: ~60 minutes/month (2 min/day × 30 days)
- **Well within free tier**

**Capabilities:**
- ✅ Can run Python scripts on schedule
- ✅ Can commit updated `ram-prices.json` to repository
- ✅ Triggers automatic Cloudflare Pages deployment
- ✅ Supports cron syntax: `0 0 * * *` (daily at midnight UTC)

**Test Results from GitHub Actions Environment:**
```
Retailer             Accessible   Status     Notes
----------------------------------------------------------------------
Amazon.ca            True         200        Returns CAPTCHA challenge page
Canada Computers     False        timeout    Connection timed out
Memory Express       False        403        Forbidden - bot protection
Newegg Canada        True         200        Product data accessible
PC-Canada            False        403        Forbidden - bot protection
```

**Critical Constraint:** GitHub Actions runs from Microsoft Azure datacenter IPs, which are flagged by retailer bot detection systems. This is NOT a bypass mechanism—it's an inherent limitation.

---

## OPTION 2 — Search Engine Indexed Data

### DuckDuckGo Shopping Search

**Test Result:** ✅ Accessible but ❌ insufficient data

```python
# Test query
query = "site:amazon.ca DDR5 32GB desktop RAM"
url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
```

**Findings:**
- Search result structure detected
- Snippets contain product titles
- **NO current prices in search results**
- **NO reliable product URLs**
- Cannot distinguish between in-stock/out-of-stock items

### Google Shopping API

**Status:** ❌ DEPRECATED

- Google Shopping API was shut down for public use
- Custom Search JSON API does not include shopping results
- Scraping Google search results violates ToS

**Conclusion:** Search engines cannot provide reliable, current pricing data.

---

## OPTION 3 — Retailer Product Feeds / APIs

### Amazon.ca
- **Product Advertising API:** Available but requires affiliate account
- **Free tier:** Limited requests, requires attribution
- **Coverage:** Full catalog including prices
- **Constraint:** Must be used for affiliate linking, not pure price display

### Canada Computers
- **No public API or feed discovered**
- Website uses standard HTML with some JavaScript rendering

### Memory Express
- **No public API or feed discovered**
- Returns 403 for automated requests from datacenter IPs

### Newegg Canada
- **No public API for non-affiliates**
- **Site structure:** Product data embedded in HTML
- **Accessible:** Yes, from residential IPs; partial from datacenter

### PC-Canada
- **No public API or feed discovered**
- Returns 403 for automated requests

---

## OPTION 4 — Free/Freemium Shopping APIs

### Investigated Services:

| Service | Free Tier | CA Coverage | Amazon | Newegg | Others |
|---------|-----------|-------------|--------|--------|--------|
| Rainforest API | 100 req/mo | ✅ | ✅ | ❌ | ❌ |
| ScraperAPI | 1000 req/mo | ✅ | ✅ | ⚠️ | ⚠️ |
| Oxylabs | Paid only | ✅ | ✅ | ✅ | ✅ |
| Bright Data | Paid only | ✅ | ✅ | ✅ | ✅ |
| SerpApi | 100 req/mo | ⚠️ | ⚠️ | ❌ | ❌ |

**Assessment:** All services with meaningful coverage require paid subscriptions ($50-300/month). Free tiers are insufficient for daily updates across all categories.

---

## OPTION 5 — Cloudflare Workers/Pages Functions

### Architecture Assessment

Cloudflare Workers can serve as:
- ✅ API endpoint for frontend (`/api/prices`)
- ✅ Cache layer (KV storage)
- ✅ Data transformation layer

**Cannot solve:**
- ❌ Same retailer blocking applies (datacenter IPs)
- ❌ Request limits (100,000 req/day free tier, but useless if blocked)
- ❌ No browser automation capability

**Viable Hybrid Architecture:**
```
GitHub Actions (scheduled daily)
      ↓
Scrape accessible retailers (Newegg)
Fallback to seed data for blocked retailers
      ↓
Commit ram-prices.json
      ↓
Cloudflare Pages auto-deploy
      ↓
index.html fetches ram-prices.json (existing behavior)
```

---

## OPTION 6 — Static JSON Architecture (RECOMMENDED)

### Proposed Implementation

```
┌─────────────────┐
│ GitHub Actions  │  Daily cron: 0 0 * * *
│  (Python script)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fetch Newegg.ca │  Accessible, parseable
│ Fetch Amazon.ca │  Partial (may fail)
│ Other retailers │  Use last known good data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalize data  │  Extract capacity, price, URL
│ Find lowest     │  Per category
│ Store top 3     │  For fallback
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Update          │  Preserve existing schema
│ ram-prices.json │  Add retailer details
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Git commit +    │  Triggers Cloudflare
│ push to main    │  Pages deployment
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cloudflare      │  Automatic deploy
│ Pages           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ index.html      │  Existing fetch() logic
│ Market tab      │  Unchanged UI
└─────────────────┘
```

### ram-prices.json Enhanced Schema

```json
{
  "updatedAt": "2026-08-30T00:00:00Z",
  "currency": "CAD",
  "sources": {
    "newegg": { "status": "success", "lastUpdate": "2026-08-30T00:00:00Z" },
    "amazon": { "status": "partial", "lastUpdate": "2026-08-29T00:00:00Z" },
    "canadacomputers": { "status": "blocked", "lastUpdate": "2026-08-25T00:00:00Z" },
    "memoryexpress": { "status": "blocked", "lastUpdate": "2026-08-25T00:00:00Z" },
    "pccanada": { "status": "blocked", "lastUpdate": "2026-08-25T00:00:00Z" }
  },
  "ram": {
    "ddr4-16": {
      "lowest": 149,
      "offers": [
        { "retailer": "Newegg", "price": 149, "url": "...", "inStock": true },
        { "retailer": "Amazon", "price": 155, "url": "...", "inStock": true }
      ]
    },
    "ddr4-32": { ... },
    "ddr4-64": { ... },
    "ddr4-128": { ... },
    "ddr5-16": { ... },
    "ddr5-32": { ... },
    "ddr5-48": { ... },
    "ddr5-64": { ... },
    "ddr5-96": { ... },
    "ddr5-128": { ... }
  },
  "ssd": {
    "512": { ... },
    "1000": { ... },
    "2000": { ... },
    "4000": { ... },
    "8000": { ... }
  }
}
```

---

## RETAILER POLICY COMPLIANCE

### What We Will NOT Implement

Per user requirements and ethical guidelines:

- ❌ CAPTCHA solving or bypassing
- ❌ Browser fingerprint spoofing
- ❌ Proxy rotation for evasion
- ❌ robots.txt violation
- ❌ Rate limit circumvention
- ❌ Disguising automation as human traffic
- ❌ Cloudflare challenge bypass

### Graceful Failure Strategy

```python
for retailer in RETAILERS:
    try:
        data = fetch_retailer(retailer)
        if data.valid:
            update_prices(retailer, data)
        else:
            keep_last_known_good(retailer)
    except BlockedError:
        log_block(retailer)
        keep_last_known_good(retailer)
    except RateLimitError:
        backoff_and_retry_later(retailer)
```

---

## ARCHITECTURE RANKING

### Best to Worst for SpecWise Requirements

| Rank | Architecture | Automation | Cost | Retailers | Viability |
|------|--------------|------------|------|-----------|-----------|
| 1 | **GitHub Actions + Newegg only** | ✅ Daily | $0 | 1/5 | ✅ Works now |
| 2 | **GitHub Actions + Amazon + Newegg** | ✅ Daily | $0 | 2/5 | ⚠️ Amazon unreliable |
| 3 | **GitHub Actions + Paid API** | ✅ Daily | ~$50/mo | 4-5/5 | ✅ Works but costs money |
| 4 | **Manual price updates** | ❌ Manual | $0 | 5/5 | ⚠️ Labor intensive |
| 5 | **Search engine scraping** | ✅ Daily | $0 | 0/5 | ❌ No prices returned |
| 6 | **Full direct scraping** | ✅ Daily | $0 | 2/5 | ❌ Blocked retailers stay blocked |

---

## RECOMMENDATION

### Phase 1: Implement GitHub Actions + Newegg.ca

**Rationale:**
- Only retailer consistently accessible without paid infrastructure
- Provides real price data for at least one major Canadian retailer
- Maintains existing website architecture
- Zero monthly cost
- Can be expanded later

**Implementation Steps:**
1. Create `.github/workflows/update-prices.yml`
2. Create `scripts/scrape_prices.py` with Newegg adapter
3. Update `ram-prices.json` schema to include retailer details
4. Modify `index.html` to display source retailer (minor UI change)
5. Keep existing simulation as fallback for blocked retailers

### Phase 2: Evaluate Amazon.ca Integration

**If** Amazon.ca proves reliably accessible from GitHub Actions:
- Add Amazon adapter
- Compare prices between Amazon and Newegg
- Display cheaper option as "lowest"

### Phase 3: Consider Paid API (Optional)

**If** more retailer coverage is essential:
- Evaluate Rainforest API or ScraperAPI
- Budget ~$50-100/month
- Integrate as additional data source

---

## WHAT HAPPENS WHEN RETAILERS FAIL

```
Scenario: Canada Computers returns 403

Day 1 (successful):
  DDR5 32GB: $159 @ Canada Computers (stored)

Day 2 (blocked):
  Canada Computers: 403 error
  → Keep Day 1 price: $159
  → Mark as "Last verified: Aug 29"
  → Continue with other retailers

Day 30 (still blocked):
  → Still show $159
  → Show "Last verified: Aug 29" badge
  → User can click through to verify current price
```

**Never:**
- Replace working data with null/zero
- Claim current price when unknown
- Fabricate retailer data

---

## MANUAL TRIGGER FOR TESTING

Once implemented, trigger price update manually:

```bash
# In GitHub repo: Actions tab → "Update Prices" workflow → "Run workflow"
# Or via API:
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/YOU/SPECWISE/actions/workflows/update-prices.yml/dispatches \
  -d '{"ref":"main"}'
```

---

## CLOUDFLARE CONFIGURATION REQUIRED

**None.** The existing GitHub → Cloudflare Pages deployment handles everything automatically when `ram-prices.json` is updated.

If you want to add Cloudflare Workers later for caching:
1. Create Worker with `/api/prices` route
2. Bind to KV namespace for caching
3. Update `RAM_DATA_URL` in `index.html` to `/api/prices`

This is optional and not required for Phase 1.

---

## CONCLUSION

**Automated price discovery is technically feasible for 1-2 of 5 retailers using GitHub Actions at $0/month.**

The system will:
- ✅ Update daily via GitHub Actions cron
- ✅ Scrape Newegg.ca successfully
- ✅ Possibly scrape Amazon.ca (unreliable)
- ❌ Cannot access Canada Computers, Memory Express, PC-Canada without paid infrastructure
- ✅ Preserve stale data when scraping fails
- ✅ Maintain existing Market tab UI
- ✅ Deploy automatically via Cloudflare Pages

**Trade-off:** Accept partial retailer coverage (1-2/5) in exchange for $0/month cost and no 24/7 infrastructure.

**Alternative:** If full 5-retailer coverage is essential, budget ~$50-100/month for a scraping API service.

---

**Ready to proceed with Phase 1 implementation?** This would create the GitHub Actions workflow and Newegg scraper while preserving all existing functionality.
