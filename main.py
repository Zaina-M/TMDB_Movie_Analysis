from Extraction.extract import fetch_movies, MOVIE_IDS
from Transformation.transform import transform_movies
from KPI.kpis import compute_all_kpis
from Visualization.visualize import prepare_analytics, run_all_visualizations

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("pipeline")


def main():
    logger.info("Starting TMDB pipeline")

    # -------- Extract --------
    raw_movies = fetch_movies(MOVIE_IDS)
    logger.info(f"Fetched {len(raw_movies)} movies")

    # -------- Transform --------
    transformed_data = transform_movies(raw_movies)
    logger.info("Transformation complete")

    # -------- KPI --------
    kpi_df = compute_all_kpis(transformed_data)
    logger.info("KPI computation complete")

    #----- Prepare analytics
    analytics_df = prepare_analytics(transformed_data)
    logger.info("Analytics preparation complete")

    # -------- Visualization --------
    run_all_visualizations(analytics_df)
    logger.info("Visualizations generated")

    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    main()
