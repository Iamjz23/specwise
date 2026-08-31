#!/usr/bin/env python3
"""
SpecWise Market Price Collector
Semi-automated category-level price discovery for Canadian RAM & SSD products.

Architecture:
1. Newegg.ca - automated direct collection (when accessible)
2. HomeGadgets API - product discovery and price lookup (free tier)
3. Manual entry support via market-products.json

Outputs:
- market-products.json: persistent candidate/offer database
- ram-prices.json: computed category winners for frontend consumption
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import hashlib

# =============================================================================
# CONFIGURATION
# =============================================================================

CATEGORIES = {
    "ram": {
        "ddr4": [16, 32, 64, 128],
        "ddr5": [16, 32, 48, 64, 96, 128]
    },
    "ssd": [512, 1000, 2000, 4000, 8000]
}

RETAILER_MAPPING = {
    "amazon": "Amazon.ca",
    "amazon.ca": "Amazon.ca",
    "canada computers": "Canada Computers",
    "canadacomputers": "Canada Computers",
    "memory express": "Memory Express",
    "newegg": "Newegg Canada",
    "newegg.ca": "Newegg Canada",
    "pc-canada": "PC-Canada",
    "pc_canada": "PC-Canada"
}

TARGET_RETAILERS = ["Amazon.ca", "Canada Computers", "Memory Express", "Newegg Canada", "PC-Canada"]

FRESHNESS_DAYS = 7  # Offers older than this are marked stale

MAX_HOMEGADGETS_REQUESTS = 10  # Free tier limit per day

HOMEGADGETS_BASE = "https://www.homegadgets.ca/public/v1"

# =============================================================================
# DATA STRUCTURES
# =============================================================================

def generate_product_id(product_name: str, retailer: str, capacity_gb: int, category_type: str) -> str:
    """Generate a deterministic product ID."""
    key = f"{product_name.lower()}|{retailer}|{capacity_gb}|{category_type}"
    return hashlib.md5(key.encode()).hexdigest()[:16]

def normalize_retailer_name(name: str) -> str:
    """Normalize retailer name to standard format."""
    name_lower = name.lower().strip()
    return RETAILER_MAPPING.get(name_lower, name)

def parse_ram_capacity(text: str) -> Optional[int]:
    """Extract RAM capacity from product text, handling kit configurations."""
    text_upper = text.upper()
    
    # Check for SO-DIMM/laptop memory (reject)
    if any(x in text_upper for x in ["SO-DIMM", "SODIMM", "LAPTOP", "NOTEBOOK"]):
        return None
    
    # Look for capacity patterns like "32GB", "2x16GB", "2 x 16 GB", etc.
    # Pattern for kit notation: 2x16, 2x16GB, 2 x 16GB, etc.
    kit_pattern = r'(\d+)\s*[xX×]\s*(\d+)\s*GB?'
    kit_match = re.search(kit_pattern, text)
    
    if kit_match:
        sticks = int(kit_match.group(1))
        stick_capacity = int(kit_match.group(2))
        return sticks * stick_capacity
    
    # Direct capacity pattern
    cap_pattern = r'(\d+)\s*GB'
    cap_matches = re.findall(cap_pattern, text_upper)
    
    if cap_matches:
        # Take the first reasonable capacity value
        for cap in cap_matches:
            cap_int = int(cap)
            if cap_int in [16, 32, 48, 64, 96, 128, 256]:
                return cap_int
        # If no exact match, return the largest reasonable value
        valid_caps = [int(c) for c in cap_matches if int(c) <= 256]
        if valid_caps:
            return max(valid_caps)
    
    return None

def parse_ram_generation(text: str) -> Optional[str]:
    """Determine DDR generation from product text."""
    text_upper = text.upper()
    if "DDR5" in text_upper or "DDR 5" in text_upper:
        return "ddr5"
    elif "DDR4" in text_upper or "DDR 4" in text_upper:
        return "ddr4"
    elif "DDR3" in text_upper:
        return "ddr3"  # Will be filtered out
    return None

def parse_ssd_capacity(text: str) -> Optional[int]:
    """Extract SSD capacity in GB, rejecting misleading marketing text."""
    text_upper = text.upper()
    
    # Reject HDD
    if "HDD" in text_upper and "SSD" not in text_upper:
        return None
    
    # Look for explicit capacity before "up to" patterns
    # Avoid matching "supports up to 2TB"
    if "UP TO" in text_upper:
        # Try to find actual product capacity before "up to"
        before_up_to = text_upper.split("UP TO")[0]
        cap_pattern = r'(\d+)\s*(TB|GB)'
        match = re.search(cap_pattern, before_up_to)
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            if unit == "TB":
                return val * 1000
            else:
                return val
    
    # Standard capacity patterns
    tb_pattern = r'(\d+)\s*TB'
    gb_pattern = r'(\d+)\s*GB'
    
    tb_match = re.search(tb_pattern, text_upper)
    if tb_match:
        return int(tb_match.group(1)) * 1000
    
    gb_match = re.search(gb_pattern, text_upper)
    if gb_match:
        return int(gb_match.group(1))
    
    return None

def get_category_key(product_type: str, capacity_gb: int, generation: str = None) -> Optional[str]:
    """Get the category key for a product."""
    if product_type == "ram":
        if generation == "ddr4" and capacity_gb in CATEGORIES["ram"]["ddr4"]:
            return f"ram-ddr4-{capacity_gb}"
        elif generation == "ddr5" and capacity_gb in CATEGORIES["ram"]["ddr5"]:
            return f"ram-ddr5-{capacity_gb}"
    elif product_type == "ssd":
        # Find closest standard capacity
        for std_cap in CATEGORIES["ssd"]:
            if abs(capacity_gb - std_cap) <= std_cap * 0.1:  # Within 10%
                return f"ssd-{std_cap}"
    return None

# =============================================================================
# HOMEGADGETS API
# =============================================================================

class HomeGadgetsClient:
    """Client for HomeGadgets Canadian price API."""
    
    def __init__(self):
        self.request_count = 0
        self.last_request_time = None
        
    def can_make_request(self) -> bool:
        """Check if we can make another request within daily limits."""
        if self.request_count >= MAX_HOMEGADGETS_REQUESTS:
            return False
        return True
    
    def fetch(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to HomeGadgets API."""
        if not self.can_make_request():
            print(f"[HomeGadgets] Daily request limit reached ({MAX_HOMEGADGETS_REQUESTS})")
            return None
        
        from urllib.parse import urlencode
        
        url = f"{HOMEGADGETS_BASE}/{endpoint}"
        if params:
            query = urlencode(params)
            url = f"{url}?{query}"
        
        try:
            req = Request(url, headers={"User-Agent": "SpecWise-Market-Bot/1.0"})
            with urlopen(req, timeout=15) as response:
                self.request_count += 1
                self.last_request_time = datetime.now(timezone.utc)
                data = json.loads(response.read().decode('utf-8'))
                print(f"[HomeGadgets] Request {self.request_count}: {endpoint}")
                return data
        except HTTPError as e:
            print(f"[HomeGadgets] HTTP Error {e.code}: {endpoint}")
            if e.code == 429:
                print("[HomeGadgets] Rate limited - stopping requests")
                return None
            return None
        except URLError as e:
            print(f"[HomeGadgets] URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"[HomeGadgets] Error: {str(e)}")
            return None
    
    def search_products(self, query: str) -> List[Dict]:
        """Search for products using free-text search."""
        # Try the search endpoint
        data = self.fetch("search", {"q": query, "limit": 20})
        if data and isinstance(data, list):
            return data
        elif data and isinstance(data, dict) and "results" in data:
            return data["results"]
        return []
    
    def get_product_prices(self, product_id: str) -> Optional[Dict]:
        """Get current prices for a specific product."""
        return self.fetch(f"products/{product_id}/prices")

# =============================================================================
# NEWEGG COLLECTOR
# =============================================================================

def collect_newegg_products() -> List[Dict]:
    """Collect RAM and SSD products from Newegg Canada."""
    products = []
    
    search_queries = [
        # RAM searches
        ("DDR4 desktop memory 16GB", "ram", "ddr4"),
        ("DDR4 desktop memory 32GB", "ram", "ddr4"),
        ("DDR4 desktop memory 64GB", "ram", "ddr4"),
        ("DDR5 desktop memory 16GB", "ram", "ddr5"),
        ("DDR5 desktop memory 32GB", "ram", "ddr5"),
        ("DDR5 desktop memory 48GB", "ram", "ddr5"),
        ("DDR5 desktop memory 64GB", "ram", "ddr5"),
        # SSD searches
        ("NVMe SSD 512GB", "ssd", None),
        ("NVMe SSD 1TB", "ssd", None),
        ("NVMe SSD 2TB", "ssd", None),
        ("NVMe SSD 4TB", "ssd", None),
    ]
    
    base_url = "https://www.newegg.ca/p/pl?d="
    
    for query, product_type, generation in search_queries:
        url = f"{base_url}{query.replace(' ', '+')}"
        print(f"[Newegg] Searching: {query}")
        
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8"
            })
            
            with urlopen(req, timeout=20) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                # Simple parsing - look for product items
                # This is a basic implementation; real scraping would need proper HTML parsing
                print(f"[Newegg] Retrieved page for: {query}")
                
                # Note: Full HTML parsing would require BeautifulSoup or similar
                # For now, we note that Newegg access works but full parsing needs more work
                
        except HTTPError as e:
            if e.code in [403, 429, 503]:
                print(f"[Newegg] Blocked or rate-limited ({e.code})")
                break
            print(f"[Newegg] HTTP Error {e.code}")
        except Exception as e:
            print(f"[Newegg] Error: {str(e)}")
    
    return products

