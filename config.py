"""
Configuration file for TikTok Parenting Agent
"""
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Timezone
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tbilisi')

# Generation Schedule
GENERATION_HOUR = int(os.getenv('GENERATION_HOUR', 13))
GENERATION_MINUTE = int(os.getenv('GENERATION_MINUTE', 0))

# News checking
NEWS_CHECK_DAYS = [int(d) for d in os.getenv('NEWS_CHECK_DAYS', '0,3').split(',')]

# Learning phase
LEARNING_PHASE_DAYS = int(os.getenv('LEARNING_PHASE_DAYS', 14))
LEARNING_VARIANTS = int(os.getenv('LEARNING_VARIANTS', 6))
NORMAL_VARIANTS = int(os.getenv('NORMAL_VARIANTS', 3))

# Content settings
BRANDING = "Nika Gablishvili - Psychologist | ნიკა გაბლიშვილი - ფსიქოკონსულტანტი"

# Age distribution
AGE_DISTRIBUTION = {
    'preschool': 0.8,  # 3-7 წელი
    'school': 0.2      # 6-12 წელი
}

# Format distribution
FORMAT_DISTRIBUTION = {
    'myth_vs_reality': 0.40,
    'self_assessment': 0.25,
    'practical_scenario': 0.20,
    'quick_tip': 0.10,
    'mini_story': 0.05
}

# Tone distribution
TONE_DISTRIBUTION = {
    'friendly': 0.80,
    'professional': 0.08,
    'practical': 0.07,
    'storytelling': 0.05
}

# Visual style distribution
VISUAL_STYLE_DISTRIBUTION = {
    'minimalist': 0.25,
    'warm_cozy': 0.25,
    'infographic': 0.20,
    'gradient': 0.20,
    'story_card': 0.10
}

# Colors palette
COLOR_PALETTES = {
    'minimalist': ['#FFFFFF', '#2C3E50', '#3498DB'],
    'warm_cozy': ['#FFF9F0', '#FFE5D9', '#F4A261', '#E76F51'],
    'infographic': ['#F8F9FA', '#4A90E2', '#50C878', '#FF6B6B'],
    'gradient': ['#667EEA', '#764BA2', '#F093FB', '#4FACFE'],
    'story_card': ['#FFF5E1', '#FFD3B5', '#FFAA85', '#FF8C5A']
}

# Image settings
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1920
IMAGE_FORMAT = 'PNG'
IMAGE_QUALITY = 95

# Georgian fonts (system fonts on most Linux servers)
GEORGIAN_FONTS = [
    'Noto Sans Georgian',
    'DejaVu Sans',
    'Liberation Sans'
]

# News sources (Georgian parenting & education sites)
NEWS_SOURCES = [
    'https://www.interpressnews.ge/',
    'https://www.netgazeti.ge/',
    'https://www.formula.ge/',
    'https://on.ge/',
]

# Data storage paths
DATA_DIR = 'data'
FEEDBACK_FILE = f'{DATA_DIR}/feedback.json'
STATS_FILE = f'{DATA_DIR}/stats.json'
GENERATED_DIR = f'{DATA_DIR}/generated'
LEARNING_FILE = f'{DATA_DIR}/learning_preferences.json'

# Hashtags
DEFAULT_HASHTAGS = [
    '#მშობლობა',
    '#ფსიქოლოგია',
    '#მშობლებისთვის',
    '#ბავშვები',
    '#სკოლამდელი',
    '#აღზრდა',
    '#მშობლისრჩევები',
    '#ქართულიმშობლობა'
]

def get_start_date():
    """Get the start date for tracking learning phase"""
    if not os.path.exists(STATS_FILE):
        return datetime.now()
    
    import json
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            stats = json.load(f)
            return datetime.fromisoformat(stats.get('start_date', datetime.now().isoformat()))
    except:
        return datetime.now()

def is_learning_phase():
    """Check if we're still in the learning phase"""
    start_date = get_start_date()
    days_running = (datetime.now() - start_date).days
    return days_running < LEARNING_PHASE_DAYS

def get_variants_count():
    """Get number of variants to generate based on phase"""
    return LEARNING_VARIANTS if is_learning_phase() else NORMAL_VARIANTS
