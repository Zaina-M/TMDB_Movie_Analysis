# import os
# import logging
# import pandas as pd
# import matplotlib.pyplot as plt

# # -------------------------
# # Logging (FILE ONLY)
# # -------------------------
# logger = logging.getLogger("movie_visualization")
# logger.setLevel(logging.INFO)

# os.makedirs("logs", exist_ok=True)

# logger.handlers.clear()  # CRITICAL for notebooks

# file_handler = logging.FileHandler("logs/visualization.log", encoding="utf-8")
# formatter = logging.Formatter(
#     "%(asctime)s | %(levelname)s | %(message)s"
# )
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# logger.propagate = False



# # -------------------------
# # Analytics Preparation
# # -------------------------
# def prepare_analytics(df: pd.DataFrame) -> pd.DataFrame:
#     logger.info("Preparing analytics columns")

#     df = df.copy()

#     df["budget_musd_num"] = pd.to_numeric(df["budget_musd_num"], errors="coerce")
#     df["revenue_musd_num"] = pd.to_numeric(df["revenue_musd_num"], errors="coerce")

#     df["profit_musd"] = df["revenue_musd_num"] - df["budget_musd_num"]
#     df["roi"] = df["profit_musd"] / df["budget_musd_num"].where(df["budget_musd_num"] > 0)

#     df["release_year"] = pd.to_datetime(
#         df["release_date"], errors="coerce"
#     ).dt.year

#     df["primary_genre"] = df["genres"].str.split("|").str[0]

#     df["movie_type"] = df["belongs_to_collection"].apply(
#         lambda x: "Franchise" if pd.notna(x) else "Standalone"
#     )

#     logger.info("Analytics preparation completed")
#     return df


# # -------------------------
# # Visualizations (Notebook)
# # -------------------------
# def plot_revenue_vs_budget(df: pd.DataFrame):
#     logger.info("Plotting Revenue vs Budget")

#     plt.figure(figsize=(10, 6))
#     plt.scatter(df["budget_musd_num"], df["revenue_musd_num"], alpha=0.6)

#     # Indicator: break-even line
#     max_val = max(df["budget_musd_num"].max(), df["revenue_musd_num"].max())
#     plt.plot([0, max_val], [0, max_val], linestyle="--", label="Break-even")

#     plt.xlabel("Budget (Million USD)")
#     plt.ylabel("Revenue (Million USD)")
#     plt.title("Revenue vs Budget")
#     plt.legend()
#     plt.grid(True)
#     plt.show()


# def plot_avg_roi_by_genre(df: pd.DataFrame):
#     logger.info("Plotting Average ROI by Genre")

#     genre_roi = (
#         df[df["budget_musd_num"] > 0]
#         .groupby("primary_genre")["roi"]
#         .mean()
#         .sort_values(ascending=False)
#     )

#     plt.figure(figsize=(12, 6))
#     plt.bar(genre_roi.index, genre_roi.values)

#     # Indicator: zero ROI reference
#     plt.axhline(0, linestyle="--")

#     plt.xlabel("Genre")
#     plt.ylabel("Average ROI")
#     plt.title("Average ROI by Genre")
#     plt.xticks(rotation=45, ha="right")
#     plt.show()


# def plot_popularity_vs_rating(df: pd.DataFrame):
#     logger.info("Plotting Popularity vs Rating")

#     plt.figure(figsize=(10, 6))
#     plt.scatter(df["popularity"], df["vote_average"], alpha=0.6)

#     # Indicator: average rating
#     avg_rating = df["vote_average"].mean()
#     plt.axhline(avg_rating, linestyle="--", label=f"Average Rating ({avg_rating:.2f})")

#     plt.xlabel("Popularity")
#     plt.ylabel("Average Rating")
#     plt.title("Popularity vs Rating")
#     plt.legend()
#     plt.grid(True)
#     plt.show()


