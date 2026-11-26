"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""

import sys

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline

# 8 to 15 columns, including "Lot Frontage"
NUMERIC_FEATURES: list[str] = [
    "Lot Frontage",
    "Lot Area",
    "Overall Qual",
    "Overall Cond",
    "Year Built",
    "Year Remod/Add",
    "Total Bsmt SF",
    "1st Flr SF",
    "2nd Flr SF",
    "Gr Liv Area",
    "Full Bath",
    "Garage Cars",
    "Garage Area",
]
CV = KFold(n_splits=5, shuffle=True, random_state=5110)


# AI generated
# custom class for neighborhood wise median fill strategy for Lot Frontage
class NeighborhoodMedianImputer(BaseEstimator, TransformerMixin):
    def __init__(self, fill_col: str = "Lot Frontage", using: str = "Neighborhood"):
        self.fill_col = fill_col
        self.using = using

    def fit(self, X: pd.DataFrame, y = None):
        self.global_median_ = float(X[self.fill_col].median())
        self.group_medians_ = X.groupby(self.using)[self.fill_col].median().to_dict()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        out = X.copy()
        mapped = out[self.using].map(self.group_medians_).fillna(self.global_median_)
        out[self.fill_col] = out[self.fill_col].fillna(mapped)
        return out


# AI generated
def make_model_step() -> Pipeline:
    """Select NUMERIC_FEATURES (with a fallback median imputer for any other NaNs) + OLS."""
    selector = ColumnTransformer(
        transformers=[("num", SimpleImputer(strategy="median"), NUMERIC_FEATURES)],
        remainder="drop",
    )
    return Pipeline(
        [
            ("select", selector),
            ("reg", LinearRegression()),
        ]
    )


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(
        estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error"
    ).mean()


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])

    # get the features and the labels
    # we also add Neighborhood feature as it is used for a median fill strategy
    # it is ok as we drop the remaining non-numeric cols
    # in ColumnTransformer(.. remainder="drop")
    X = df[NUMERIC_FEATURES + ["Neighborhood"]]
    y = np.log(df["SalePrice"])

    # variant A: median "Lot Frontage" with each quintile of "Sale Price" on full table
    # create copy of features
    X_a = X.copy()
    quintiles = pd.qcut(y, q=5)
    X_a["Lot Frontage"] = X_a["Lot Frontage"].fillna(
        X_a.groupby(quintiles, observed=False)["Lot Frontage"].transform("median")
    )
    rmse_a = rmse(make_model_step(), X_a, y)

    # variant B: neighborhood wise median Lot Frontage (my part 6 strategy) filled
    # using the whole table before cross validation
    X_b = NeighborhoodMedianImputer().fit_transform(X)
    rmse_b = rmse(make_model_step(), X_b, y)

    # variant C: neighborhood wise median Lot Frontage (my part 6 strategy) filled
    # inside a pipeline
    pipeline_c = Pipeline(
        [
            ("imp", NeighborhoodMedianImputer()),
            ("model", make_model_step()),
        ]
    )
    rmse_c = rmse(pipeline_c, X, y)

    # print summary of RMSE values
    print(f"RMSE of variant A (Target leakage): {rmse_a:.8f}")
    print(f"RMSE of variant B (Contamination): {rmse_b:.8f}")
    print(f"RMSE of variant C: {rmse_c:.8f}")