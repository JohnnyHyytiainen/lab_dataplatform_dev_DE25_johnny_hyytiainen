# lab_dataplatform_dev_DE25_johnny_hyytiainen
Lab for Programming in Dataplatform Development

# TODO: Update README.md

## Steps
- 1) `uv init` for virtual environment.

- 2) `uv add fastapi "uvicorn[standard]" pandas pydantic-settings lxml httpx sqlalchemy` for dependencies.

- 2.5) `uv add "psycopg[binary]" "psycopg[pool]"` for more dependencies.

- 3) `uv python pin 3.12` to lock python version to 3.12

- 4) `uv add --dev pytest ruff mypy black` to add ruff linter, mypy and and black formatter.

- 5) `uv run pytest` `uv run ruff check .` to test pytest and ruff.
