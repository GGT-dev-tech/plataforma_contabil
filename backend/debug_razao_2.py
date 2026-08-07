import pandas as pd
from app.services.parsers.base import ImportAdapter

class TestAdapter(ImportAdapter):
    def can_parse(self, f, t): return True
    def parse(self, f, db, e): pass

adapter = TestAdapter()
df = pd.read_excel("Architecture/Razão SUCESSOR.xlsx", engine="calamine", header=None)
current_date = None
import re
for idx, row in df.iterrows():
    col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
    if idx > 4 and idx < 15:
        print(f"Row {idx}: col0='{col0}'")
    if re.match(r'^\d{2}/\d{2}/\d{4}$', col0):
        print(f"Matched date: {col0}")
        parsed = adapter._parse_date(col0)
        if parsed: current_date = parsed
        continue
