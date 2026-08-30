# SpecWise Market — Automated Price Discovery Feasibility Report (V2)

## Executive Summary

After thorough technical investigation of all proposed options, **automated price discovery for Canadian RAM/SSD pricing faces significant technical barriers** that prevent reliable implementation using free infrastructure only.

---

## Option 1: GitHub Actions Scheduled Scraper

### Technical Findings

**GitHub Actions Free Tier:**
- 2,000 minutes/month included
- Sufficient for daily ~5-minute scraping jobs
- No cost for public repositories

**Retailer Accessibility Testing:**

| Retailer | HTTP Status | Parseable Data | Anti-Bot Protection | Verdict |
|----------|-------------|----------------|---------------------|---------|
| Amazon.ca | 200 (with CAPTCHA) | ❌ No | Strong | BLOCKED |
| Canada Computers | Timeout | ❌ No | Connection-level | BLOCKED |
| Memory Express | 403 Forbidden | ❌ No | Bot detection | BLOCKED |
| Newegg.ca | 200 OK | ⚠️ Partial (JS-rendered) | Moderate | PARTIALLY WORKS |
| PC-Canada | 403 Forbidden | ❌ No | Bot detection | BLOCKED |

**Newegg.ca Detailed Analysis:**
- HTML returned but product data is JavaScript-rendered
- No embedded JSON state found in page source
- API endpoints return 404
- Would require headless browser (Puppeteer/Playwright) which:
  - Exceeds GitHub Actions time limits
  - Violates "no browser automation" requirement
  - May violate retailer terms

**Conclusion:** Only 1 of 5 retailers (Newegg) is technically accessible, and even that requires JavaScript rendering not available in simple curl-based scrapers.

---

## Option 2: Search Engine Indexed Data

### Technical Findings

**Google/Bing Custom Search APIs:**
- Free tier: 100 queries/day (Google)
- Returns snippets, NOT structured prices
- Cannot reliably extract current CAD pricing
- Search results show outdated/stale prices

**DuckDuckGo:**
- No official API
- HTML search results don't include current prices
- Rate limiting applies

**Test Query Results:**
```
Query: "site:newegg.ca DDR5 32GB RAM price"
Result: Snippets without structured price data
```

**Conclusion:** Search engines do not expose real-time pricing data in a machine-readable format. Not viable for accurate price discovery.

---

## Option 3: Shopping/Product Feeds

### Investigation Results

| Retailer | Public Feed | Affiliate Feed | API Available | Notes |
|----------|-------------|----------------|---------------|-------|
| Amazon.ca | ❌ No | ✅ Product Advertising API | ✅ Yes | Requires approval, associate account |
| Canada Computers | ❌ No | ❌ Unknown | ❌ No | No public program found |
| Memory Express | ❌ No | ❌ No | ❌ No | No affiliate program |
| Newegg Canada | ⚠️ Limited | ✅ Partner Program | ⚠️ Limited | Requires application |
| PC-Canada | ❌ No | ❌ No | ❌ No | No public program |

**Amazon Product Advertising API:**
- Requires Amazon Associates account
- Must generate 3 qualified sales in first 180 days
- API rate limits apply
- Complex authentication (AWS SigV4)
- Returns prices but requires ongoing sales qualification

**Newegg Partner Program:**
- Application required
- Feed access not guaranteed
- Terms may prohibit automated scraping

**Conclusion:** No retailer provides open, permissionless product feeds suitable for this use case.

---

## Option 4: Free/Freemium Shopping APIs

### Investigated Services

| Service | Free Quota | Canadian Coverage | Target Retailers | Verdict |
|---------|------------|-------------------|------------------|---------|
| Google Shopping API | Discontinued (paid only) | Good via paid | Partial | NOT FREE |
| Bing Shopping API | Paid only | Good | Partial | NOT FREE |
| PriceAPI.com | 100 req/month | Limited | None of target | INSUFFICIENT |
| ScrapingBee | 1000 req/month (free) | N/A (proxy service) | N/A | STILL NEEDS SCRAPER |
| HomeGadgets.ca | 10 req/day anonymous | ✅ Yes | ✅ All 5 tracked | LIMITED BUT WORKS |

