lear# HW5 report

## 1 Provenance
### Dataset
- Ames Housing Dataset (De Cock, 2011), containing `2930` home sales in Ames, Iowa from `2006` to `2010` across `82` columns.
### Source
- Downloaded once via `download.py` from `https://jse.amstat.org/v19n3/decock/AmesHousing.txt` to `raw/AmesHousing.txt`
- The raw data is never edited and any changes are to the cleaned file `processed/ames_cleaned.csv`
## 2 Validation: failures on the raw file

### Output of validation on raw file before cleaning
```
❯ python validate.py ../data/raw/AmesHousing.txt --raw
FAIL ../data/raw/AmesHousing.txt
Garage Yr Blt: 1 values outside [1870, 2010]
MS Zoning: 29 values not in {'C', 'FV', 'RL', 'I', 'RM', 'RP', 'RH', 'A'}
Bldg Type: 101 values not in {'Duplex', 'TwnhsI', 'TwnhsE', '1Fam', '2fmCon'}
Year Remodeled is before year built for 1 rows.
Year Sold is before year built for 1 rows.
```

### Fixes for each issue

| Issue | Fix Strategy |
| --- | --- |
| `Garage Yr Blt: 1 values outside [1870, 2010]` | Fix `2207` to `2007` as the year built was `2006` and year sold was `2007`. It must have been a typo. |
| `MS Zoning: 29 values not in {'C', 'FV', 'RL', 'I', 'RM', 'RP', 'RH', 'A'}` | The actual values that are outside these allowed values are `{'C (all)', 'I (all)', 'A (agr)'}`. Fix is to map `"C (all)" -> "C", "I (all)" -> "I", "A (agr)" -> "A"`. |
| `Bldg Type: 101 values not in {'Duplex', 'TwnhsI', 'TwnhsE', '1Fam', '2fmCon'}` | The only value that is outside these allowed values is `Twnhs`. Fix is to map `"Twnhs" -> "TwnhsI"`. |
| `Year Remodeled is before year built for 1 rows.` | For the one row, year remodeled is `2001` and year built is `2002`. The strategey used to fix is to swap the values. |
| `Year Sold is before year built for 1 rows.` | For the one row, year sold is `2007` and year built is `2008`. The strategey used to fix is to swap the values. |

### Output of validation after cleaning
```
❯ make validate
mkdir -p data/processed
python src/clean.py data/raw/AmesHousing.txt data/processed/ames_clean.csv
Number of exact duplicate rows: 0
Number of duplicate rows with same Order: 0
Number of duplicate rows with same PID: 0
Number of records before merging: 2930
Number of records after merging: 2930
Are any 'Neighborhood Full Name' values empty? False
Cleaned file saved to data/processed/ames_clean.csv
! python src/validate.py data/raw/AmesHousing.txt --raw
FAIL data/raw/AmesHousing.txt
Garage Yr Blt: 1 values outside [1870, 2010]
MS Zoning: 29 values not in {'RL', 'RH', 'I', 'FV', 'C', 'RP', 'A', 'RM'}
Bldg Type: 101 values not in {'TwnhsI', 'Duplex', '1Fam', '2fmCon', 'TwnhsE'}
Year Remodeled is before year built for 1 rows.
Year Sold is before year built for 1 rows.
python src/validate.py data/processed/ames_clean.csv
PASS data/processed/ames_clean.csv
```

## 3 Sentinels and structural absence
Loading `AmesHousing.txt` with default `pd.read_csv(path, sep="\t")` vs. `keep_default_na=False`:

| Value  | Columns Affected | Dictionary Meaning |
| --- | --- | --- |
| `"NA"` = structural absence ("none") | 14 columns: `Alley`, `Bsmt Qual`, `Bsmt Cond`, `Bsmt Exposure`, `BsmtFin Type 1`, `BsmtFin Type 2`, `Fireplace Qu`, `Garage Type`, `Garage Finish`, `Garage Qual`, `Garage Cond`, `Pool QC`, `Fence`, `Misc Feature` | "none" instead of `NaN` |
| `"NA"` = missing | `Mas Vnr Type` | "NA" and "" dedcoded to actual missing values |

## 4 Keys and duplicates

### Fix "Names" to "NAmes"
 - output before this fix
