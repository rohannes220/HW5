"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

NA_MEANS_NONE: list[str] = [
    "Alley",
    "Bsmt Qual",
    "Bsmt Cond",
    "Bsmt Exposure",
    "BsmtFin Type 1",
    "BsmtFin Type 2",
    "Fireplace Qu",
    "Garage Type",
    "Garage Finish",
    "Garage Qual",
    "Garage Cond",
    "Pool QC",
    "Fence",
    "Misc Feature",
]

NUMERIC_COLUMNS = [
    "Order",
    "PID",
    "MS SubClass",
    "Lot Frontage",
    "Lot Area",
    "Overall Qual",
    "Overall Cond",
    "Year Built",
    "Year Remod/Add",
    "Mas Vnr Area",
    "BsmtFin SF 1",
    "BsmtFin SF 2",
    "Bsmt Unf SF",
    "Total Bsmt SF",
    "1st Flr SF",
    "2nd Flr SF",
    "Low Qual Fin SF",
    "Gr Liv Area",
    "Bsmt Full Bath",
    "Bsmt Half Bath",
    "Full Bath",
    "Half Bath",
    "Bedroom AbvGr",
    "Kitchen AbvGr",
    "TotRms AbvGrd",
    "Fireplaces",
    "Garage Yr Blt",
    "Garage Cars",
    "Garage Area",
    "Wood Deck SF",
    "Open Porch SF",
    "Enclosed Porch",
    "3Ssn Porch",
    "Screen Porch",
    "Pool Area",
    "Misc Val",
    "Mo Sold",
    "Yr Sold",
    "SalePrice",
]


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", keep_default_na=False)


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()

    for col in NUMERIC_COLUMNS:
        copy[col] = pd.to_numeric(copy[col], errors="coerce")

    copy = copy.replace(r"^\s*$", np.nan, regex=True)

    copy["Mas Vnr Type"] = copy["Mas Vnr Type"].replace({"NA": np.nan})

    for col in NA_MEANS_NONE:
        copy[col] = copy[col].replace({"NA": "none"})

    copy.loc[copy["Garage Yr Blt"] == 2207, "Garage Yr Blt"] = 2007

    copy["MS Zoning"] = copy["MS Zoning"].replace(
        {"C (all)": "C", "I (all)": "I", "A (agr)": "A"}
    )

    copy["Bldg Type"] = copy["Bldg Type"].replace({"Twnhs": "TwnhsI"})

    out_of_order = copy["Year Remod/Add"] < copy["Year Built"]
    copy.loc[out_of_order, "Year Remod/Add"], copy.loc[out_of_order, "Year Built"] = (
        copy.loc[out_of_order, "Year Built"],
        copy.loc[out_of_order, "Year Remod/Add"],
    )

    out_of_order = copy["Yr Sold"] < copy["Year Built"]
    copy.loc[out_of_order, "Yr Sold"], copy.loc[out_of_order, "Year Built"] = (
        copy.loc[out_of_order, "Year Built"],
        copy.loc[out_of_order, "Yr Sold"],
    )

    return copy


def check_keys(df: pd.DataFrame) -> None:
    exact_duplicates = int(df.duplicated().sum())
    print(f"Number of exact duplicate rows: {exact_duplicates}")

    order_duplicates = int(df.duplicated(subset=["Order"]).sum())
    pid_duplicates = int(df.duplicated(subset=["PID"]).sum())
    print(f"Number of duplicate rows with same Order: {order_duplicates}")
    print(f"Number of duplicate rows with same PID: {pid_duplicates}")
    assert (
        order_duplicates == 0
    ), f"Order should be unique. Num order duplicates: {order_duplicates}"

    neighborhood_mapping = pd.DataFrame(
        [
            ("Blmngtn", "Bloomington Heights"),
            ("Blueste", "Bluestem"),
            ("BrDale", "Briardale"),
            ("BrkSide", "Brookside"),
            ("ClearCr", "Clear Creek"),
            ("CollgCr", "College Creek"),
            ("Crawfor", "Crawford"),
            ("Edwards", "Edwards"),
            ("Gilbert", "Gilbert"),
            ("Greens", "Greens"),
            ("GrnHill", "Green Hills"),
            ("IDOTRR", "Iowa DOT and Rail Road"),
            ("Landmrk", "Landmark"),
            ("MeadowV", "Meadow Village"),
            ("Mitchel", "Mitchell"),
            ("NAmes", "North Ames"),
            ("NoRidge", "Northridge"),
            ("NPkVill", "Northpark Villa"),
            ("NridgHt", "Northridge Heights"),
            ("NWAmes", "Northwest Ames"),
            ("OldTown", "Old Town"),
            ("SWISU", "South & West of Iowa State University"),
            ("Sawyer", "Sawyer"),
            ("SawyerW", "Sawyer West"),
            ("Somerst", "Somerset"),
            ("StoneBr", "Stone Brook"),
            ("Timber", "Timberland"),
            ("Veenker", "Veenker"),
        ],
        columns=("Neighborhood", "Neighborhood Full Name"),
    )

    num_records_before_merge = len(df)
    merged = pd.merge(
        df, neighborhood_mapping, on="Neighborhood", how="left", validate="many_to_one"
    )
    num_records_after_merge = len(merged)
    print(f"Number of records before merging: {num_records_before_merge}")
    print(f"Number of records after merging: {num_records_after_merge}")
    assert (
        num_records_before_merge == num_records_after_merge
    ), f"Number of records should be same before and after merge"

    print(
        f"Are any 'Neighborhood Full Name' values empty? {merged['Neighborhood Full Name'].isna().any()}"
    )
    assert not merged["Neighborhood Full Name"].isna().any()


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]

    df = decode_missing(load_raw(raw_path))
    check_keys(df)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Cleaned file saved to {out_path}")