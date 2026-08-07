import logging
from app.services.parsers.razao_sucessor import RazaoSucessorAdapter
from app.api.deps import SessionLocal
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
db = SessionLocal()
adapter = RazaoSucessorAdapter()

df = pd.read_excel("Architecture/Razão SUCESSOR.xlsx", engine="calamine", header=None)
current_date = None
import re
novos = 0
for idx, row in df.iterrows():
    col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
    if re.match(r'^\d{2}/\d{2}/\d{4}$', col0):
        parsed = adapter._parse_date(col0)
        if parsed:
            current_date = parsed
        continue
    if not current_date:
        continue
    if not col0 or col0 == "Histórico" or "Saldo" in col0 or col0.startswith("EMPRESA"):
        continue
    
    deb = str(row[10]).strip() if pd.notna(row[10]) else ""
    val_deb = adapter._parse_float(deb)
    
    cred = str(row[13]).strip() if pd.notna(row[13]) else ""
    val_cred = adapter._parse_float(cred)
    
    if val_deb > 0 or val_cred > 0:
        print(f"Row {idx} is valid! val_deb={val_deb}, val_cred={val_cred}")
        novos += 1

print("Total novos com valor:", novos)