# =============================================================================
# MANUAL ENTRY SUPPORT
# =============================================================================

def load_existing_products(filepath: str) -> List[Dict]:
    """Load existing products from market-products.json."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "products" in data:
                    return data["products"]
        except Exception as e:
            print(f"Error loading existing products: {e}")
    return []

def save_products(products: List[Dict], filepath: str):
    """Save products to market-products.json."""
    # Sort by category and price
    sorted_products = sorted(products, key=lambda p: (p.get("category", ""), p.get("price", 99999)))
    
    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "productCount": len(sorted_products),
        "products": sorted_products
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[IO] Saved {len(sorted_products)} products to {filepath}")

def compute_category_winners(products: List[Dict]) -> Dict:
    """Compute the winning (cheapest) offer for each category."""
    winners = {}
    now = datetime.now(timezone.utc)
    
    # Group products by category
    by_category: Dict[str, List[Dict]] = {}
    for product in products:
        cat = product.get("category")
        if not cat:
            continue
        
        # Check freshness
        verified_at = product.get("verifiedAt", "")
        if verified_at:
            try:
                verified_time = datetime.fromisoformat(verified_at.replace('Z', '+00:00'))
                age_days = (now - verified_time).days
                product["_ageDays"] = age_days
                product["_isStale"] = age_days > FRESHNESS_DAYS
            except:
                product["_isStale"] = True
        else:
            product["_isStale"] = True
        
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(product)
    
    # Find winner for each category
    for category, offers in by_category.items():
        # Filter out stale offers for winner selection, but keep them in data
        fresh_offers = [o for o in offers if not o.get("_isStale", True)]
        
        if not fresh_offers:
            # Use stale offers if no fresh ones available
            fresh_offers = [o for o in offers if o.get("price")]
        
        if fresh_offers:
            # Sort by price
            fresh_offers.sort(key=lambda x: x.get("price", 99999))
            winner = fresh_offers[0]
            
            winners[category] = {
                "price": winner.get("price"),
                "currency": "CAD",
                "retailer": winner.get("retailer"),
                "productName": winner.get("productName"),
                "url": winner.get("url"),
                "source": winner.get("source", "manual"),
                "verifiedAt": winner.get("verifiedAt"),
                "alternatives": [
                    {
                        "price": o.get("price"),
                        "retailer": o.get("retailer"),
                        "productName": o.get("productName"),
                        "url": o.get("url")
                    }
                    for o in fresh_offers[1:3]  # Top 3 total
                ]
            }
    
    return winners

def generate_ram_prices_json(winners: Dict, output_path: str):
    """Generate the ram-prices.json file for the frontend."""
    now = datetime.now(timezone.utc)
    
    # Structure for frontend compatibility
    kits = {"ddr4": {}, "ddr5": {}}
    ssd = {}
    
    for category, data in winners.items():
        if category.startswith("ram-ddr4-"):
            cap = int(category.split("-")[-1])
            kits["ddr4"][str(cap)] = data["price"]
        elif category.startswith("ram-ddr5-"):
            cap = int(category.split("-")[-1])
            kits["ddr5"][str(cap)] = data["price"]
        elif category.startswith("ssd-"):
            cap = int(category.split("-")[-1])
            ssd[str(cap)] = data["price"]
    
    # Build detailed retailer info for each category (frontend expects this)
    # For simplicity, we create a structure similar to the original simulated data
    
    output = {
        "updated": now.isoformat(),
        "currency": "CAD",
        "note": "Prices collected from Canadian retailers. Data may be stale - verify before purchase.",
        "kits": kits,
        "ssd": ssd,
        "_winners": winners,  # Include full winner data for debugging
        "_metadata": {
            "generatedAt": now.isoformat(),
            "freshnessDays": FRESHNESS_DAYS,
            "targetRetailers": TARGET_RETAILERS
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[IO] Generated {output_path}")

# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def main():
    """Main execution workflow."""
    print("=" * 60)
    print("SpecWise Market Price Collector")
    print(f"Run started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    products_file = os.path.join(root_dir, "market-products.json")
    prices_file = os.path.join(root_dir, "ram-prices.json")
    
    # Load existing products
    print("\n[Step 1] Loading existing products...")
    existing_products = load_existing_products(products_file)
    print(f"Loaded {len(existing_products)} existing products")
    
    # Initialize HomeGadgets client
    print("\n[Step 2] Initializing HomeGadgets client...")
    hg_client = HomeGadgetsClient()
    
    # Search for products via HomeGadgets
    print("\n[Step 3] Discovering products via HomeGadgets...")
    search_queries = [
        "DDR4 desktop memory",
        "DDR5 desktop memory", 
        "NVMe SSD",
        "SATA SSD"
    ]
    
    discovered_products = []
    for query in search_queries:
        if not hg_client.can_make_request():
            break
        
        results = hg_client.search_products(query)
        print(f"  Query '{query}': {len(results)} results")
        
        for item in results[:10]:  # Limit per query
            # Parse and classify product
            product_name = item.get("name", item.get("title", ""))
            
            # Determine product type
            name_upper = product_name.upper()
            if "DDR" in name_upper:
                product_type = "ram"
                generation = parse_ram_generation(product_name)
                capacity = parse_ram_capacity(product_name)
                
                if generation and capacity and capacity <= 128:
                    category = get_category_key(product_type, capacity, generation)
                    if category:
                        # Get pricing info
                        prices = item.get("prices", [])
                        for price_info in prices:
                            retailer = normalize_retailer_name(price_info.get("retailer", ""))
                            if retailer in TARGET_RETAILERS:
                                discovered_products.append({
                                    "id": generate_product_id(product_name, retailer, capacity, product_type),
                                    "category": category,
                                    "productName": product_name,
                                    "brand": item.get("brand", "Unknown"),
                                    "retailer": retailer,
                                    "price": price_info.get("price"),
                                    "currency": "CAD",
                                    "url": price_info.get("url", item.get("url", "")),
                                    "source": "homegadgets",
                                    "verifiedAt": price_info.get("updatedAt", item.get("updatedAt", datetime.now(timezone.utc).isoformat()))
                                })
            
            elif "SSD" in name_upper or "NVME" in name_upper:
                product_type = "ssd"
                capacity = parse_ssd_capacity(product_name)
                
                if capacity:
                    category = get_category_key(product_type, capacity)
                    if category:
                        prices = item.get("prices", [])
                        for price_info in prices:
                            retailer = normalize_retailer_name(price_info.get("retailer", ""))
                            if retailer in TARGET_RETAILERS:
                                discovered_products.append({
                                    "id": generate_product_id(product_name, retailer, capacity, product_type),
                                    "category": category,
                                    "productName": product_name,
                                    "brand": item.get("brand", "Unknown"),
                                    "retailer": retailer,
                                    "price": price_info.get("price"),
                                    "currency": "CAD",
                                    "url": price_info.get("url", item.get("url", "")),
                                    "source": "homegadgets",
                                    "verifiedAt": price_info.get("updatedAt", item.get("updatedAt", datetime.now(timezone.utc).isoformat()))
                                })
    
    print(f"\nDiscovered {len(discovered_products)} new product offers")
    
    # Merge with existing products
    print("\n[Step 4] Merging with existing products...")
    all_products = existing_products.copy()
    
    # Add new discoveries (avoid duplicates by ID)
    existing_ids = {p.get("id") for p in all_products}
    for product in discovered_products:
        if product.get("id") not in existing_ids:
            all_products.append(product)
            existing_ids.add(product.get("id"))
        else:
            # Update existing product if newer data
            for i, existing in enumerate(all_products):
                if existing.get("id") == product.get("id"):
                    # Keep the one with more recent verification
                    if product.get("verifiedAt", "") > existing.get("verifiedAt", ""):
                        all_products[i] = product
                    break
    
    # Attempt Newegg collection (may fail due to blocking)
    print("\n[Step 5] Attempting Newegg direct collection...")
    newegg_products = collect_newegg_products()
    # Note: Full implementation would parse HTML and add products
    
    # Save updated products
    print("\n[Step 6] Saving products...")
    save_products(all_products, products_file)
    
    # Compute winners
    print("\n[Step 7] Computing category winners...")
    winners = compute_category_winners(all_products)
    
    print("\nCategory Winners:")
    print("-" * 50)
    for cat in sorted(winners.keys()):
        w = winners[cat]
        print(f"  {cat}: ${w['price']} @ {w['retailer']} ({w['productName'][:40]}...)")
    
    # Generate ram-prices.json
    print("\n[Step 8] Generating ram-prices.json...")
    generate_ram_prices_json(winners, prices_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total products tracked: {len(all_products)}")
    print(f"Categories with winners: {len(winners)}")
    print(f"HomeGadgets requests used: {hg_client.request_count}/{MAX_HOMEGADGETS_REQUESTS}")
    print(f"Output files: {products_file}, {prices_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
