import os
from dotenv import load_dotenv

load_dotenv()

# Helper to get multiple keys
def get_multiple_keys(prefix):
    keys = []
    # Primary key
    primary = os.getenv(prefix)
    if primary:
        keys.append(primary)
    
    # Secondary keys (1 to 5)
    for i in range(2, 6):
        key = os.getenv(f"{prefix}_{i}")
        if key:
            keys.append(key)
    return keys

# Configuration Settings
OPENAI_API_KEYS = get_multiple_keys("OPENAI_API_KEY")
GEMINI_API_KEYS = get_multiple_keys("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

DEFAULT_MODEL = "gemini-2.5-flash-lite"

RESEARCH_DEPTH_DEFAULT = "deep"

MAX_CONCURRENT_CRAWLS = 5

# Rate Limiting
REQUEST_DELAY = 1.0 # Seconds between requests
MAX_RETRIES = 3
