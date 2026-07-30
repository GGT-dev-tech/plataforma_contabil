import re

class SciPatterns:
    # Captura cabeçalho de conta: "85 - INTER - 01.1.1.02.004 Banco Inter"
    CONTA_HEADER = re.compile(r'^(\d+)\s*-\s*(.*?)\s*-\s*([\d\.]+)\s*(.*)$')
    
    # Captura data isolada: "01/06/2026"
    DATA_ISOLADA = re.compile(r'^(\d{2}/\d{2}/\d{4})$')
    
    # Captura valores monetários (ex: 33.139,35D ou 1.392,20 ou 33.139,35C)
    MONEY = re.compile(r'^\s*([\d\.]+,\d{2})([DC])?\s*$')
    
    # Palavras de cabeçalho (para pular)
    IGNORAR_HEADERS = ["Histórico", "Lote", "Chave", "Contra", "Débito", "Crédito", "Saldo atual", "Saldo anterior:"]
