# Programming in Dataplatform Development
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-success)

**Lab 1 for the Dataplatform Development course in the Data Engineer 2025 program at STI.**  


## About The Project
This repository showcases an ETL (Extract, Transform, Load) pipeline built in Python. The goal is to ingest raw, "dirty" product data (CSV), clean and validate it using Pandas, and load the high-quality data into a PostgreSQL Data Warehouse.

The project simulates a real-world scenario where data integrity is compromised (mixed formats, missing IDs, invalid prices) and demonstrates how to build a resilient pipeline to handle these edge cases.


---

## Goals & Objectives
- ETL Implementation: Build a complete pipeline from extraction to loading.

- Data Quality: Handle missing values, standardize date formats (ISO 8601), and normalize text data.

- Validation Logic: Implement business logic to flag and reject invalid data (negative prices, missing primary keys).

- Infrastructure: Use Docker to containerize the database layer.

- Analytics: Generate summary statistics and identify price outliers (Z-score analysis).

## Key Features
**Architecture**
- v1 Pipeline (MVP): A file-based pipeline that reads raw CSVs, cleans them, and outputs validated CSV files + analytics summaries.

- v2 Pipeline (Production-Grade): An advanced pipeline that integrates with PostgreSQL.
    - Ingestion Timestamps: Tracks Event Time (created_at) vs System Time (ingested_at).
    - Database Loading: Uses SQLAlchemy to push cleaned data to a "Gold Layer" and rejected data to an "Audit Layer".

**Advanced Data Cleaning**
- Strict Typing: Handles mixed data types and coercion safely.

- Rejection Logic: Automatically separates valid data from rejected data based on configured rules (ex, `Missing ID`, `Negative Price`)

- Format Standardization: Converts various date formats (ex `2024/02/15`) to standard `YYYY-MM-DD`.

**Analytics**
- Price Analysis: Identifies top 10 most expensive items.
- Outlier Detection: Calculates Z-scores to find products with statistically significant price deviations.

## Tech Stack
- **Language:** `Python 3.12`
- **Data Manipulation:** `Pandas`, `NumPy`
- **Database:** `PostgreSQL 16 Alpine`
- **Infrastructure:** `Docker & Docker Compose`
- **ORM/Connector:** `SQLAlchemy`, `Psycoph`


## Quick Start
**Prerequisites:** 
- Docker Desktop installed and running.
- Python 3.10+ installed.
- *optional* uv for fast package management (Recommended)

**Start the environment:**
- `uv sync`
- `docker-compose up -d` to start spin up your docker container
- `uv run src/products_lab_v2.py` **OR**
    - `python src/products_lab_v2.py` if you dont use uv and are using standard Python commands.
- [click here for a quick step by step guide for docker and ingesting data to PostgreSQL DB](docs/docker_runbook.md)


[Click Here for a step by step guide] [Or click here for the commands needed to run docker]
---

## Repository structure

```text
.
├── data/
│   ├── raw/                     # Original input files (products.csv)
│   ├── clean/                   # Output from v1 pipeline (CSV)
│   └── clean_v2/                # Output from v2 pipeline (CSV + Analytics)
│
├── docs/                        # Documentation
│   ├── DE_25_Lab1.pdf           # Lab Requirements
│   ├── theory_answers.md        # Answers to theoretical questions (KUN9, KUN10)
│   ├── notes.md                 # Academic references
│   ├── docker_runbook.md        # Quick setup with run commands for docker and Pgadmin4
│   └── visuals/                 # Screenshots with dirty prices, clean prices and end result output
│      
│
├── src/
│   ├── products_lab_v1.py       # MVP Pipeline (File -> File)
│   └── products_lab_v2.py       # Advanced Pipeline (File -> DB)
│
├── docker-compose.yml           # PostgreSQL container configuration
├── README.md                    # Project documentation
└── pyproject.toml               # Dependencies
```

### [Sources - for full Academic transparency and Academic integrity click here](docs/notes.md)


