import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from Config.paths import VIS_LOG, LOG_DIR, TRANSFORMED_CSV


# LOGGING 

LOG_DIR.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger("movie_visualization")
logger.setLevel(logging.INFO)

# Clear handlers to avoid notebook duplication
if not logger.handlers:
    file_handler = logging.FileHandler(VIS_LOG, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

logger.propagate = False
logger.info("Logger initialized successfully")


file_handler = logging.FileHandler(
    VIS_LOG,
    mode="w",
    encoding="utf-8"
)

logger.info("Logger initialized successfully")
file_handler.flush()



# ANALYTICS PREPARATION

def prepare_analytics(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Preparing analytics columns")

    df = df.copy()

    df["budget_musd_num"] = pd.to_numeric(df["budget_musd_num"], errors="coerce")
    df["revenue_musd_num"] = pd.to_numeric(df["revenue_musd_num"], errors="coerce")

    df["profit_musd"] = df["revenue_musd_num"] - df["budget_musd_num"]
    df["roi"] = df["profit_musd"] / df["budget_musd_num"].where(df["budget_musd_num"] > 0)

    df["release_year"] = pd.to_datetime(
        df["release_date"], errors="coerce"
    ).dt.year

    df["genres"] = df["genres"].str.split("|")
    df = df.explode("genres")


    df["movie_type"] = df["belongs_to_collection"].apply(
        lambda x: "Franchise" if pd.notna(x) else "Standalone"
    )

    logger.info("Analytics preparation completed")
    file_handler.flush()

    return df


# VISUALIZATIONS 

def plot_revenue_vs_budget(df: pd.DataFrame):
    logger.info("Plotting Revenue vs Budget (Franchise vs Standalone)")

    plt.figure(figsize=(12, 7))

    # Split data
    standalone = df[df["movie_type"] == "Standalone"]
    franchise = df[df["movie_type"] == "Franchise"]

    # Scatter plots
    plt.scatter(
        standalone["budget_musd_num"],
        standalone["revenue_musd_num"],
        alpha=0.6,
        s=40,
        label="Standalone"
    )

    plt.scatter(
        franchise["budget_musd_num"],
        franchise["revenue_musd_num"],
        alpha=0.6,
        s=60,
        label="Franchise"
    )

    # HARD axis limits (NO AUTO SCALING)
    plt.xlim(100, 400)
    plt.ylim(1000, 3000)

    # FORCE x-axis ticks: 100, 150, 200, ...
    plt.xticks(range(100, 501, 50))

    # Break-even line (within forced limits)
    plt.plot(
        [100, 500],
        [100, 500],
        linestyle="--",
        label="Break-even"
    )

    # Labels and title
    plt.xlabel("Budget (Million USD)")
    plt.ylabel("Revenue (Million USD)")
    plt.title("Revenue vs Budget (Franchise vs Standalone)")
    plt.legend()

    plt.show()



def plot_avg_roi_by_genre(df: pd.DataFrame):
    logger.info("Plotting Average ROI by Genre")

    genre_roi = (
        df[df["budget_musd_num"] > 0]
        .groupby("genres")["roi"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(12, 6))
    plt.bar(genre_roi.index, genre_roi.values)

    # Indicator: zero ROI reference
    plt.axhline(0, linestyle="--")

    plt.xlabel("Genre")
    plt.ylabel("Average ROI")
    plt.title("Average ROI by Genre")
    plt.xticks(rotation=45, ha="right")
    plt.show()



def plot_popularity_vs_rating(df: pd.DataFrame):
    logger.info("Plotting Popularity vs Rating")

    plt.figure(figsize=(10, 6))

    # Scatter: each dot is one movie
    plt.scatter(
        df["popularity"],
        df["vote_average"],
        alpha=0.6,
        marker="o",
        label="Movies"
    )

    # Average rating reference line
    avg_rating = df["vote_average"].mean()
    plt.axhline(
        avg_rating,
        linestyle="--",
        label=f"Average Rating ({avg_rating:.2f})"
    )

    plt.xlabel("Popularity")
    plt.ylabel("Average Rating")
    plt.title("Popularity vs Rating")

    plt.legend()
    plt.show()

    file_handler.flush()


def plot_yearly_revenue_trend(df: pd.DataFrame):
    logger.info("Plotting Yearly Revenue Trend")

    yearly = (
        df.groupby("release_year")["revenue_musd_num"]
        .mean()
        .dropna()
    )

    plt.figure(figsize=(12, 6))

    # Yearly revenue trend
    plt.plot(
        yearly.index,
        yearly.values,
        marker="o",
        label="Average Revenue per Year"
    )

    # Overall average reference line
    overall_avg = yearly.mean()
    plt.axhline(
        overall_avg,
        linestyle="--",
        label="Overall Average Revenue"
    )

    plt.xlabel("Release Year")
    plt.ylabel("Average Revenue (Million USD)")
    plt.title("Yearly Average Box Office Revenue")

    plt.legend()
    plt.show()

    file_handler.flush()



def plot_franchise_vs_standalone(df: pd.DataFrame):
    logger.info("Plotting Franchise vs Standalone (Multiple Metrics)")

    # Aggregate metrics
    metrics = df.groupby("movie_type").agg(
        avg_revenue=("revenue_musd_num", "mean"),
        avg_roi=("roi", "mean"),
        avg_rating=("vote_average", "mean"),
        avg_popularity=("popularity", "mean")
    )

    # Ensure fixed order
    metrics = metrics.loc[["Standalone", "Franchise"]]

    categories = metrics.index.tolist()
    x = range(len(categories))

    # Color mapping (EXPLICIT)
    color_map = {
        "Standalone": "skyblue",
        "Franchise": "orange"
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    # Helper function to plot bars correctly
    def bar_plot(ax, values, title, ylabel=None):
        ax.bar(
            x,
            values,
            color=[color_map[c] for c in categories]
        )
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_title(title)
        if ylabel:
            ax.set_ylabel(ylabel)

    bar_plot(
        axes[0],
        metrics["avg_revenue"],
        "Average Revenue",
        "Million USD"
    )

    bar_plot(
        axes[1],
        metrics["avg_roi"],
        "Average ROI"
    )

    bar_plot(
        axes[2],
        metrics["avg_rating"],
        "Average Rating"
    )

    bar_plot(
        axes[3],
        metrics["avg_popularity"],
        "Average Popularity"
    )

    # Proper legend (BOTTOM, readable)
    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, color="skyblue"),
        plt.Rectangle((0, 0), 1, 1, color="orange")
    ]

    fig.legend(
        legend_handles,
        ["Standalone", "Franchise"],
        loc="lower center",
        ncol=2
    )

    fig.suptitle("Franchise vs Standalone Comparison", fontsize=16)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.show()

    file_handler.flush()



# RUNNER

def run_all_visualizations(df: pd.DataFrame):
    logger.info("Starting visualization pipeline")

    df_analytics = prepare_analytics(df) 

    plot_revenue_vs_budget(df_analytics)
    plot_avg_roi_by_genre(df_analytics)
    plot_popularity_vs_rating(df_analytics)
    plot_yearly_revenue_trend(df_analytics)
    plot_franchise_vs_standalone(df_analytics)

    logger.info("All visualizations completed")


# if __name__ == "__main__":
    

#     try:
#         df = pd.read_csv(TRANSFORMED_CSV)
#         logger.info("Loaded transformed data")
#         run_all_visualizations(df)
#     except FileNotFoundError:
#         logger.error("Transformed CSV not found")
