#!/usr/bin/env python3
"""
Fetch the complete hawramani.com narrator index via WordPress REST API.

Downloads all 135K narrator entries (id, name, slug, categories) and
62 source book categories. Stores locally so we never hit the API again.

Usage:
  uv run --with httpx python scripts/fetch_hawramani_index.py

Output:
  reference/hawramani-categories.json  — 62 source books
  reference/hawramani-index.json       — all narrator entries
"""

import asyncio
import json
import time
from pathlib import Path

import httpx

BASE_URL = "https://hadithtransmitters.hawramani.com/wp-json/wp/v2"
OUTPUT_DIR = Path("reference")
CATEGORIES_FILE = OUTPUT_DIR / "hawramani-categories.json"
INDEX_FILE = OUTPUT_DIR / "hawramani-index.json"
PER_PAGE = 100
MAX_CONCURRENT = 5  # be respectful
DELAY_BETWEEN_BATCHES = 1.0  # seconds between batches of concurrent requests


async def fetch_categories(client: httpx.AsyncClient) -> list[dict]:
    """Fetch all source book categories."""
    categories = []
    page = 1
    while True:
        resp = await client.get(
            f"{BASE_URL}/categories",
            params={"per_page": 100, "page": page},
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for cat in data:
            categories.append({
                "id": cat["id"],
                "name": cat["name"],
                "slug": cat["slug"],
                "count": cat["count"],
            })
        page += 1
    return categories


async def fetch_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    """Fetch one page of narrator entries."""
    resp = await client.get(
        f"{BASE_URL}/posts",
        params={"per_page": PER_PAGE, "page": page, "_fields": "id,title,slug,categories"},
    )
    if resp.status_code == 400:
        # Past the last page
        return []
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "id": post["id"],
            "name_arabic": post["title"]["rendered"],
            "slug": post["slug"],
            "categories": post["categories"],
        }
        for post in data
    ]


async def fetch_all_entries(client: httpx.AsyncClient, total_estimate: int = 135000) -> list[dict]:
    """Fetch all narrator entries with controlled concurrency."""
    total_pages = (total_estimate // PER_PAGE) + 10  # small buffer
    all_entries = []
    fetched_pages = 0

    for batch_start in range(1, total_pages + 1, MAX_CONCURRENT):
        batch_end = min(batch_start + MAX_CONCURRENT, total_pages + 1)
        tasks = [fetch_page(client, p) for p in range(batch_start, batch_end)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        empty_count = 0
        for result in results:
            if isinstance(result, Exception):
                print(f"  Error on page: {result}")
                continue
            if not result:
                empty_count += 1
                continue
            all_entries.extend(result)

        fetched_pages += len(tasks)
        if fetched_pages % 50 == 0 or empty_count > 0:
            print(f"  Pages fetched: {fetched_pages}, entries so far: {len(all_entries)}")

        # Stop if we got empty pages (past the end)
        if empty_count >= MAX_CONCURRENT:
            print(f"  Reached end at page ~{batch_start}")
            break

        await asyncio.sleep(DELAY_BETWEEN_BATCHES)

    return all_entries


async def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Categories
        print("Fetching categories (source books)...")
        categories = await fetch_categories(client)
        with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        print(f"  Saved {len(categories)} categories to {CATEGORIES_FILE}")

        # Get total count from categories
        total = sum(c["count"] for c in categories)
        print(f"\nFetching narrator entries (estimated {total:,})...")

        # Step 2: All entries
        start = time.time()
        entries = await fetch_all_entries(client, total)
        elapsed = time.time() - start

        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=None)  # compact

        size_mb = INDEX_FILE.stat().st_size / (1024 * 1024)
        print(f"\n  Saved {len(entries):,} entries to {INDEX_FILE}")
        print(f"  File size: {size_mb:.1f} MB")
        print(f"  Time: {elapsed:.0f}s")

        # Quick stats
        print(f"\n=== Summary ===")
        print(f"  Categories (source books): {len(categories)}")
        print(f"  Narrator entries: {len(entries):,}")
        print(f"  Files: {CATEGORIES_FILE}, {INDEX_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
