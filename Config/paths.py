from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parents[1]

# Data paths
DATA_DIR = BASE_DIR / "data"
RAW_JSON = DATA_DIR / "movies_raw.json"
TRANSFORMED_CSV = DATA_DIR / "movies_transformed.csv"
KPI_CSV = DATA_DIR / "movie_kpis.csv"

# Log paths
LOG_DIR = BASE_DIR / "Logs"
FETCH_LOG = LOG_DIR / "fetch_movies.log"
TRANSFORM_LOG = LOG_DIR / "transform_movies.log"
KPI_LOG = LOG_DIR / "kpi_movies.log"
VIS_LOG = LOG_DIR / "visualization.log"