# def plot_yearly_revenue_trend(df: pd.DataFrame):
#     logger.info("Plotting Yearly Revenue Trend")

#     yearly = (
#         df.groupby("release_year")["revenue_musd_num"]
#         .mean()
#         .dropna()
#     )

#     plt.figure(figsize=(12, 6))
#     plt.plot(yearly.index, yearly.values, marker="o")

#     # Indicator: overall average
#     overall_avg = yearly.mean()
#     plt.axhline(overall_avg, linestyle="--", label="Overall Average")

#     plt.xlabel("Release Year")
#     plt.ylabel("Average Revenue (Million USD)")
#     plt.title("Yearly Average Box Office Revenue")
#     plt.legend()
#     plt.grid(True)
#     plt.show()


# def plot_franchise_vs_standalone(df: pd.DataFrame):
#     logger.info("Plotting Franchise vs Standalone (Multiple Metrics)")

#     metrics = df.groupby("movie_type").agg(
#         avg_revenue=("revenue_musd_num", "mean"),
#         avg_roi=("roi", "mean"),
#         avg_rating=("vote_average", "mean"),
#         avg_popularity=("popularity", "mean")
#     )

#     fig, axes = plt.subplots(2, 2, figsize=(14, 10))
#     axes = axes.flatten()

#     metrics["avg_revenue"].plot(kind="bar", ax=axes[0], title="Average Revenue")
#     metrics["avg_roi"].plot(kind="bar", ax=axes[1], title="Average ROI")
#     metrics["avg_rating"].plot(kind="bar", ax=axes[2], title="Average Rating")
#     metrics["avg_popularity"].plot(kind="bar", ax=axes[3], title="Average Popularity")

#     for ax in axes:
#         ax.grid(True)

#     fig.suptitle("Franchise vs Standalone Comparison")
#     plt.show()


# # -------------------------
# # Runner
# # -------------------------
# def run_all_visualizations(df: pd.DataFrame):
#     logger.info("Running all visualizations")

#     plot_revenue_vs_budget(df)
#     plot_avg_roi_by_genre(df)
#     plot_popularity_vs_rating(df)
#     plot_yearly_revenue_trend(df)
#     plot_franchise_vs_standalone(df)

#     logger.info("All visualizations completed")


import os
import logging
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# LOGGING (NOTEBOOK-SAFE)
# =========================
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("movie_visualization")
logger.setLevel(logging.INFO)

# Clear handlers to avoid notebook duplication
logger.handlers.clear()

