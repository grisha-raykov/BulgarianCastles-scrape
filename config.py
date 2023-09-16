from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Logging configuration
LOG_FILE = "castle_scraper.log"
LOG_LEVEL = "ERROR"

# Scraping configuration
BASE_URL = "https://www.bulgariancastles.com/category/severozapadna-b-ya/"
MAX_WORKERS = 10