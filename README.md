HW5: Ames Housing quality audit
How to run
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
Provenance (Part 1)
Item	Value
Source URL	https://jse.amstat.org/v19n3/decock/AmesHousing.txt
Downloaded on	Nov 24th 2026
Citation	De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. Journal of Statistics Education, 19(3).
Data dictionary	https://jse.amstat.org/v19n3/decock/DataDocumentation.txt
Terms of use	Educational & Research use
Rows, columns on arrival	2930 x 82
Features used in Part 7
The regression model in src/evaluate.py uses 13 numeric features (NUMERIC_FEATURES):

Lot and location adjacent size: Lot Frontage, Lot Area
Overall quality and condition: Overall Qual, Overall Cond
Age and renovation: Year Built, Year Remod/Add
Interior and basement square footage: Total Bsmt SF, 1st Flr SF, 2nd Flr SF, Gr Liv Area
Rooms and garage capacity: Full Bath, Garage Cars, Garage Area
Reasons

Lot Frontage is required by the assignment.
The remaining 12 numeric columns majorly attribute towards the prices and sales of residential houses.
AI assistance
I used AI for bug fixes and certain code snippets which I clearly marked as "AI generated" in a comment above the corresponding 4 code snippets in clean.py, evaluate.py, impute.py. The tool I used is Google Gemini.
