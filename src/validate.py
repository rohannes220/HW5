"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""

import sys

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

# source: data dictionary
ALL_COLUMNS = [
    "Order",
    "PID",
    "MS SubClass",
    "MS Zoning",
    "Lot Frontage",
    "Lot Area",
    "Street",
    "Alley",
    "Lot Shape",
    "Land Contour",
    "Utilities",
    "Lot Config",
    "Land Slope",
    "Neighborhood",
    "Condition 1",
    "Condition 2",
    "Bldg Type",
    "House Style",
    "Overall Qual",
    "Overall Cond",
    "Year Built",
    "Year Remod/Add",
    "Roof Style",
    "Roof Matl",
    "Exterior 1st",
    "Exterior 2nd",
    "Mas Vnr Type",
    "Mas Vnr Area",
    "Exter Qual",
    "Exter Cond",
    "Foundation",
    "Bsmt Qual",
    "Bsmt Cond",
    "Bsmt Exposure",
    "BsmtFin Type 1",
    "BsmtFin SF 1",
    "BsmtFin Type 2",
    "BsmtFin SF 2",
    "Bsmt Unf SF",
    "Total Bsmt SF",
    "Heating",
    "Heating QC",
    "Central Air",
    "Electrical",
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
    "Kitchen Qual",
    "TotRms AbvGrd",
    "Functional",
    "Fireplaces",
    "Fireplace Qu",
    "Garage Type",
    "Garage Yr Blt",
    "Garage Finish",
    "Garage Cars",
    "Garage Area",
    "Garage Qual",
    "Garage Cond",
    "Paved Drive",
    "Wood Deck SF",
    "Open Porch SF",
    "Enclosed Porch",
    "3Ssn Porch",
    "Screen Porch",
    "Pool Area",
    "Pool QC",
    "Fence",
    "Misc Feature",
    "Misc Val",
    "Mo Sold",
    "Yr Sold",
    "Sale Type",
    "Sale Condition",
    "SalePrice",
]

# source: data dictionary
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


class ValidationError(Exception):
    pass


# Each rule needs a source. Put it in the comment.
# atleast 8 range rules are required
RANGES = {
    # source: data dictionary
    # Overall Qual (Ordinal)
    "Overall Qual": (1, 10),
    # source: data dictionary
    # Overall Cond (Ordinal)
    "Overall Cond": (1, 10),
    # source: data dictionary
    # sold in Ames, IA from 2006 to 2010
    "Yr Sold": (2006, 2010),
    # source: month can only be in [1, 12]
    "Mo Sold": (1, 12),
    # source: historical bound of 1870 and 2010 from data dictionary
    # as the houses are sold in [2006, 2010] so they can't be built after 2010
    "Year Built": (1870, 2010),
    # source: similar to "Year Built"
    "Year Remod/Add": (1870, 2010),
    # source: similar to "Year Built"
    "Garage Yr Blt": (1870, 2010),
    # source: "SalePrice" has to be positive and
    # assuming an economic upper limit of $10 million for houses sold in [2006, 2010]
    "SalePrice": (1, 10_000_000),
}

# atleast 4 allowed rules are required
ALLOWED = {
    # source: data dictionary
    # Street (Nominal)
    "Street": {"Grvl", "Pave"},
    # source: data dictionary
    # Central Air (Nominal)
    "Central Air": {"N", "Y"},
    # source: data dictionary
    # MS Zoning (Nominal)
    "MS Zoning": {
        "A",
        "C",
        "FV",
        "I",
        "RH",
        "RL",
        "RP",
        "RM",
    },
    # source: data dictionary
    # Bldg Type (Nominal)
    "Bldg Type": {
        "1Fam",
        "2fmCon",
        "Duplex",
        "TwnhsE",
        "TwnhsI",
    },
    # source: data dictionary, Paved Drive (Nominal)
    "Paved Drive": {"Y", "P", "N"},
}


