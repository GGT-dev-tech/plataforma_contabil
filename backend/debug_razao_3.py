import pandas as pd
from app.services.parsers.base import ImportAdapter
class Dummy(ImportAdapter):
    def can_parse(self, x,y): return True
    def parse(self, x,y,z): return True
adapter = Dummy()

df = pd.read_excel("Architecture/Razão SUCESSOR.xlsx", engine="calamine", header=None)
import re
current_date = True
for idx, row in df.iterrows():
    if idx == 8:
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        debito_str = str(row[10]).strip() if pd.notna(row[10]) else ""
        val_debito = adapter._parse_float(debito_str)
        cred_str = str(row[13]).strip() if pd.notna(row[13]) else ""
        val_cred = adapter._parse_float(cred_str)
        print(f"Row 8: deb={debito_str} -> {val_debito}, cred={cred_str} -> {val_cred}")
