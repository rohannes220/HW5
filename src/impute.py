"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    return pd.Series(
        {
            "std_before": before.std(),
            "std_after": after.std(),
            "corr_before": before.corr(other),
            "corr_after": after.corr(other),
        }
    )


def fill_median(df: pd.DataFrame) -> pd.Series:
    return df["Lot Frontage"].fillna(df["Lot Frontage"].median())


# AI generated
def fill_neighborhood_median(df: pd.DataFrame) -> pd.Series:
    overall_med = df["Lot Frontage"].median()
    grp_med = (
        df.groupby("Neighborhood")["Lot Frontage"]
        .transform("median")
        .fillna(overall_med)
    )
    return df["Lot Frontage"].fillna(grp_med)


def plot_histogram(
    before: pd.Series, after: pd.Series, title: str, out_path: Path
) -> None:
    # plot the histograms
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # plot histogram before imputing
    axes[0].hist(before.dropna(), bins=50, label="Before (observed)")
    axes[0].set_title("Lot Frontage before imputing")
    axes[0].set_xlabel("Lot Frontage")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()

    # plot histogram after imputing
    axes[1].hist(after, bins=50, label="After (imputed)")
    axes[1].set_title(title)
    axes[1].set_xlabel("Lot Frontage")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()

    # save file to out path
    # make sure that folder exists
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)


if __name__ == "__main__":
    # load the cleaned df
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])

    # imputing "Lot Frontage" and observing correlation with "Lot Area"
    lot_frontage_values_before = df["Lot Frontage"]
    lot_area_values = df["Lot Area"]

    # impute values using both strategies
    lot_frontage_imputed_with_median = fill_median(df)
    lot_frontage_imputed_using_neighborhood_median = fill_neighborhood_median(df)

    # create summary data frame with columns - std_before, std_after, corr_before, corr_after
    # and each row for a different imputing strategy
    # and print the summary
    table = pd.DataFrame(
        {
            "median": cost_table(
                lot_frontage_values_before,
                lot_frontage_imputed_with_median,
                lot_area_values,
            ),
            "neighborhood_median": cost_table(
                lot_frontage_values_before,
                lot_frontage_imputed_using_neighborhood_median,
                lot_area_values,
            ),
        }
    ).T
    print(table)

    # save the histograms
    fig_dir = Path("reports/figures")
    plot_histogram(
        lot_frontage_values_before,
        lot_frontage_imputed_with_median,
        "Lot Frontage: Median Fill",
        fig_dir / "histogram_median_fill.png",
    )
    plot_histogram(
        lot_frontage_values_before,
        lot_frontage_imputed_using_neighborhood_median,
        "Lot Frontage: Neighborhood Median Fill",
        fig_dir / "histogram_neighborhood_median_fill.png",
    )