def check_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema failures: missing or extra columns, wrong dtype families."""

    # check if all the columns exactly match
    errors = []
    all_columns_set = set(ALL_COLUMNS)
    df_columns_set = set(df.columns)
    if not df_columns_set.issubset(all_columns_set):
        errors.append(f"Extra columns: {df_columns_set.difference(all_columns_set)}")
    if not all_columns_set.issubset(df_columns_set):
        errors.append(f"Missing columns: {all_columns_set.difference(df_columns_set)}")

    # check the data types of the columns
    for col in ALL_COLUMNS:
        # at this point there could be missing columns, so we check
        if col not in df_columns_set:
            continue

        # at this point the col is present in the df
        # if it is a numeric column, it's dtype should be numeric
        if col in NUMERIC_COLUMNS:
            if not is_numeric_dtype(df[col]):
                errors.append(f"{col} is supposed to be numeric but is {df[col].dtype}")
            continue

        # at this point it has to be a non-numeric column
        if not is_string_dtype(df[col]) and not (df[col].dtype == "object"):
            errors.append(f"{col} is supposed to be text but is {df[col].dtype}")

    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Return one message per column with values outside its range. NaN is not judged here."""

    # for each column, we check if the values are in the appropriate range
    errors = []
    for col, (lo, hi) in RANGES.items():
        # at this point there could be missing columns, so we check
        if col not in df.columns:
            continue

        present = df[col].notna()
        outside = ~df[col].between(lo, hi)
        bad = present & outside
        if bad.any():
            errors.append(f"{col}: {bad.sum()} values outside [{lo}, {hi}]")
    return errors


def check_allowed(df: pd.DataFrame) -> list[str]:
    """Return one message per categorical column with values not in the dictionary."""

    # for each column, we check if the values are only the allowed ones
    errors = []
    for col, allowed_values in ALLOWED.items():
        # at this point there could be missing columns, so we check
        if col not in df.columns:
            continue

        present = df[col].notna()
        contains_not_allowed = ~df[col].isin(allowed_values)
        bad = present & contains_not_allowed
        if bad.any():
            errors.append(f"{col}: {bad.sum()} values not in {allowed_values}")
    return errors


# atleast 1 cross column rule is required
def check_cross_column(df: pd.DataFrame) -> list[str]:
    """Return failures of rules that involve two or more columns."""

    # all the errors
    errors = []

    # make sure that the basement areas add up to the total basement area
    # we will only do this check if all the columns are present
    # otherwise it will throw an error
    basement_columns = ["BsmtFin SF 1", "BsmtFin SF 2", "Bsmt Unf SF", "Total Bsmt SF"]
    if set(basement_columns).issubset(df.columns):
        type1_sf = pd.to_numeric(df[basement_columns[0]], errors="coerce")
        type2_sf = pd.to_numeric(df[basement_columns[1]], errors="coerce")
        unfinished_sf = pd.to_numeric(df[basement_columns[2]], errors="coerce")
        total_sf = pd.to_numeric(df[basement_columns[3]], errors="coerce")

        present = (
            type1_sf.notna()
            & type2_sf.notna()
            & unfinished_sf.notna()
            & total_sf.notna()
        )
        bad = present & ~np.isclose(type1_sf + type2_sf + unfinished_sf, total_sf)
        if bad.any():
            errors.append(f"Basement areas don't add up for {bad.sum()} rows.")

    # year that it was rebuilt/additions can't be before the year it was built
    # we will only do this check if all the columns are present
    # otherwise it will throw an error
    if {"Year Built", "Year Remod/Add"}.issubset(df.columns):
        year_built = pd.to_numeric(df["Year Built"], errors="coerce")
        year_remod = pd.to_numeric(df["Year Remod/Add"], errors="coerce")

        present = year_built.notna() & year_remod.notna()
        bad = present & (year_built > year_remod)
        if bad.any():
            errors.append(f"Year Remodeled is before year built for {bad.sum()} rows.")

    # year that it was sold can't be before the year it was built
    # we will only do this check if all the columns are present
    # otherwise it will throw an error
    if {"Year Built", "Yr Sold"}.issubset(df.columns):
        year_built = pd.to_numeric(df["Year Built"], errors="coerce")
        year_sold = pd.to_numeric(df["Yr Sold"], errors="coerce")

        present = year_built.notna() & year_sold.notna()
        bad = present & (year_built > year_sold)
        if bad.any():
            errors.append(f"Year Sold is before year built for {bad.sum()} rows.")

    # return the errors
    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = (
        check_schema(df) + check_ranges(df) + check_allowed(df) + check_cross_column(df)
    )
    if errors:
        raise ValidationError("\n".join(errors))
    return df


if __name__ == "__main__":
    path = sys.argv[1]
    raw = "--raw" in sys.argv
    df = pd.read_csv(
        path, sep="\t" if raw else ",", keep_default_na=False, na_values=[""]
    )
    try:
        validate(df)
        print(f"PASS {path}")
    except ValidationError as e:
        print(f"FAIL {path}\n{e}")
        sys.exit(1)