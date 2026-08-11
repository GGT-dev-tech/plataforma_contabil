import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import re

def create_pdf(lines, pdf_file, title):
    c = canvas.Canvas(pdf_file, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, title)
    
    c.setFont("Helvetica", 10)
    y = 760
    
    for line in lines:
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = 800
            
    c.save()

if __name__ == "__main__":
    os.makedirs("test_data/real", exist_ok=True)
    
    # 1. Extrato Inter
    extrato_file = "backend/tests/fixtures/production_sample/Extrato-01-06-2026-a-30-06-2026-PDF.xlsx"
    df_extrato = pd.read_excel(extrato_file, engine='calamine', header=None)
    
    extrato_lines = []
    current_date = "01/06/2026"
    for idx, row in df_extrato.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        col1 = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else ""
        
        # Fake formatting date for pdf parser
        # The generic PDF parser looks for \d{2}/\d{2}/\d{4} and R$ value
        # We will format it exactly like that: DD/MM/YYYY   Desc   R$ Val
        # If it's an Inter Date (e.g. 1 de Junho de 2026), we'll try to extract date or just use current
        if "de 2026" in col0:
            match = re.search(r'(\d+)\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})', col0, re.IGNORECASE)
            if match:
                day = int(match.group(1))
                current_date = f"{day:02d}/06/2026" # Hardcode month for simplicity
            continue
            
        if col1 and any(c.isdigit() for c in col1):
            val_str = str(col1).replace("-R$", "R$ -").replace("R$", "").strip()
            # It's a float or string, we just append it
            extrato_lines.append(f"{current_date}   {col0[:60]}   R$ {val_str}")
            
    create_pdf(extrato_lines, "test_data/real/extrato_real.pdf", "Extrato Bancario")
    
    # 2. Razão Sucessor
    razao_file = "backend/tests/fixtures/production_sample/Razão SUCESSOR.xlsx"
    df_razao = pd.read_excel(razao_file, engine='calamine', header=None)
    
    razao_lines = []
    current_date = "01/06/2026"
    for idx, row in df_razao.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        
        if re.match(r'^\d{2}/\d{2}/\d{4}$', col0):
            current_date = col0
            continue
            
        if not col0 or col0 == "Histórico" or "Saldo" in col0:
            continue
            
        debito = str(row[10]).strip() if len(row) > 10 and pd.notna(row[10]) else ""
        credito = str(row[13]).strip() if len(row) > 13 and pd.notna(row[13]) else ""
        
        val = 0
        try:
            if debito: val = float(debito)
            elif credito: val = float(credito)
        except:
            pass
            
        if val > 0:
            val_fmt = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            razao_lines.append(f"{current_date}   {col0[:60]}   {val_fmt}")
            
    create_pdf(razao_lines, "test_data/real/razao_real.pdf", "Razao Sucessor")
    
    print("PDFs reais criados em test_data/real/!")
