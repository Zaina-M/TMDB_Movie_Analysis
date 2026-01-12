import os
import logging
import pandas as pd

# ======================================================
# Logging Configuration
# ======================================================

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("movie_transformer")
logger.setLevel(logging.INFO)

log_file = os.path.join(LOG_DIR, "transform_movies.log")

if not logger.handlers:
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False


# ======================================================
# Helper Functions
# ======================================================

def extract_credits(credits: dict) -> pd.Series:
    """Extract cast, director, and crew stats from credits JSON."""
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
    """
    Flattens:
    - dict -> value['name']
    - list[dict] -> 'name|name|name'
    """
    if isinstance(value, dict):
        return value.get("name")
    if isinstance(value, list):
        return "|".join(
            item.get("name") for item in value if isinstance(item, dict)
        )
    return pd.NA


# ======================================================
# Main Transform Function
# ======================================================

def transform_movies(raw_movies: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting movie transformation")

    wanted_data = raw_movies.copy()
    logger.info(f"Initial rows: {len(wanted_data)}")

    # --------------------------------------------------
    # Credits Extraction (BEFORE dropping credits)
    # --------------------------------------------------
    if "credits" in wanted_data.columns:
        logger.info("Extracting credits data")
        credits_df = wanted_data["credits"].apply(extract_credits)
        wanted_data = pd.concat([wanted_data, credits_df], axis=1)
    else:
        logger.warning("credits column missing")

    # --------------------------------------------------
    # Flatten JSON-like Columns
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Drop Irrelevant / Noisy Columns
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Type Conversions
    # --------------------------------------------------
    numeric_cols = ["budget", "revenue", "id", "popularity", "vote_count"]

    for col in numeric_cols:
        if col in wanted_data.columns:
            wanted_data[col] = pd.to_numeric(wanted_data[col], errors="coerce")

    if "release_date" in wanted_data.columns:
        wanted_data["release_date"] = pd.to_datetime(
            wanted_data["release_date"], errors="coerce"
        )

    # --------------------------------------------------
    # Handle Invalid / Zero Values
    # --------------------------------------------------
    wanted_data.loc[wanted_data["budget"] == 0, "budget"] = pd.NA
    wanted_data.loc[wanted_data["revenue"] == 0, "revenue"] = pd.NA

    # --------------------------------------------------
    # Financial Analytics
    # --------------------------------------------------
    wanted_data["budget_musd_num"] = wanted_data["budget"] / 1_000_000
    wanted_data["revenue_musd_num"] = wanted_data["revenue"] / 1_000_000

    wanted_data["profit_musd"] = (
        wanted_data["revenue_musd_num"] - wanted_data["budget_musd_num"]
    )

    wanted_data["roi"] = (
        wanted_data["profit_musd"] / wanted_data["budget_musd_num"]
    ).replace([float("inf"), -float("inf")], pd.NA)

    # --------------------------------------------------
    # Presentation Columns
    # --------------------------------------------------
    wanted_data["budget_musd"] = wanted_data["budget_musd_num"].apply(
        lambda x: f"${x:.1f}M" if pd.notna(x) else pd.NA
    )

    wanted_data["revenue_musd"] = wanted_data["revenue_musd_num"].apply(
        lambda x: f"${x:.1f}M" if pd.notna(x) else pd.NA
    )

    # --------------------------------------------------
    # Data Quality Filters
    # --------------------------------------------------
    wanted_data.drop_duplicates(subset=["movie_id"], inplace=True)
    wanted_data.dropna(subset=["movie_id", "title"], inplace=True)

    # Keep rows with at least 10 non-null fields
    wanted_data = wanted_data[wanted_data.notna().sum(axis=1) >= 10]
    # --------------------------------------------------
    # Column Ordering (Guaranteed)
    # --------------------------------------------------
    final_columns = [
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


# ======================================================
# Local Execution
# ======================================================

if __name__ == "__main__":
    try:
        raw_df = pd.read_json("movies_raw.json")
        logger.info(f"Loaded {len(raw_df)} raw movies")
    except FileNotFoundError:
        logger.error("movies_raw.json not found. Run extract.py first.")
        raise

    transformed = transform_movies(raw_df)
    transformed.to_csv("movies_transformed.csv", index=False)
    logger.info("Saved movies_transformed.csv")
# import os
# import logging
# import pandas as pd

# # -------------------------
# # Logging
# # -------------------------

# import logging
# import os

# LOG_DIR = "logs"
# os.makedirs(LOG_DIR, exist_ok=True)

# logger = logging.getLogger("movie_transformer")
# logger.setLevel(logging.INFO)

# log_file = os.path.join(LOG_DIR, "transform_movies.log")

# # Prevent duplicate handlers
# if not logger.handlers:
#     file_handler = logging.FileHandler(log_file)
#     formatter = logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#     )
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)

# # Prevent logs going to root logger / console
# logger.propagate = False



# # -------------------------
# # Helpers
# # -------------------------
# def extract_credits(credits: dict) -> pd.Series:
#     if not isinstance(credits, dict):
#         logger.warning("Credits is not a dict; defaulting to empty")
#         credits = {}

#     cast = credits.get("cast", [])
#     crew = credits.get("crew", [])

#     if not isinstance(cast, list):
#         logger.warning("Cast is not a list; defaulting to empty")
#         cast = []

#     if not isinstance(crew, list):
#         logger.warning("Crew is not a list; defaulting to empty")
#         crew = []

#     director = next(
#         (person.get("name") for person in crew if person.get("job") == "Director"),
#         None
#     )

#     return pd.Series({
#         "cast": cast,
#         "cast_size": len(cast),
#         "director": director,
#         "crew_size": len(crew)
#     })


# def flatten_json_column(value):
#     if isinstance(value, dict):
#         return value.get("name")
#     if isinstance(value, list):
#         return "|".join(
#             item.get("name") for item in value if isinstance(item, dict)
#         )
#     return None


# def format_musd(value):
#     try:
#         return f"${value / 1_000_000:.1f}M"
#     except Exception:
#         logger.warning(f"Failed to format value as MUSD: {value}")
#         return None


# # -------------------------
# # Main Transform Function
# # -------------------------
# def transform_movies(wanted_movies):
#     logger.info("Starting movie transformation")

#     wanted_data = pd.DataFrame(wanted_movies)
#     logger.info(f"Initial rows: {len(wanted_data)}")

#     # -------- Credits --------
#     if "credits" in wanted_data.columns:
#         logger.info("Extracting credits information")
#         credits_df = wanted_data["credits"].apply(extract_credits)
#         wanted_data = pd.concat([wanted_data, credits_df], axis=1)
#     else:
#         logger.warning("Credits column not found")

#     # -------- Drop noise --------
#     drop_cols = [
#         "adult", "imdb_id", "original_title",
#         "video", "homepage", "credits"
#     ]
#     existing_drop_cols = [c for c in drop_cols if c in wanted_data.columns]
#     wanted_data.drop(columns=existing_drop_cols, inplace=True)

#     logger.info(f"Dropped columns: {existing_drop_cols}")

#     # -------- Flatten JSON fields --------
#     json_cols = [
#         "belongs_to_collection",
#         "genres",
#         "production_companies",
#         "spoken_languages",
#         "production_countries"
#     ]

#     for col in json_cols:
#         if col in wanted_data.columns:
#             logger.info(f"Flattening column: {col}")
#             wanted_data[col] = wanted_data[col].apply(flatten_json_column)

#     # -------- Numeric conversions --------
#     numeric_cols = ["budget", "revenue", "id", "popularity"]
#     for col in numeric_cols:
#         if col in wanted_data.columns:
#             wanted_data[col] = pd.to_numeric(wanted_data[col], errors="coerce").fillna(0)

#     logger.info(f"Converted numeric columns: {numeric_cols}")

#     # -------- Dates --------
#     if "release_date" in wanted_data.columns:
#         wanted_data["release_date"] = pd.to_datetime(wanted_data["release_date"], errors="coerce")
#         logger.info("Converted release_date to datetime")

#     # -------- Money formatting --------
#     for col in ["budget", "revenue"]:
#         if col in wanted_data.columns:
#             logger.info(f"Formatting {col} to USD millions")
#             wanted_data[f"{col}_musd"] = wanted_data[col].apply(format_musd)
#             wanted_data.drop(columns=[col], inplace=True)

#     # -------- Reorder columns --------
#     column_order = [
#         "id", "title", "tagline", "release_date", "genres",
#         "belongs_to_collection", "original_language",
#         "budget_musd", "revenue_musd",
#         "production_companies", "production_countries",
#         "vote_count", "vote_average", "popularity",
#         "runtime", "overview", "spoken_languages",
#         "poster_path", "cast", "cast_size",
#         "director", "crew_size"
#     ]

#     wanted_data = wanted_data[[c for c in column_order if c in wanted_data.columns]]

#     wanted_data.reset_index(drop=True, inplace=True)

#     logger.info(f"Transformation completed | final rows: {len(wanted_data)}")

#     return wanted_data


# # -------------------------  
# # Main Execution
# # -------------------------
# if __name__ == "__main__":
#     # Load raw movie data
#     try:
#         raw_movies = pd.read_json("movies_raw.json")
#         logger.info(f"Loaded {len(raw_movies)} movies from movies_raw.json")
#     except FileNotFoundError:
#         logger.error("movies_raw.json not found. Run extract.py first.")
#         exit(1)
    
#     # Transform the data
#     transformed_data = transform_movies(raw_movies)
    
#     # Save transformed data
#     transformed_data.to_csv("movies_transformed.csv", index=False)
#     logger.info("Transformed data saved to movies_transformed.csv")