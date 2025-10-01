#!/usr/bin/env python3
"""
Quick test script to verify your OpenAI API key works.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("🔍 Checking .env file...")
print(f"   .env file loaded: {'✅' if load_dotenv() else '❌'}")

if not OPENAI_API_KEY:
    print("\n❌ Error: OPENAI_API_KEY not found in .env file")
    print("\n📝 Your .env file should look like:")
    print("   OPENAI_API_KEY=sk-proj-xxxxxxxxxx")
    print("\n💡 Make sure:")
    print("   1. You created a .env file in this directory")
    print("   2. It contains: OPENAI_API_KEY=your_actual_key")
    print("   3. No spaces around the = sign")
    print("   4. No quotes around the key")
    exit(1)

print(f"   Key found: {OPENAI_API_KEY[:20]}...{OPENAI_API_KEY[-4:]}")

print("\n🤖 Testing OpenAI API connection...")

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Make a simple test request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Say 'Hello! API is working!' in a fun way."}
        ],
        max_tokens=50
    )
    
    reply = response.choices[0].message.content
    
    print("✅ OpenAI API key is VALID and working!")
    print(f"\n🎉 Test response from GPT-4o-mini:")
    print(f"   {reply}")
    print(f"\n📊 Tokens used: {response.usage.total_tokens}")
    print("\n✨ Your bot is ready to run!")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ Error: {error_msg}")
    
    if "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
        print("\n💡 Your API key is invalid. Please check:")
        print("   1. Copy the ENTIRE key from https://platform.openai.com/api-keys")
        print("   2. It should start with 'sk-proj-' or 'sk-'")
        print("   3. Make sure there are no extra spaces")
    elif "insufficient_quota" in error_msg:
        print("\n💳 You've exceeded your OpenAI quota.")
        print("   Add credits at: https://platform.openai.com/account/billing")
    else:
        print("\n🔍 Check your API key at: https://platform.openai.com/api-keys")
