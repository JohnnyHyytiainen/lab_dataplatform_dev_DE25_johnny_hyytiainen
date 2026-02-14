# Theory:


### **KUN09: typiska komponenter och teknologier i en dataplattform**

**Ingest Layer:**
- Pandas read_csv() läser från products.csv.
- Hanterar olika separatorer (';').
- I production: APIs, streaming (Kafka), batch (Airflow).

**Storage Layer:**
- CSV files (enkelt för lab).
- I mina egna pågående eller klara projekt, PostgreSQL (golden layer), DuckDB, Sqlite3.
- I production: Data lakes (S3), warehouses (Snowflake).

**Transform Layer:**
- Pandas operationer (clean text, fix dates, flag issues).
- I production: Spark, DBT, Airflow pipelines, custom Python pipelines.
- I pågående eller färdiga egna projekt: Keyword taxonomy matching, custom Pipeline.

**Access Layer:**
- Output CSVs för analys.
- I production: BI tools (Power BI), APIs (FastAPI t.ex), dashboards.

**Orchestration/scheduling:**
- Schemalägger när pipelines körs.
- I production: AirFlow, Prefect, Dagster.
- I lab: Manuell körning `python src/products_lab_v1.py`

**Exempel från egna projekt:**
- Ingest: JSONL files (4.3M rows) eller syntetiskt dataset(100k rows för benchmarking)
- Storage: PostgreSQL (de-normalized for BI dashboard)
- Transform: Keyword taxonomy matching
- Access: Power BI team consumption


### **KUN10: ETL Pipeline**

**Extract:**
- Läser rådata från products.csv med Pandas
- Validerar att filen finns
- Hanterar olika datatyper (dtype=str först)

**Transform:**
- Text cleaning (strip whitespace, standardize case)
- Datum standardisering (olika format --> YYYY-MM-DD)
- Pris hantering ("free" --> 0, "not_available" --> null)
- Flaggar data quality issues (missing values, negative, luxury, free)
- Separerar valid vs rejected data

**Load:**
- cleaned_products.csv (processad data)
- rejected_products.csv (invalid data)
- analytics_summary.csv (aggregerad statistik)
- price_analysis_deviant.csv (avvikelser) <-- Har valt att separera dyra items och avvikelser pga enklare att läsa.
- price_analysis_expensive.csv (luxury items) <-- Har valt att separera dyra items och avvikelser pga enklare att läsa.


### **F10: Python olika dataformat**

CSV (denna lab):
- Pandas: read_csv(), to_csv()
- Hanterade olika separatorer (';')

I mina andra projekt:
- JSON/JSONL (AF Pipeline): json.load(), json.dumps()
- PostgreSQL (YrkesCo + AF): psycopg3, SQLAlchemy
- JSON/JSONL/CSV (Space_bridge pipeline): json.load(), json.dumps()
- Excel: Pandas read_excel(), to_excel()

**Teknologier att hålla koll på för Programmering inom Dataplatform Development:**

- **Pandas (dataframes):**
    - Ett bibliotek för att hantera strukturerad (tabulär) data i minnet, likt en Excel tabell fast för kod.
    - Viktigt koncept: DataFrames och Series. Möjliggör vektoriserade operationer (beräkningar på hela kolumner samtidigt) vilket är mycket snabbare än Python loopar.

- **Pydantic (Data validation + parsing):**
    - Till skillnad från vanliga Python klasser (som litar på att du skickar rätt data) så tvingar Pydantic datan att följa reglerna.
    - Runtime Enforcement: Om jag säger t.ex `id: int` och skickar in strängen `"123"`, konverterar Pydantic det automatiskt till ett nummer. Skickar jag `"hej"`, kastar den ett error direkt. Det garanterar datakvalitet vid ingestion. 

- **SQLAlchemy (ORM)**
    - Fungerar som en "översättare" mellan Python-objekt och SQL-tabeller.

    - Istället för att skriva rå SQL (`INSERT INTO...`), jobbar jag med Python-klasser `user.save()`. Det gör koden databas-oberoende(database agnostic) det vill säga, det är lätt att byta från SQLite till Postgres.

    - **Exempel** kring ORM. Om du använder dig utav t.ex SQLAlchemy och skriver python skript så ser ORM'en på min `Connection String` i min `.env` och ser om det t.ex står `postgresql://` så kommer den översätta min Python kod till PostgreSQL dialekt. Om jag vid nästa tillfälle vill experimentera och testa t.ex `sqlite:///` så kommer det samma Python kod till `SQLite` dialekt.

    - **Varning kring ORM** ORM är bra då det är portabelt och framförallt **Säkert** (ORM hanterar automatiskt saker så som SQL-injection). **MEN** trots att det är fantastiskt att använda för t.ex applikationer(Hantera användare, orders och produkter) så är det EJ optimalt vid stora dataset. Har du STORA dataset(tänk 1 mil rows +) kommer du stöta på problem. Detta för att ORM skapar ett nytt Python Object för varje rad.

- **Parquet (columnar storage)**
    - Lagrar data kolumn för kolumn istället för rad för rad (som CSV).

    - Effektivt för analys (OLAP) då man ofta bara vill läsa specifika kolumner, samt tar mindre plats pga bättre komprimering.

    - Användningsområden: Big data, Data lakes.


- **JSON och JSONL**
    - Likt varningen och förklaringen kring ORM ovan kan jag även jämföra JSON och JSONL här med. 
    - **Exempel:** Säg att du har byggt en pipeline i Python och har som uppgift att Extrahera rå data(En raw JSON fil på 12gb), Transformera den datan och sedan Ladda den datan för analys. Här måste du vara väldigt noga med hur du går till väga för att undvika problem om du ska processa den JSON filen på din laptop med 8gb RAM.`

- **JSON**
    - Anledningen till det är för att vanlig JSON är "all or nothing". En ren JSON fil är *ett enda stort objekt* (inneslutet i [......]). För att din dator ska "förstå" filen måste den hitta start och slut. Alltså -->[<-- Start och Slut -->]<--. **Problemet som KOMMER uppstå** är då att om filen är stor så måste Python läsa in hela 12gb i minnet innan pipen ens kan ge dig första raden. Resultatet?
        - Ett `MemoryError`(KRASCH) på din laptop som enbart har 8gb RAM.
- **JSONL(NDJSON)**
    - Om du däremot har alternativet att jobba med exakt samma data fast i JSONL(Line delimited) format där VARJE rad är sitt eget objekt så kommer du undvika `MemoryError` och krasch som JSON filen orsakar. Detta för att varje rad i en JSONL fil ses som sitt egna objekt. Fördelen med det är att Python läser rad 1, processerar den, **glömmer den(frigör minnet)** och går vidare till rad 2... etc ... etc...
        - Resultatet blir då att du kan processa en 10gb, 37gb, 69gb eller en 835gb stor JSONL fil på en laptop med väldigt lite RAM-minne(8gb i detta exempel). Användningen av minnet är lågt.

    - Det här är anledningen till varför JSONL är "kung" i Big Data världen jämfört med JSON. Det är därför JSONL syns överallt i form av t.ex Loggar eller BigQuery exports. **JSONL är att föredra ALLA dagar i veckan för data pipelines**


- **Avro/Protocol Buffers (binary formats):**
    - Kompaktare än JSON (binary vs text)
    - Schema evolution (kan ändra struktur över tid)
    - Användningsområde: Kafka streams, gRPC APIs
    - Trade off: Svårare att debugga (ej human-readable)