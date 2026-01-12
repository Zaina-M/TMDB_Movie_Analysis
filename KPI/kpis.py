import logging
import pandas as pd
import os

# -------------------------
# Logging
# -------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("movie_kpis")
logger.setLevel(logging.INFO)

log_file = os.path.join(LOG_DIR, "kpi_movies.log")

# Prevent duplicate handlers
if not logger.handlers:
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Prevent logs going to root logger / console
logger.propagate = False


KPI_DEFINITIONS = {
    "Highest Revenue": {
        "column": "revenue_musd_num",
        "agg": "max"
    },
    "Highest Budget": {
        "column": "budget_musd_num",
        "agg": "max"
    },
    "Highest Profit": {
        "column": "profit_musd",
        "agg": "max"
    },
    "Lowest Profit": {
        "column": "profit_musd",
        "agg": "min"
    },
    "Highest ROI (Budget ≥10M)": {
        "column": "roi",
        "agg": "max",
        "filter_col": "budget_musd_num",
        "filter_val": 10
    },
    "Lowest ROI (Budget ≥10M)": {
        "column": "roi",
        "agg": "min",
        "filter_col": "budget_musd_num",
        "filter_val": 10
    },
    "Most Voted": {
        "column": "vote_count",
        "agg": "max"
    },
    "Highest Rated (Votes ≥10)": {
        "column": "vote_average",
        "agg": "max",
        "filter_col": "vote_count",
        "filter_val": 10
    },
    "Lowest Rated (Votes ≥10)": {
        "column": "vote_average",
        "agg": "min",
        "filter_col": "vote_count",
        "filter_val": 10
    },
    "Most Popular": {
        "column": "popularity",
        "agg": "max"
    }
}

def get_movie_kpi(df: pd.DataFrame, kpi_name: str) -> pd.DataFrame:
    """
    Compute a single movie KPI and return the result as a DataFrame.
    """

    logger.info(f"Computing KPI: {kpi_name}")

    if kpi_name not in KPI_DEFINITIONS:
        logger.error(f"KPI '{kpi_name}' is not defined")
        raise ValueError(f"Unknown KPI: {kpi_name}")

    config = KPI_DEFINITIONS[kpi_name]
    col = config["column"]
    agg = config["agg"]
    filter_col = config.get("filter_col")
    filter_val = config.get("filter_val")

    # Validate required columns
    required_cols = ["title", col]
    if filter_col:
        required_cols.append(filter_col)

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        logger.error(f"Missing columns for KPI '{kpi_name}': {missing}")
        raise ValueError(f"Missing columns: {missing}")

    temp = df.copy()

    # Apply filter if needed
    if filter_col:
        temp = temp[temp[filter_col] >= filter_val]
        logger.info(
            f"Applied filter: {filter_col} >= {filter_val} "
            f"(remaining rows: {len(temp)})"
        )

    if temp.empty:
        logger.warning(f"No data after filtering for KPI '{kpi_name}'")
        return pd.DataFrame([{
            "KPI": kpi_name,
            "Movie": None,
            "Value": None
        }])

    idx = temp[col].idxmax() if agg == "max" else temp[col].idxmin()

    result = pd.DataFrame([{
        "KPI": kpi_name,
        "Movie": temp.loc[idx, "title"],
        "Value": temp.loc[idx, col]
    }])

    logger.info(
        f"KPI '{kpi_name}' result: "
        f"{result.iloc[0]['Movie']} ({result.iloc[0]['Value']})"
    )

    return result


def compute_all_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all defined KPIs and return as a single DataFrame.
    """
    logger.info(f"Computing all KPIs for {len(df)} movies")
    
    results = []
    for kpi_name in KPI_DEFINITIONS.keys():
        try:
            result = get_movie_kpi(df, kpi_name)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to compute KPI '{kpi_name}': {e}")
    
    if results:
        all_results = pd.concat(results, ignore_index=True)
        logger.info(f"Computed {len(all_results)} KPIs successfully")
        return all_results
    else:
        logger.error("No KPIs were computed successfully")
        return pd.DataFrame()


# -------------------------
# Main Execution
# -------------------------
if __name__ == "__main__":
    # Load transformed movie data
    try:
        movies_df = pd.read_csv("movies_transformed.csv")
        logger.info(f"Loaded {len(movies_df)} movies from movies_transformed.csv")
    except FileNotFoundError:
        logger.error("movies_transformed.csv not found. Run transform.py first.")
        exit(1)
    
    # Compute all KPIs
    kpi_results = compute_all_kpis(movies_df)
    
    if not kpi_results.empty:
        # Save KPI results
        kpi_results.to_csv("movie_kpis.csv", index=False)
        logger.info("KPI results saved to movie_kpis.csv")
        
    else:
        logger.error("No KPI results to save")