#!/usr/bin/env python3
"""
SpecWise Market - Manual Price Entry Tool

This tool allows you to manually add product offers from retailers that cannot be 
automatically scraped (Amazon.ca, Canada Computers, Memory Express, PC-Canada).

Usage:
    python scripts/manual_entry.py
    
The tool will guide you through entering product information interactively.
After entering offers, it will:
1. Add them to market-products.json
2. Recalculate category winners
3. Regenerate ram-prices.json

You can also run in batch mode:
    python scripts/manual_entry.py --batch input.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional
import hashlib

# Import functions from collect_prices.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect_prices import (
    CATEGORIES,
    TARGET_RETAILERS,
    FRESHNESS_DAYS,
    generate_product_id,
    normalize_retailer_name,
    parse_ram_capacity,
    parse_ram_generation,
    parse_ssd_capacity,
    get_category_key,
    load_existing_products,
    save_products,
    compute_category_winners,
    generate_ram_prices_json
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PRODUCTS_FILE = os.path.join(PROJECT_ROOT, "market-products.json")
PRICES_FILE = os.path.join(PROJECT_ROOT, "ram-prices.json")


def print_header():
    """Print tool header."""
    print("=" * 60)
    print("SpecWise Market - Manual Price Entry Tool")
    print("=" * 60)
    print()
    print("This tool helps you manually add product offers from retailers.")
    print("Supported retailers:", ", ".join(TARGET_RETAILERS))
    print()


def print_categories():
    """Print available categories."""
    print("\nAvailable Categories:")
    print("-" * 40)
    print("RAM DDR4: 16GB, 32GB, 64GB, 128GB")
    print("RAM DDR5: 16GB, 32GB, 48GB, 64GB, 96GB, 128GB")
    print("SSD: 512GB, 1TB (1000GB), 2TB (2000GB), 4TB (4000GB), 8TB (8000GB)")
    print("-" * 40)


def get_input(prompt: str, required: bool = True, default: str = None) -> str:
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        value = input(prompt).strip()
        if not value and default:
            return default
        if not value and required:
            print("  This field is required. Please enter a value.")
            continue
        return value


def select_retailer() -> str:
    """Let user select a retailer from the list."""
    print("\nSelect Retailer:")
    for i, retailer in enumerate(TARGET_RETAILERS, 1):
        print(f"  {i}. {retailer}")
    
    while True:
        choice = get_input("Enter number (1-5)")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(TARGET_RETAILERS):
                return TARGET_RETAILERS[idx]
        except ValueError:
            pass
        print("  Invalid selection. Please try again.")


def select_category_type() -> tuple:
    """Let user select product type and category."""
    print("\nSelect Product Type:")
    print("  1. RAM (Desktop Memory)")
    print("  2. SSD (Solid State Drive)")
    
    while True:
        choice = get_input("Enter number (1-2)")
        if choice == "1":
            print("\nSelect RAM Generation:")
            print("  1. DDR4")
            print("  2. DDR5")
            gen_choice = get_input("Enter number (1-2)")
            if gen_choice == "1":
                gen = "ddr4"
                caps = CATEGORIES["ram"]["ddr4"]
            else:
                gen = "ddr5"
                caps = CATEGORIES["ram"]["ddr5"]
            
            print(f"\nSelect Capacity ({gen.upper()}):")
            for i, cap in enumerate(caps, 1):
                print(f"  {i}. {cap}GB")
            
            while True:
                cap_choice = get_input(f"Enter number (1-{len(caps)})")
                try:
                    idx = int(cap_choice) - 1
                    if 0 <= idx < len(caps):
                        return ("ram", gen, caps[idx])
                except ValueError:
                    pass
                print("  Invalid selection.")
                
        elif choice == "2":
            caps = CATEGORIES["ssd"]
            print("\nSelect SSD Capacity:")
            for i, cap in enumerate(caps, 1):
                tb = cap / 1000 if cap >= 1000 else cap
                unit = "TB" if cap >= 1000 else "GB"
                print(f"  {i}. {tb}{unit} ({cap}GB)")
            
            while True:
                cap_choice = get_input(f"Enter number (1-{len(caps)})")
                try:
                    idx = int(cap_choice) - 1
                    if 0 <= idx < len(caps):
                        return ("ssd", None, caps[idx])
                except ValueError:
                    pass
                print("  Invalid selection.")
        else:
            print("  Invalid selection. Please try again.")


def validate_product_name(product_name: str, product_type: str, expected_cap: int, generation: str = None) -> bool:
    """Validate that product name matches the selected category."""
    if product_type == "ram":
        cap = parse_ram_capacity(product_name)
        gen = parse_ram_generation(product_name)
        
        # Check for SO-DIMM/laptop memory
        if "SO-DIMM" in product_name.upper() or "SODIMM" in product_name.upper():
            if "LAPTOP" in product_name.upper() or "NOTEBOOK" in product_name.upper():
                print("  ⚠ Warning: This appears to be laptop memory. Desktop memory only.")
                return False
        
        if cap != expected_cap:
            print(f"  ⚠ Warning: Detected capacity {cap}GB doesn't match selected {expected_cap}GB")
            confirm = get_input("Continue anyway? (y/n)", default="n")
            return confirm.lower() == "y"
        
        if generation and gen != generation:
            print(f"  ⚠ Warning: Detected {gen.upper()} doesn't match selected {generation.upper()}")
            confirm = get_input("Continue anyway? (y/n)", default="n")
            return confirm.lower() == "y"
            
    elif product_type == "ssd":
        cap = parse_ssd_capacity(product_name)
        if cap and abs(cap - expected_cap) > expected_cap * 0.15:  # 15% tolerance
            print(f"  ⚠ Warning: Detected capacity {cap}GB doesn't match selected {expected_cap}GB")
            confirm = get_input("Continue anyway? (y/n)", default="n")
            return confirm.lower() == "y"
    
    return True


def enter_single_offer(existing_products: List[Dict]) -> Optional[Dict]:
    """Guide user through entering a single product offer."""
    print("\n" + "=" * 60)
    print("ENTER NEW PRODUCT OFFER")
    print("=" * 60)
    
    # Select category
    product_type, generation, capacity = select_category_type()
    category = get_category_key(product_type, capacity, generation)
    
    print(f"\nSelected Category: {category}")
    
    # Select retailer
    retailer = select_retailer()
    
    # Get product details
    print("\nEnter Product Details:")
    product_name = get_input("Product Name (full title from retailer website)", required=True)
    
    # Validate product name
    if not validate_product_name(product_name, product_type, capacity, generation):
        return None
    
    brand = get_input("Brand", required=False, default=product_name.split()[0] if product_name else "Unknown")
    
    # Get price
    while True:
        price_str = get_input("Price in CAD (e.g., 89.99)", required=True)
        try:
            price = float(price_str)
            if price > 0:
                break
            print("  Price must be greater than 0.")
        except ValueError:
            print("  Invalid price format. Please enter a number.")
    
    # Get URL
    url = get_input("Product URL (optional, but recommended)", required=False)
    if url and not url.startswith("http"):
        url = "https://" + url
    
    # Generate product ID
    product_id = generate_product_id(product_name, retailer, capacity, product_type)
    
    # Check for existing offer
    for existing in existing_products:
        if existing.get("id") == product_id:
            print(f"\n⚠ An offer for this product/retailer combination already exists:")
            print(f"   {existing.get('productName')} @ {existing.get('retailer')} - ${existing.get('price')}")
            overwrite = get_input("Overwrite with new data? (y/n)", default="n")
            if overwrite.lower() != "y":
                return None
            break
    
    offer = {
        "id": product_id,
        "category": category,
        "productName": product_name,
        "brand": brand,
        "retailer": retailer,
        "price": price,
        "currency": "CAD",
        "url": url,
        "source": "manual",
        "verifiedAt": datetime.now(timezone.utc).isoformat()
    }
    
    print("\n✓ Offer created successfully!")
    print(f"  Category: {category}")
    print(f"  Product: {product_name[:50]}...")
    print(f"  Retailer: {retailer}")
    print(f"  Price: ${price:.2f} CAD")
    
    return offer


def interactive_mode():
    """Run the tool in interactive mode."""
    print_header()
    
    # Load existing products
    print("Loading existing products...")
    existing_products = load_existing_products(PRODUCTS_FILE)
    print(f"Loaded {len(existing_products)} existing offers.\n")
    
    offers_added = []
    
    while True:
        offer = enter_single_offer(existing_products)
        if offer:
            offers_added.append(offer)
            existing_products.append(offer)
            print(f"\nTotal offers entered this session: {len(offers_added)}")
        
        print("\n" + "-" * 40)
        another = get_input("Enter another offer? (y/n)", default="n")
        if another.lower() != "y":
            break
    
    if not offers_added:
        print("\nNo offers were entered. Exiting.")
        return
    
    # Save updated products
    print("\n" + "=" * 60)
    print("SAVING CHANGES")
    print("=" * 60)
    
    save_products(existing_products, PRODUCTS_FILE)
    
    # Compute winners
    print("\nRecalculating category winners...")
    winners = compute_category_winners(existing_products)
    
    # Show summary
    print("\nCategory Winners Summary:")
    print("-" * 60)
    for cat in sorted(winners.keys()):
        w = winners[cat]
        source_marker = "★" if w.get("source") == "manual" else " "
        print(f"  {source_marker} {cat}: ${w['price']} @ {w['retailer']}")
    
    # Generate ram-prices.json
    generate_ram_prices_json(winners, PRICES_FILE)
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"Offers added: {len(offers_added)}")
    print(f"Categories with winners: {len(winners)}")
    print(f"Files updated:")
    print(f"  - {PRODUCTS_FILE}")
    print(f"  - {PRICES_FILE}")
    print("\n★ symbol indicates categories where manual entry provided the best price.")
    print("\nTo deploy changes to your website, commit and push to GitHub:")
    print("  git add market-products.json ram-prices.json")
    print("  git commit -m 'Update market prices with manual entries'")
    print("  git push")


def batch_mode(batch_file: str):
    """Process offers from a JSON file."""
    print_header()
    print(f"Processing batch file: {batch_file}")
    
    if not os.path.exists(batch_file):
        print(f"Error: File not found: {batch_file}")
        sys.exit(1)
    
    try:
        with open(batch_file, 'r') as f:
            batch_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in batch file: {e}")
        sys.exit(1)
    
    # Handle both list and dict formats
    if isinstance(batch_data, list):
        new_offers = batch_data
    elif isinstance(batch_data, dict) and "offers" in batch_data:
        new_offers = batch_data["offers"]
    else:
        print("Error: Batch file must contain a list of offers or {'offers': [...]}")
        sys.exit(1)
    
    print(f"Found {len(new_offers)} offers to process.\n")
    
    # Load existing products
    existing_products = load_existing_products(PRODUCTS_FILE)
    existing_ids = {p.get("id") for p in existing_products}
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for offer in new_offers:
        # Validate required fields
        required = ["category", "productName", "retailer", "price"]
        missing = [f for f in required if not offer.get(f)]
        if missing:
            print(f"⚠ Skipping offer - missing fields: {missing}")
            skipped_count += 1
            continue
        
        # Normalize retailer
        offer["retailer"] = normalize_retailer_name(offer.get("retailer", ""))
        
        # Generate ID if not present
        if "id" not in offer:
            # Extract capacity from category
            parts = offer["category"].split("-")
            capacity = int(parts[-1]) if parts[-1].isdigit() else 0
            product_type = "ssd" if offer["category"].startswith("ssd") else "ram"
            offer["id"] = generate_product_id(
                offer["productName"],
                offer["retailer"],
                capacity,
                product_type
            )
        
        # Set defaults
        offer.setdefault("currency", "CAD")
        offer.setdefault("source", "manual")
        offer.setdefault("verifiedAt", datetime.now(timezone.utc).isoformat())
        
        # Check for existing
        if offer["id"] in existing_ids:
            # Update existing
            for i, existing in enumerate(existing_products):
                if existing.get("id") == offer["id"]:
                    existing_products[i].update(offer)
                    updated_count += 1
                    print(f"✓ Updated: {offer['productName'][:40]}... @ {offer['retailer']}")
                    break
        else:
            existing_products.append(offer)
            existing_ids.add(offer["id"])
            added_count += 1
            print(f"✓ Added: {offer['productName'][:40]}... @ {offer['retailer']} - ${offer['price']}")
    
    if added_count == 0 and updated_count == 0:
        print("\nNo offers were added or updated.")
        return
    
    # Save
    print("\n" + "=" * 60)
    print("SAVING CHANGES")
    print("=" * 60)
    
    save_products(existing_products, PRODUCTS_FILE)
    
    # Compute winners
    winners = compute_category_winners(existing_products)
    generate_ram_prices_json(winners, PRICES_FILE)
    
    print(f"\nSummary:")
    print(f"  Added: {added_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total tracked: {len(existing_products)}")
    print(f"  Categories with winners: {len(winners)}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch" or sys.argv[1] == "-b":
            if len(sys.argv) < 3:
                print("Usage: python manual_entry.py --batch <input.json>")
                sys.exit(1)
            batch_mode(sys.argv[2])
        elif sys.argv[1] in ["--help", "-h"]:
            print(__doc__)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information.")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