**HomeGadgets.ca Deep Dive:**

Discovered during investigation: https://www.homegadgets.ca/public/v1/openapi.json

**Capabilities:**
- Tracks 20,000+ products across 140+ Canadian retailers
- Includes: Amazon.ca, Canada Computers, Memory Express, Newegg, PC-Canada
- Returns: price_cad, retailer, buy_link, observed_at, retailer_count
- Provides TWO cheapest offers per product
- Anonymous access: NO API key required

**Limitations:**
- 10 requests/day per IP (anonymous tier)
- 250 requests/day shared global ceiling
- 200 catalogue rows/day maximum
- Maximum 20 search results per request
- Catalog updated on schedule (NOT live)
- Search terms tested:
  - "DDR5 32GB desktop memory" → 0 results
  - "DDR5 memory" → 0 results  
  - "RAM" → 20 results (all toner cartridges, wrong category!)
  - "SSD 1TB" → 20 results (all laptops with SSDs, not standalone)
  - "NVMe SSD" → 20 results (laptops, not drives)
  - "Corsair Vengeance DDR5" → 0 results
  - "Samsung 990 Pro SSD" → 0 results

**Critical Finding:** HomeGadgets does NOT currently track standalone RAM modules or SSDs as discrete products. Their catalog focuses on:
- Appliances
- Laptops (with RAM/SSD as components)
- Toner cartridges
- Consumer electronics

The search API returns zero results for component-level queries like "DDR5 RAM" or "NVMe SSD".

**Conclusion:** HomeGadgets has the right infrastructure and retailer coverage, but does not track the specific product categories (desktop RAM, standalone SSDs) needed for SpecWise Market.

---

## Option 5: Cloudflare Workers as Data Layer

### Assessment

**Cloudflare Workers Free Tier:**
- 100,000 requests/day
- 10ms CPU time per request
- Can serve as API endpoint
- Can cache responses

**Viability:**
- ✅ Excellent for serving price data TO frontend
- ❌ Cannot run scraper (time limits, no persistent storage without D1)
- ❌ Same retailer blocking issues as any serverless function

**Recommended Role:**
Use Cloudflare Workers ONLY as:
- Cache layer for ram-prices.json
- API endpoint if dynamic serving needed
- NOT as scraper execution environment

---

## Option 6: Static JSON Architecture (Simplest)

### Proposed Architecture

```
GitHub Actions (daily cron)
       ↓
Update ram-prices.json
       ↓
Git commit → push
       ↓
Cloudflare Pages auto-deploy
       ↓
index.html fetches ram-prices.json
```

**Requirements:**
1. Working scraper that can actually retrieve prices
2. JSON schema compatible with existing Market tab
3. Fallback mechanism for failed updates

**Blocker:**
No working scraper exists for 4 of 5 retailers. Newegg alone provides insufficient market coverage.

---

## Critical Constraints Summary

### What We CANNOT Do (Per Requirements)

1. ❌ Run 24/7 server/VPS/Raspberry Pi
2. ❌ Use paid proxy services
3. ❌ Use paid APIs
4. ❌ Bypass CAPTCHAs
5. ❌ Defeat anti-bot protections
6. ❌ Spoof browser fingerprints
7. ❌ Circumvent robots.txt
8. ❌ Use browser automation at scale
9. ❌ Claim "lowest price in Canada" without checking all retailers

### What Actually Works

| Method | Retailers Covered | Cost | Automation | Accuracy |
|--------|-------------------|------|------------|----------|
| Direct scraping (curl) | 0/5 | $0 | ✅ Yes | N/A |
| Direct scraping (headless browser) | 1/5 (Newegg) | $0 | ⚠️ Slow | Medium |
| HomeGadgets API | 0/5 (wrong categories) | $0 | ✅ Yes | N/A |
| Amazon PA-API | 1/5 | $0* | ✅ Yes | High (*requires sales) |
| Manual entry | 5/5 | Time cost | ❌ No | High |

