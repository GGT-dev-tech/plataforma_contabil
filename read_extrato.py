import pandas as pd

def read_extrato(filepath):
    df = pd.read_excel(filepath, nrows=30)
    for i, row in df.iterrows():
        print(f"Row {i}: {row.tolist()}")

read_extrato("Architecture/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx")
