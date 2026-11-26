"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""

import sys

import pandas as pd


def compare_groups(
    df: pd.DataFrame, col: str, observed_cols: list[str]
) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""

    # count the number of rows in the df that have 'col' as missing
    is_col_missing = df[col].isna()
    num_missing_rows = int(is_col_missing.sum())
    print(f"{num_missing_rows}/{len(is_col_missing)} rows missing")
    print(f"Missing rows proportion: {num_missing_rows / len(is_col_missing):.2f}")

    # find the mean of the observed (numeric) columns with and without col
    # find the mode of the observed (categorical) columns with and without col
    summary_rows = []
    for observed_col in observed_cols:
        if pd.api.types.is_numeric_dtype(df[observed_col]):
            # compute mean with and without col
            mean_with_col = df.loc[~is_col_missing, observed_col].mean()
            mean_without_col = df.loc[is_col_missing, observed_col].mean()

            summary_rows.append(
                {
                    "column": observed_col,
                    "present_mean": mean_with_col,
                    "absent_mean": mean_without_col,
                    "present_top": "",
                    "absent_top": "",
                }
            )
        else:
            # compute mode with and without col
            modes_with_col = df.loc[~is_col_missing, observed_col].mode()
            mode_with_col = modes_with_col.iloc[0] if not modes_with_col.empty else ""

            modes_without_col = df.loc[is_col_missing, observed_col].mode()
            mode_without_col = (
                modes_without_col.iloc[0] if not modes_without_col.empty else ""
            )

            summary_rows.append(
                {
                    "column": observed_col,
                    "present_mean": float("nan"),
                    "absent_mean": float("nan"),
                    "present_top": mode_with_col,
                    "absent_top": mode_without_col,
                }
            )

    # print and return the summary df
    summary = pd.DataFrame(summary_rows)
    print(f"Reference col: {col}")
    print("Summary:")
    print(summary)
    print()
    return summary


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    observed_cols = [
        "Lot Area",
        "Year Built",
        "SalePrice",
        "Lot Config",
        "Neighborhood",
    ]
    compare_groups(df, "Lot Frontage", observed_cols)
    compare_groups(df, "Garage Yr Blt", observed_cols)