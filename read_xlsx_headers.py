import pandas as pd

def show_headers(filepath):
    print(f"\n--- {filepath} ---")
    try:
        df = pd.read_excel(filepath, nrows=10)
        print("Colunas iniciais:", df.columns.tolist())
        print("Primeiras 3 linhas:")
        print(df.head(3).to_string())
    except Exception as e:
        print(f"Erro: {e}")

show_headers("Architecture/Despesas 06-2026.xlsx")
show_headers("Architecture/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx")
show_headers("Architecture/Razão SUCESSOR.xlsx")