---

## Honest Assessment

### The Fundamental Problem

**Canadian PC component retailers do not provide open, machine-readable price data for RAM/SSD components.**

This is not a technical limitation that can be solved with better code. It is a business reality:

1. Retailers actively block automated access
2. No public product feeds exist for components
3. Affiliate APIs require sales qualifications
4. Third-party aggregators don't track these categories

### What This Means for SpecWise

Given the constraints ($0/month, no 24/7 hardware, no bot bypassing), **fully automated price discovery is not technically feasible** for the specified retailers and product categories.

---

## Recommended Path Forward

### Option A: Hybrid Semi-Automated System

**Architecture:**
1. Keep existing `ram-prices.json` structure
2. Create GitHub Action workflow (infrastructure ready)
3. Add manual price entry mechanism:
   - Simple form (Google Forms / GitHub Issue template)
   - Monthly price update ritual
4. Display "Last verified: [date]" honestly

**Pros:**
- $0/month
- Accurate data
- Compliant with all retailer policies
- Preserves Market UI

**Cons:**
- Not fully automated
- Requires manual effort

### Option B: Single-Retailer Automation (Newegg Only)

**Architecture:**
1. GitHub Actions daily job
2. Scrape Newegg.ca only (with proper rate limiting)
3. Fall back to seed data for other retailers
4. Label results honestly: "Newegg price" vs "Seed estimate"

**Pros:**
- Partially automated
- One real data source
- $0/month

**Cons:**
- Only 1 of 5 retailers
- Still risks Newegg blocking
- Misleading if presented as "market-wide"

### Option C: Affiliate API Integration

**Architecture:**
1. Apply for Amazon Associates + Newegg Partner programs
2. Implement official API clients
3. Accept that 3 retailers (Canada Computers, Memory Express, PC-Canada) won't be covered
4. Display "Prices from Amazon/Newegg partners"

**Pros:**
- Legitimate, permitted access
- Real-time pricing
- Potential revenue share

**Cons:**
- Requires application/approval
- Must maintain sales quotas
- Only covers 2 of 5 retailers
- More complex implementation

---

## Final Recommendation

**Implement Option A (Hybrid Semi-Automated) with infrastructure for future expansion.**

Rationale:
1. Honest about limitations
2. Keeps existing Market UI intact
3. Infrastructure ready if better data sources emerge
4. $0/month operating cost
5. Compliant with all retailer policies
6. Can upgrade to partial automation later

The GitHub Actions infrastructure should still be built—it's useful even for semi-automated workflows. But we must be honest that **retailer data is not freely available** for automated collection without either:
- Paid services
- Policy-violating workarounds
- Manual effort

---

## Files Referenced

- `/workspace/index.html` — Existing Market tab implementation
- `/workspace/ram-prices.json` — Current simulated price data
- `/workspace/FEASIBILITY_REPORT.md` — Previous investigation
- HomeGadgets API: https://www.homegadgets.ca/public/v1/openapi.json

---

## Test Commands Used

```bash
# HomeGadgets API tests
curl "https://www.homegadgets.ca/public/v1/search/DDR5%2032GB%20desktop%20memory"
curl "https://www.homegadgets.ca/public/v1/search/NVMe%20SSD"
curl "https://www.homegadgets.ca/public/v1/search/Corsair%20Vengeance%20DDR5"

# Newegg scraping tests
curl "https://www.newegg.ca/p/pl?d=DDR5+32GB&N=100007693"

# Retailer blocking tests
curl "https://www.canadacomputers.com/search..."  # Timeout
curl "https://www.memoryexpress.com/Search/..."   # 403
curl "https://www.pc-canada.com/catalog..."        # 403
```

---

**Report Date:** December 2025
**Investigation Duration:** Comprehensive multi-option analysis
**Confidence Level:** High — based on actual API testing and HTTP response analysis
