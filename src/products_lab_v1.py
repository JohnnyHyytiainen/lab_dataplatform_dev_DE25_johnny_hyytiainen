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
print(f"{df_clean.head(20)} \n\n")

# 3. Flagga problem
# Se över och hitta saknade värden med isna() method
df['flag_missing_currency'] = df['currency'].isna()
# Se över och flagga för "luxury items", konstanten i min config avgör var den gränsen går.
df['flag_luxury_items'] = df['price'] > THRESHOLD
df['flag_free_items'] = df['price'] == 0
df_missing_curr = df['flag_missing_currency']
df_luxury_items = df['flag_luxury_items']
df_free_items = df['flag_free_items']

# Prints för att dubbelkolla all data
print(f"{df_missing_curr.describe()}\n\n")
print(f"{df_free_items.describe()}\n\n")
print(f"{df_luxury_items.describe()}\n\n")


# 4. Avvisa alla omöjlig data
df_rejected = df[df['price'] < 0]


# 5. Generera sammanfattning
analytics = {
    'avg_price': df['price'].mean(),
    'median_price': df['price'].median(),
    'total_products': len(df),
    'missing_price': df['price'].isna().sum()
}

# 6. Spara i rätt folder
output_dir = Path("data/clean")
output_dir.mkdir(parents=True, exist_ok=True)

pd.DataFrame([analytics]).to_csv(output_dir / "analytics_summary.csv", index=False)

# Bonus
top10_expensive = df.nlargest(10, 'price')
top10_expensive.to_csv(output_dir / "price_analysis.csv", index=False)