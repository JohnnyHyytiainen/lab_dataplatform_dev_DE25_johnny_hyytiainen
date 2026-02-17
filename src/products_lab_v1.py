import pandas as pd
from pathlib import Path
# Kod: Engelska
# Kommentarer: Svenska
"""
Lab 1: Data Ingestion & Transformation
Student: Johnny Hyytiäinen
Course: Dataplatform Development
Files: I chose to separate my files with expensive items and my deviant items in two separate files for readability
"""
# Config
FILEPATH = Path("data/raw/products.csv")
OUTPUT_DIR = Path("data/clean")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THRESHOLD_LUXURY = 5000
# Pris analyser
def create_price_analysis(df_valid, output_dir):
    """BONUS: Generate price analysis with top 10 expensive and deviant products."""
    # Top 10 dyraste
    top10_expensive = df_valid.nlargest(10, 'price_numeric')[['name', 'price_numeric', 'currency']].copy()
    top10_expensive['category'] = 'expensive'
    
    # Top 10 mest avvikelser (använder mig av z-score)
    mean_price = df_valid['price_numeric'].mean()
    std_price = df_valid['price_numeric'].std()
    df_valid_copy = df_valid.copy()
    df_valid_copy['price_deviation'] = abs((df_valid_copy['price_numeric'] - mean_price) / std_price)
    top10_deviant = df_valid_copy.nlargest(10, 'price_deviation')[['name', 'price_numeric', 'price_deviation']].copy()
    top10_deviant['category'] = 'deviant'
    
    # Spara
    top10_expensive.to_csv(output_dir / "price_analysis_expensive_v1.csv", index=False)
    top10_deviant.to_csv(output_dir / "price_analysis_deviant_v1.csv", index=False)
    print("   - Saved price_analysis files (BONUS)")

def run_pipeline():
    print("Starting ETL Pipeline")
    # Sanity check för att se om filen existerar
    if not FILEPATH.exists():
        print(f"File not found: {FILEPATH}")
        return
    
    # EXTRACT (E)
    df = pd.read_csv(FILEPATH, sep=';', dtype=str)
    print(f"Loaded {len(df)} rows")

    # TRANSFORM (T)
    # Tvätta kolumn namn
    df.columns = df.columns.str.strip().str.lower()
    # Tvätta textfält
    text_cols = ['name', 'currency', 'price', 'created_at']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()
    # Standardisera/Normalisera text. Namn som title och currency i caps
    if 'name' in df.columns:
        df['name'] = df['name'].str.title()
    if 'currency' in df.columns:
        df['currency'] = df['currency'].str.upper()
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].str.strip().str.replace("/", "-", regex=False)
    
    # Fixar till format på datum
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['created_at_str'] = df['created_at'].dt.strftime('%Y-%m-%d')
    
    # Tvätta priserna (hanterar "free", "not_available")
    df['price_clean'] = df['price'].str.lower()
    df['price_clean'] = df['price_clean'].replace({
        'free': '0', 
        'not_available': None, 
        '': None
    })
    df['price_numeric'] = pd.to_numeric(df['price_clean'], errors='coerce')
    
    # FLAGGA för problem
    df['flag_missing_price'] = df['price_numeric'].isna()
    df['flag_negative_price'] = df['price_numeric'] < 0
    df['flag_is_free'] = df['price_numeric'] == 0
    df['flag_luxury'] = df['price_numeric'] > THRESHOLD_LUXURY
    df['flag_missing_currency'] = df['currency'].isna() | (df['currency'] == '')  # Added!
    df['flag_missing_id'] = df['id'].isna() | (df['id'] == '') # Added!
    
    # REJECT'A omöjliga värden
    # Nu åker man ut om man saknar pris, har negativt pris, ELLER saknar ID
    rejection_mask = (
        df['flag_missing_price'] | 
        df['flag_negative_price'] | 
        df['flag_missing_id']
    )

    df_rejected = df[rejection_mask].copy()
    df_valid = df[~rejection_mask].copy()
    
    print(f"Valid rows: {len(df_valid)}")
    print(f"Rejected rows: {len(df_rejected)}")
    
    # LOAD (L) - Sparar outputs
    df_valid.to_csv(OUTPUT_DIR / "cleaned_products_v1.csv", index=False)
    df_rejected.to_csv(OUTPUT_DIR / "rejected_products_v1.csv", index=False)
    
    # Analytics sammanfattning
    summary = {
        'avg_price': df_valid['price_numeric'].mean(),
        'median_price': df_valid['price_numeric'].median(),
        'total_products': len(df_valid),
        'total_rejected': len(df_rejected),
        'missing_currency_count': df_valid['flag_missing_currency'].sum(),
        'missing_price_count': df['flag_missing_price'].sum()
    }
    pd.DataFrame([summary]).to_csv(OUTPUT_DIR / "analytics_summary_v1.csv", index=False)
    print("Saved analytics_summary_v1.csv")
    
    # BONUS: Pris analys
    create_price_analysis(df_valid, OUTPUT_DIR)
    
    print(f"\n -  Summary:")
    print(f"   - Avg price: {summary['avg_price']:.2f}")
    print(f"   - Median price: {summary['median_price']:.2f}")
    print(f"   - Luxury items: (>{THRESHOLD_LUXURY}): {df_valid['flag_luxury'].sum()}")
    print(f"   - Free items: {df_valid['flag_is_free'].sum()}")
    print(f"   - Missing currency: {summary['missing_currency_count']}")
    print(f"   - Missing prices: {summary['missing_price_count']}")
    print("\n Pipeline complete!")

if __name__ == "__main__":
    run_pipeline()