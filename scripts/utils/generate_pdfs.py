import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def format_currency(val_str):
    try:
        v = float(val_str)
        # Format as R$ XX.XXX,XX
        s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"-R$ {s}" if v < 0 else f"R$ {s}"
    except:
        return val_str

def csv_to_pdf(csv_file, pdf_file, title):
    c = canvas.Canvas(pdf_file, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, title)
    
    c.setFont("Helvetica", 12)
    y = 760
    
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = row.get('Data', row.get('Data Lançamento', ''))
            hist = row.get('Histórico', row.get('Histórico/Fornecedor', ''))
            val = row.get('Valor', row.get('Valor Débito', ''))
            
            if not val:
                val = row.get('Valor Crédito', '0.00')
                if val != '0.00' and float(val) > 0:
                    val = str(float(val))
                elif row.get('Valor Débito') and float(row.get('Valor Débito', 0)) > 0:
                    val = str(-float(row.get('Valor Débito')))
            
            val_fmt = format_currency(val)
            line = f"{data}    {hist}    {val_fmt}"
            
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 800
                
    c.save()

if __name__ == "__main__":
    csv_to_pdf("test_data/extrato_sample.csv", "test_data/extrato_sample.pdf", "Extrato Bancário")
    csv_to_pdf("test_data/razao_sample.csv", "test_data/razao_sample.pdf", "Razão Contábil - Sucessor")
    print("PDFs gerados com sucesso!")
