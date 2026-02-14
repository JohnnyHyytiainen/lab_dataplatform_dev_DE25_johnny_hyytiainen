import pandas as pd
from pathlib import Path

# Config
filepath = Path("data/raw/products.csv")
THRESHOLD = 15000

# 1. Read
# Eftersom att CSV fil innehåller ';' som separator och inte ',' använder jag character/regex pattern för att se ';' som delimiter.
df = pd.read_csv(filepath, sep=';')

print(f"{df.head(20)} \n\n")
# 2. Transform (clean, validate)
# Konvertera till numeric först för att undvika issues med strängar och jämförelser.
df['price'] = pd.to_numeric(df['price'], errors='coerce')
# Tar bort rader där priser ger NaN värde(inte existerar) med 'dropna' method och 'subset' som parameter
df_clean = df.dropna(subset=['price'])
df_clean = df_clean[df_clean['price'] > 0]  # Remove invalid
print(df_clean.head(20))

