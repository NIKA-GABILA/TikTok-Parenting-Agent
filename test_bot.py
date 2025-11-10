"""
Test script to verify all components work
Run this before deploying to Render
"""
import os
from dotenv import load_dotenv

print("🧪 Testing TikTok Parenting Agent Components...\n")

# Load environment
load_dotenv()

# Test 1: Environment Variables
print("1️⃣ Testing Environment Variables...")
required_vars = [
    'ANTHROPIC_API_KEY',
    'TELEGRAM_BOT_TOKEN'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)
        print(f"   ❌ {var} - MISSING")
    else:
        print(f"   ✅ {var} - OK")

if missing:
    print(f"\n❌ Missing variables: {', '.join(missing)}")
    print("შექმენი .env ფაილი .env.example-ის მაგალითით!\n")
    exit(1)

# Test 2: Dependencies
print("\n2️⃣ Testing Dependencies...")
try:
    import anthropic
    print("   ✅ anthropic - OK")
except ImportError:
    print("   ❌ anthropic - MISSING")
    print("   გაუშვი: pip install anthropic")

try:
    import telegram
    print("   ✅ python-telegram-bot - OK")
except ImportError:
    print("   ❌ python-telegram-bot - MISSING")
    print("   გაუშვი: pip install python-telegram-bot")

try:
    from PIL import Image
    print("   ✅ Pillow - OK")
except ImportError:
    print("   ❌ Pillow - MISSING")
    print("   გაუშვი: pip install Pillow")

try:
    import requests
    print("   ✅ requests - OK")
except ImportError:
    print("   ❌ requests - MISSING")

try:
    from bs4 import BeautifulSoup
    print("   ✅ beautifulsoup4 - OK")
except ImportError:
    print("   ❌ beautifulsoup4 - MISSING")

# Test 3: Module Imports
print("\n3️⃣ Testing Module Imports...")
try:
    import config
    print("   ✅ config.py - OK")
except Exception as e:
    print(f"   ❌ config.py - ERROR: {e}")

try:
    from content_creator import ContentCreator
    print("   ✅ content_creator.py - OK")
except Exception as e:
    print(f"   ❌ content_creator.py - ERROR: {e}")

try:
    from design_generator import DesignGenerator
    print("   ✅ design_generator.py - OK")
except Exception as e:
    print(f"   ❌ design_generator.py - ERROR: {e}")

try:
    from news_tracker import NewsTracker
    print("   ✅ news_tracker.py - OK")
except Exception as e:
    print(f"   ❌ news_tracker.py - ERROR: {e}")

# Test 4: Claude API Connection
print("\n4️⃣ Testing Claude API Connection...")
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Simple test
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        messages=[{"role": "user", "content": "გამარჯობა"}]
    )
    
    print(f"   ✅ Claude API - OK")
    print(f"   Response: {message.content[0].text[:50]}...")
except Exception as e:
    print(f"   ❌ Claude API - ERROR: {e}")

# Test 5: Image Generation
print("\n5️⃣ Testing Image Generation...")
try:
    from design_generator import DesignGenerator
    
    test_content = {
        'title': 'ტესტი',
        'main_text': 'ეს არის ტესტური ტექსტი',
        'caption': 'ტესტური caption',
        'hashtags': ['#test']
    }
    
    generator = DesignGenerator()
    img = generator.generate_image(test_content, style='minimalist')
    
    # Try to save
    os.makedirs('data/generated', exist_ok=True)
    filepath = generator.save_image(img, 'test_image.png')
    
    print(f"   ✅ Image Generation - OK")
    print(f"   Saved to: {filepath}")
except Exception as e:
    print(f"   ❌ Image Generation - ERROR: {e}")

print("\n" + "="*50)
print("🎉 ტესტირება დასრულებულია!")
print("="*50)

print("\nთუ ყველა ტესტი ✅ არის:")
print("1. შეგიძლია გაუშვა: python bot.py")
print("2. ან deploy გააკეთო Render-ზე")
print("\nთუ რამე ❌ არის:")
print("1. დააყენე შესაბამისი packages: pip install -r requirements.txt")
print("2. შეამოწმე .env ფაილი")
print("3. კიდევ გაუშვი: python test_bot.py")
