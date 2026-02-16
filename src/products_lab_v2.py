import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from datetime import datetime
# Kod: Engelska
# Kommentarer: Svenska


# === Config v2 ===
# Separat output för att ej skriva över v1
FILEPATH = Path("data/raw/products.csv")
OUTPUT_DIR = Path("data/clean_v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
THRESHOLD_LUXURY = 5000

# DB CONNECTION (Anpassad efter docker setup!)
# Format: postgresql+psycopg://user:password@host:port/dbname
# Generisk användare och password enbart för lab
DB_CONNECTION_STR = "postgresql+psycopg://postgres:password@localhost:5434/lab_db"

def save_to_warehouse(df, table_name, engine):
    """Save dataframe to database (Data Warehouse layer)."""
    try:
        print(f"Saving {len(df)} rows to DB table '{table_name}'...")
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Table '{table_name}' updated successfully!")
    except Exception as e:
        print(f"Database error: {e}")

# Pris analyser (BONUS)
def create_price_analysis(df_valid, output_dir):
    """BONUS: Generate price analysis with top 10 expensive and deviant products."""
    print("Generating price analysis...")
    
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
    top10_expensive.to_csv(OUTPUT_DIR / "price_analysis_expensive_v2.csv", index=False)
    top10_deviant.to_csv(OUTPUT_DIR / "price_analysis_deviant_v2.csv", index=False)
    print("   - Saved price_analysis files (BONUS)")


def run_pipeline_v2():
    print("Starting ETL pipeline v2 (DB edition)")

    if not FILEPATH.exists():
        print(f"File not found. Look over pathing: {FILEPATH}")
        return
    
    # === 1: EXTRACT ===
    df = pd.read_csv(FILEPATH, sep=';', dtype=str)
    print(f"Loaded {len(df)} rows of data")

    # === 2: TRANSFORM ===
    # Samma städning som i v1
    df.columns = df.columns.str.strip().str.lower()

    text_cols = ['name', 'currency', 'price', 'created_at']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()

    if 'name' in df.columns:
        df['name'] = df['name'].str.title()
    if 'currency' in df.columns:
        df['currency'] = df['currency'].str.upper()
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].str.strip().str.replace("/", "-", regex=False)

    # Fixa till datum format
    # Spara som string för CSV, men behåller datetime objekt för SQL
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

    # Prisfix
    df['price_clean'] = df['price'].str.lower()
    df['price_clean'] = df['price_clean'].replace({'free': '0', 'not_available': None, '': None})
    df['price_numeric'] = pd.to_numeric(df['price_clean'], errors='coerce')

    # === NYTT FÖR V2: Timestamps (ingestion time) ===
    # visar before och after med created_at(event time) + ingested_at(system time)
    df['ingested_at'] = datetime.now()

    # Flaggning
    df['flag_missing_price'] = df['price_numeric'].isna()
    df['flag_negative_price'] = df['price_numeric'] < 0
    df['flag_is_free'] = df['price_numeric'] == 0
    df['flag_luxury'] = df['price_numeric'] > THRESHOLD_LUXURY
    df['flag_missing_currency'] = df['currency'].isna() | (df['currency'] == '')
    df['flag_missing_id'] = df['id'].isna() | (df['id'] == '')

    # Filtrering
    rejection_mask = (
    df['flag_missing_price'] | 
    df['flag_negative_price'] | 
    df['flag_missing_id']  # <-- Ny regel!
)
    df_rejected = df[rejection_mask].copy()
    df_valid = df[~rejection_mask].copy()

    # === 3: LOAD (Filer + Databas) ===

    # Spara CSV(Access layer + backup)
    df_valid.to_csv(OUTPUT_DIR / "cleaned_products_v2.csv", index=False)
    df_rejected.to_csv(OUTPUT_DIR / "rejected_products_v2.csv", index=False)

    # Spara till Data Warehouse(PostgreSQL)
    print("\n Database Loading ")
    try:
        engine = create_engine(DB_CONNECTION_STR)

        with engine.connect() as conn:
            print("Connected to PostgreSQL!")

        # Spara valid data -> Gold Layer eller Warehouse
        save_to_warehouse(df_valid, "products_cleaned", engine)
        # Spara rejected data (Bra att ha all data jag har rört i pipelinen sparad)
        save_to_warehouse(df_rejected, "products_rejected", engine)

    except Exception as e:
        print(f"Could NOT connect to database. Is docker running? Error: {e}")
        print("Continuing with CSV only")

    # Analytics summar
    summary = {
        'avg_price': df_valid['price_numeric'].mean(),
        'median_price': df_valid['price_numeric'].median(),
        'total_products': len(df_valid),
        'total_rejected': len(df_rejected),
        'ingestion_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    pd.DataFrame([summary]).to_csv(OUTPUT_DIR / "analytics_summary_v2.csv", index=False)

    # === BONUS: PRISANALYS ===
    # Anropar pris analys funktionen
    create_price_analysis(df_valid, OUTPUT_DIR)

    print("\n Pipeline v2 Complete! Check data/clean_v2/ and your PgAdmin4.")
    
if __name__ == "__main__":
    run_pipeline_v2()