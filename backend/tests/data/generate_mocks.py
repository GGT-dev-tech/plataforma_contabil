import os
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def create_pdf_mock():
    filepath = os.path.join(DATA_DIR, 'extrato_mock.pdf')
    c = canvas.Canvas(filepath)
    c.drawString(100, 800, "Extrato Bancário Genérico")
    c.drawString(100, 780, "20/10/2026 - Pagamento Boleto R$ 1500,00")
    c.drawString(100, 760, "21/10/2026 - Transferencia PIX R$ 250,50")
    c.drawString(100, 740, "22/10/2026 - Tarifa Bancaria R$ 15,00")
    c.save()
    print(f"Gerado: {filepath}")

def create_xml_mock():
    filepath = os.path.join(DATA_DIR, 'nf_mock.xml')
    
    nfe = ET.Element('NFe')
    inf = ET.SubElement(nfe, 'infNFe')
    
    ide = ET.SubElement(inf, 'ide')
    dhEmi = ET.SubElement(ide, 'dhEmi')
    dhEmi.text = '2026-10-25T14:30:00-03:00'
    
    emit = ET.SubElement(inf, 'emit')
    xNome = ET.SubElement(emit, 'xNome')
    xNome.text = 'Fornecedor de Tecnologia SA'
    
    total = ET.SubElement(inf, 'total')
    vNF = ET.SubElement(total, 'vNF')
    vNF.text = '3500.00'
    
    tree = ET.ElementTree(nfe)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)
    print(f"Gerado: {filepath}")

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    create_pdf_mock()
    create_xml_mock()