file_handler = logging.FileHandler(
    "logs/visualization.log",
    mode="w",
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.propagate = False

logger.info("Logger initialized successfully")
file_handler.flush()


# =========================
# ANALYTICS PREPARATION
# =========================
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

    df["primary_genre"] = df["genres"].str.split("|").str[0]

    df["movie_type"] = df["belongs_to_collection"].apply(
        lambda x: "Franchise" if pd.notna(x) else "Standalone"
    )

    logger.info("Analytics preparation completed")
    file_handler.flush()

    return df


# =========================
# VISUALIZATIONS (SHOW ONLY)
# =========================
def plot_revenue_vs_budget(df: pd.DataFrame):
    logger.info("Plotting Revenue vs Budget")

    plt.figure(figsize=(12, 7))
    
    # Scatter plot
    plt.scatter(
        df["budget_musd_num"], 
        df["revenue_musd_num"], 
        alpha=0.6, 
        c='teal', 
        edgecolor='k', 
        label="Movies"
    )

    # Break-even line
    max_val = max(df["budget_musd_num"].max(), df["revenue_musd_num"].max())
    plt.plot([0, max_val], [0, max_val], linestyle="--", color="red", label="Break-even")

    # Labels and title
    plt.xlabel("Budget (Million USD)", fontsize=12)
    plt.ylabel("Revenue (Million USD)", fontsize=12)
    plt.title("Revenue vs Budget", fontsize=14)

    # Legend
    plt.legend()

    # Grid and layout
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()  # prevent overlap

    # Show plot
    plt.show()

    # Flush logs
    file_handler.flush()


def plot_avg_roi_by_genre(df: pd.DataFrame):
    logger.info("Plotting Average ROI by Genre")

    genre_roi = (
        df[df["budget_musd_num"] > 0]
        .groupby("primary_genre")["roi"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(12, 6))
    plt.bar(genre_roi.index, genre_roi.values)
    plt.axhline(0, linestyle="--")

    plt.xlabel("Genre")
    plt.ylabel("Average ROI")
    plt.title("Average ROI by Genre")
    plt.xticks(rotation=45, ha="right")
    plt.show()

    file_handler.flush()


def plot_popularity_vs_rating(df: pd.DataFrame):
    logger.info("Plotting Popularity vs Rating")

    plt.figure(figsize=(10, 6))
    plt.scatter(df["popularity"], df["vote_average"], alpha=0.6)

    avg_rating = df["vote_average"].mean()
    plt.axhline(avg_rating, linestyle="--", label=f"Avg Rating ({avg_rating:.2f})")

    plt.xlabel("Popularity")
    plt.ylabel("Average Rating")
    plt.title("Popularity vs Rating")
    plt.legend()
    plt.grid(True)
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
    plt.plot(yearly.index, yearly.values, marker="o")

    overall_avg = yearly.mean()
    plt.axhline(overall_avg, linestyle="--", label="Overall Average")

    plt.xlabel("Release Year")
    plt.ylabel("Average Revenue (Million USD)")
    plt.title("Yearly Average Box Office Revenue")
    plt.legend()
    #plt.grid(True)
    plt.show()

    file_handler.flush()


def plot_franchise_vs_standalone(df: pd.DataFrame):
    logger.info("Plotting Franchise vs Standalone (Multiple Metrics)")

    # Aggregate multiple metrics
    metrics = df.groupby("movie_type").agg(
        avg_revenue=("revenue_musd_num", "mean"),
        avg_roi=("roi", "mean"),
        avg_rating=("vote_average", "mean"),
        avg_popularity=("popularity", "mean")
    )

    # Define colors for each metric
    metric_colors = {
        "avg_revenue": ["skyblue", "orange"],
        "avg_roi": ["skyblue", "orange"],
        "avg_rating": ["skyblue", "orange"],
        "avg_popularity": ["skyblue", "orange"]
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    # Plot each metric with its colors
    metrics["avg_revenue"].plot(kind="bar", ax=axes[0], title="Average Revenue", color=metric_colors["avg_revenue"])
    axes[0].set_ylabel("Million USD")
    axes[0].grid(True, axis="y", linestyle="--", alpha=0.5)

    metrics["avg_roi"].plot(kind="bar", ax=axes[1], title="Average ROI", color=metric_colors["avg_roi"])
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.5)

    metrics["avg_rating"].plot(kind="bar", ax=axes[2], title="Average Rating", color=metric_colors["avg_rating"])
    axes[2].grid(True, axis="y", linestyle="--", alpha=0.5)

    metrics["avg_popularity"].plot(kind="bar", ax=axes[3], title="Average Popularity", color=metric_colors["avg_popularity"])
    axes[3].grid(True, axis="y", linestyle="--", alpha=0.5)

    fig.suptitle("Franchise vs Standalone Comparison", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    file_handler.flush()


# =========================
# RUNNER
# =========================

def run_all_visualizations(df: pd.DataFrame):
    logger.info("Starting visualization pipeline")

    df_analytics = prepare_analytics(df) 

    plot_revenue_vs_budget(df_analytics)
    plot_avg_roi_by_genre(df_analytics)
    plot_popularity_vs_rating(df_analytics)
    plot_yearly_revenue_trend(df_analytics)
    plot_franchise_vs_standalone(df_analytics)

    logger.info("All visualizations completed")
