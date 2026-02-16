import pandas as pd
from pathlib import Path
from datetime import datetime
# Kod: Engelska
# Kommentarer: Svenska


# === Config v2 ===
FILEPATH = Path("data/raw/products.csv")
OUTPUT_DIR = Path("data/clean_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THRESHOLD_LUXURY = 5000
# Pris analyser