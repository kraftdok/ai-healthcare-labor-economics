"""
Configuration for AI Clinical Intermediary Study.

API keys loaded from .env file. Study parameters defined here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional: for multi-model comparison

# --- Model ---
MODEL_ID = "claude-opus-4-7"

# --- Study Parameters ---
REPETITIONS = 5              # Repetitions per prompt combination (5 × 48 = 240 total)
PILOT_REPETITIONS = 1        # For quick pilot (1 × 48 = 48 total, ~$1)
RATE_LIMIT_DELAY = 0.3       # Seconds between API calls
MAX_TOKENS = 1024
TEMPERATURE = 1.0            # Default temperature for variability measurement

# --- Paths ---
RESULTS_DIR = "data/results"
FIGURES_DIR = "outputs/figures"
TABLES_DIR = "outputs/tables"
SUMMARY_DIR = "outputs"
