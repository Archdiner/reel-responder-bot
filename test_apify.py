#!/usr/bin/env python3
"""
Quick test script to verify your Apify API key works.
"""

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load environment variables
load_dotenv()

APIFY_KEY = os.getenv("APIFY_KEY")

if not APIFY_KEY:
    print("❌ Error: APIFY_KEY not found in .env file")
    print("Please add your Apify API key to .env")
    exit(1)

print("🔑 Testing Apify API key...")
print(f"   Key: {APIFY_KEY[:15]}...{APIFY_KEY[-4:]}")

try:
    client = ApifyClient(APIFY_KEY)
    
    # Test with a sample Instagram reel
    # This is a random public reel - replace with any Instagram reel URL
    test_reel_url = "https://www.instagram.com/p/C7xZQxMy8vT/"
    
    print(f"\n📹 Testing comment scraping on: {test_reel_url}")
    print("   (This may take 10-30 seconds...)\n")
    
    run_input = {
        "directUrls": [test_reel_url],
        "resultsLimit": 5,
    }
    
    run = client.actor("SbK00X0JYCPblD2wp").call(run_input=run_input)
    
    print("✅ Apify API key works!")
    print(f"   Run ID: {run['id']}")
    print(f"   Status: {run['status']}")
    
    # Get comments
    print("\n💬 Fetched comments:")
    count = 0
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        if count >= 3:
            break
        if 'text' in item:
            print(f"   {count + 1}. {item['text'][:80]}...")
            count += 1
    
    if count == 0:
        print("   (No comments found - this is normal for some reels)")
    
    print("\n🎉 Success! Your Apify setup is ready to use.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. No credits remaining on your Apify account")
    print("  3. Network connection issue")
    print("\nCheck your Apify dashboard: https://console.apify.com/")