``` 
> python clean.py ../data/raw/AmesHousing.txt ../data/processed/ames_clean.csv
Number of exact duplicate rows: 0
Number of duplicate rows with same Order: 0
Number of duplicate rows with same PID: 0
Number of records before merging: 2930
Number of records after merging: 2930
Are any 'Neighborhood Full Name' values empty? True
```
 - The data dictionary says the mapping is "Names" -> "North Ames", but the actual value in the data is "NAmes". So we use "NAmes" in the mapping.
 - That fixes the 'Neighborhood Full Name" values to be not empty
 - output after this fix
 ```
 ❯ python clean.py ../data/raw/AmesHousing.txt ../data/processed/ames_clean.csv
Number of exact duplicate rows: 0
Number of duplicate rows with same Order: 0
Number of duplicate rows with same PID: 0
Number of records before merging: 2930
Number of records after merging: 2930
Are any 'Neighborhood Full Name' values empty? False
Cleaned file saved to ../data/processed/ames_clean.csv
 ```

### Validating the cleaned data
```
❯ python validate.py ../data/processed/ames_clean.csv
PASS ../data/processed/ames_clean.csv
```

### Keys & duplicates counts interpretation
 - `Order` is unique for each order (`0` exact duplicates, `0` `Order` duplicates across 2930 rows).
 - `PID` is also unique for every row.
 - The merge with 28 rows mapping also preserves all the 2930 rows.

## 5 Missingness mechanism
### Output of missingness.py
```
❯ python missingness.py ../data/processed/ames_clean.csv
490/2930 rows missing
Missing rows proportion: 0.17
Reference col: Lot Frontage
Summary:
         column   present_mean    absent_mean present_top absent_top
0      Lot Area    9709.522951   12330.969388                       
1    Year Built    1970.520902    1975.512245                       
2     SalePrice  180099.741803  184263.440816                       
3    Lot Config            NaN            NaN      Inside     Inside
4  Neighborhood            NaN            NaN       NAmes      NAmes

159/2930 rows missing
Missing rows proportion: 0.05
Reference col: Garage Yr Blt
Summary:
         column   present_mean    absent_mean present_top absent_top
0      Lot Area   10286.925659    7725.408805                       
1    Year Built    1972.926741    1943.974843                       
2     SalePrice  185111.697582  105584.540881                       
3    Lot Config            NaN            NaN      Inside     Inside
4  Neighborhood            NaN            NaN       NAmes    Edwards
```

### Observations
- About 17% of the rows have missing `Lot Frontage`
- Houses with missing `Lot Frontage` have a considerably more `Lot Area` than the ones that are not missing. `Year Built` and `SalePrice` aren't meaningfully different. Have to do hypothesis testing for more details.
- Since the missing values are strongly dependent on the lot area column, it is not `MCAR` and we model it as `MAR`
- About 5% of the rows have missing `Garage Yr Built`
- Houses with missing `Garage Yr Built` have a considerably lower `Lot Area` than the ones that are not missing. And `Year Built`, `Sale Price` are also significantly different. The top `Neighborhood` is also different for missing vs not missing. 
- Since the missing values are strongly dependent on the observed columns, it is not `MCAR` and we model it as `MAR`
- What the data can't tell us is if it is actually `MAR` or `MNAR` because the actual `Lot Frontage` values themselves are missing.
- If it were to be MNAR, it could potentially be that when the `Lot Frontage` is too small they chose to not report it.

## 6 Imputation strategy and defense (at most 150 words)
### Output of impute.py
```
❯ python impute.py ../data/processed/ames_clean.csv
                     std_before  std_after  corr_before  corr_after
median                23.365335  21.326422     0.491313    0.362758
neighborhood_median   23.365335  21.718453     0.491313    0.389108
```

### Defense
- We rejected `MCAR` for `Lot Frontage` in part 5 because of how missingness depended on the other observed columsn like `Neighborhood`, `Lot Config`, `Lot Area`, and `Year Built`. So if we are going with an `MAR` assumption, imputing based on an observed column Neighborhood makes a lot more sense instead of collapsing everything into one city wide median. We could have considered KNN Imputer using the 4 columns as features for finding the nearest neighbours and using their median. I chose neighborhood median fill for its simplicity. Global median fill also weakens the relationship.

## 7 Leakage-safe evaluation
### Output of evaluate.py
```
❯ python evaluate.py ../data/processed/ames_clean.csv
RMSE of variant A (Target leakage): 0.158851
RMSE of variant B (Contamination) : 0.158881
RMSE of variant C                 : 0.158898
```

### Observations
- Variant A has the smallest RMSE and it is expected because we are using the target information to fill the missing values (target leakage) and then using them to predict the target itself.
- Variant B has a smaller RMSE than variant C and that is also expected as we are using information from the validation/test set (contamination). So it performs better on the validation/test set.
- Variant C has expectedly the largest RMSE as it neither uses target information nor information from the test/validation set (honest).
- Variant A cannot be used on new data as it needs the output label.


## 8 What this data cannot tell you
- The data cannot tell us if it is actually `MNAR` or `MAR` as the actual values themselves are missing so we can't confirm that it is `MNAR` or not.