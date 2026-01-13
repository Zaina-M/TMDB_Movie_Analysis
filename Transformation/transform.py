import os
import logging
from xml.sax import handler
import pandas as pd
from Config.paths import TRANSFORM_LOG, RAW_JSON, TRANSFORMED_CSV



# Logging Configuration

import logging
import os
from Config.paths import TRANSFORM_LOG

# Ensure log directory exists
os.makedirs(TRANSFORM_LOG.parent, exist_ok=True)

# Create logger
logger = logging.getLogger("movie_transformer")
logger.setLevel(logging.INFO)

# IMPORTANT: avoid duplicate handlers (notebooks + reruns)
logger.handlers.clear()

# Create file handler
file_handler = logging.FileHandler(
    TRANSFORM_LOG,
    encoding="utf-8"
)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file_handler.setFormatter(formatter)

# Attach handler
logger.addHandler(file_handler)

# Stop propagation to root logger
logger.propagate = False





# Helper Functions


def extract_credits(credits: dict) -> pd.Series:
    # Extract cast, director, and crew stats from credits JSON.
    if not isinstance(credits, dict):
        credits = {}

    cast = credits.get("cast", [])
    crew = credits.get("crew", [])

    director = next(
        (p.get("name") for p in crew if p.get("job") == "Director"),
        None
    )

    return pd.Series({
        "cast": "|".join(
            p.get("name") for p in cast if isinstance(p, dict)
        ),
        "cast_size": len(cast),
        "director": director,
        "crew_size": len(crew)
    })


def flatten_named_json(value):
   #  Flattens:dict -> value['name']  to list[dict] -> 'name|name|name'
    
    if isinstance(value, dict):
        return value.get("name")
    if isinstance(value, list):
        return "|".join(
            item.get("name") for item in value if isinstance(item, dict)
        )
    return pd.NA



# Main Transform Function

def transform_movies(raw_movies: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting movie transformation")

    wanted_data = raw_movies.copy()
    logger.info(f"Initial rows: {len(wanted_data)}")

    
    # Credits Extraction 

    if "credits" in wanted_data.columns:
        logger.info("Extracting credits data")
        credits_df = wanted_data["credits"].apply(extract_credits)
        wanted_data = pd.concat([wanted_data, credits_df], axis=1)
    else:
        logger.warning("credits column missing")

    
    # Flatten JSON-like Columns
    json_columns = [
        "belongs_to_collection",
        "genres",
        "production_companies",
        "production_countries",
        "spoken_languages"
    ]

    for col in json_columns:
        if col in wanted_data.columns:
            logger.info(f"Flattening column: {col}")
            wanted_data[col] = wanted_data[col].apply(flatten_named_json)

    
    # Drop Irrelevant / Noisy Columns
    
    drop_columns = [
        "adult",
        "imdb_id",
        "original_title",
        "video",
        "homepage",
        "credits",
        "status"
    ]

    existing = [c for c in drop_columns if c in wanted_data.columns]
    wanted_data.drop(columns=existing, inplace=True)

    logger.info(f"Dropped columns: {existing}")

    
    # Type Conversions

    numeric_cols = ["budget", "revenue", "id", "popularity", "vote_count"]

    for col in numeric_cols:
        if col in wanted_data.columns:
            wanted_data[col] = pd.to_numeric(wanted_data[col], errors="coerce")

    if "release_date" in wanted_data.columns:
        wanted_data["release_date"] = pd.to_datetime(
            wanted_data["release_date"], errors="coerce"
        )

    
    # Handle Invalid 
    
    wanted_data.loc[wanted_data["budget"] == 0, "budget"] = pd.NA
    wanted_data.loc[wanted_data["revenue"] == 0, "revenue"] = pd.NA


    # Financial Analytics
    
    wanted_data["budget_musd_num"] = wanted_data["budget"] / 1_000_000
    wanted_data["revenue_musd_num"] = wanted_data["revenue"] / 1_000_000

    wanted_data["profit_musd"] = (
        wanted_data["revenue_musd_num"] - wanted_data["budget_musd_num"]
    )

    wanted_data["roi"] = (
        wanted_data["profit_musd"] / wanted_data["budget_musd_num"]
    ).replace([float("inf"), -float("inf")], pd.NA)

    
    # Presentation Columns
    
    wanted_data["budget_musd"] = wanted_data["budget_musd_num"].apply(
        lambda x: f"${x:.1f}M" if pd.notna(x) else pd.NA
    )

    wanted_data["revenue_musd"] = wanted_data["revenue_musd_num"].apply(
        lambda x: f"${x:.1f}M" if pd.notna(x) else pd.NA
    )

    
    # Data Quality Filters
    
    wanted_data.drop_duplicates(subset=["movie_id"], inplace=True)
    wanted_data.dropna(subset=["movie_id", "title"], inplace=True)

    # Keep rows with at least 10 non-null fields
    wanted_data = wanted_data[wanted_data.notna().sum(axis=1) >= 10]
    
    # Column Ordering (Guaranteed)
    
    final_columns = [
        "movie_id",
        "title",
        "tagline",
        "release_date",
        "genres",
        "belongs_to_collection",
        "original_language",
        "budget_musd",
        "revenue_musd",
        "budget_musd_num",
        "revenue_musd_num",
        "profit_musd",
        "roi",
        "production_companies",
        "production_countries",
        "vote_count",
        "vote_average",
        "popularity",
        "runtime",
        "overview",
        "spoken_languages",
        "poster_path",
        "cast",
        "cast_size",
        "director",
        "crew_size"
    ]

    missing = set(final_columns) - set(wanted_data.columns)
    if missing:
        logger.warning(f"Missing expected columns: {missing}")

    wanted_data = wanted_data[[c for c in final_columns if c in wanted_data.columns]]
    wanted_data.reset_index(drop=True, inplace=True)

    logger.info(f"Transformation complete | final rows: {len(wanted_data)}")
    logger.info(f"Final columns: {wanted_data.columns.tolist()}")
    return wanted_data



# Local Execution


if __name__ == "__main__":
    try:
       raw_df = pd.read_json(RAW_JSON)
       logger.info(f"Loaded {len(raw_df)} raw movies")
    except FileNotFoundError:
        logger.error("movies_raw.json not found. Run extract.py first.")
        raise

    transformed = transform_movies(raw_df)
    transformed.to_csv(TRANSFORMED_CSV, index=False)
    logger.info(f"Saved transformed movies to {TRANSFORMED_CSV}")
    