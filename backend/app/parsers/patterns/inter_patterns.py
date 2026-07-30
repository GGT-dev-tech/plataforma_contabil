import re

class InterPatterns:
    # Exemplo: "1 de Junho de 2026 Saldo do dia: R$ 34.255,05"
    DATA_HEADER = re.compile(r'^(\d{1,2}) de ([A-Za-zç]+) de (\d{4})')
    
    # Mapeamento de meses em português
    MESES = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    # Extração de código "Cp :..." ou chaves diversas
    CP_CODE = re.compile(r'Cp\s*:(\d+)-')
    
    # Pix extrator de nome
    PIX_NOME = re.compile(r'Pix [enviadorec]+: "(?:Cp\s*:\d+-)?(.*?)"', re.IGNORECASE)
