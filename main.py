from Extraction.extract import fetch_movies, MOVIE_IDS
from Transformation.transform import transform_movies
from KPI.kpis import compute_all_kpis
from Visualization.visualize import prepare_analytics, run_all_visualizations

from Config.paths import (
    RAW_JSON,
    TRANSFORMED_CSV,
    KPI_CSV
)

import logging


# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("tmdb_pipeline")


# ---------------- PIPELINE ----------------

def main():
    logger.info("Starting TMDB pipeline")

    # -------- EXTRACT --------
    logger.info("Starting extraction step")
    raw_movies = fetch_movies(MOVIE_IDS)
    raw_movies.to_json(RAW_JSON, orient="records", lines=True)
    logger.info(f"Fetched {len(raw_movies)} movies")

    # -------- TRANSFORM --------
    logger.info("Starting transformation step")
    transformed_df = transform_movies(raw_movies)
    transformed_df.to_csv(TRANSFORMED_CSV, index=False)
    logger.info(f"Transformed data saved to {TRANSFORMED_CSV}")

    # -------- KPI --------
    logger.info("Starting KPI computation")
    kpi_df = compute_all_kpis(transformed_df)
    kpi_df.to_csv(KPI_CSV, index=False)
    logger.info(f"KPI results saved to {KPI_CSV}")

    # -------- ANALYTICS --------
    logger.info("Preparing analytics dataset")
    analytics_df = prepare_analytics(transformed_df)

    # -------- VISUALIZATION --------
    logger.info("Running visualizations")
    run_all_visualizations(analytics_df)

    logger.info("TMDB pipeline finished successfully")


# ---------------- ENTRY POINT ----------------

if __name__ == "__main__":
    main()
