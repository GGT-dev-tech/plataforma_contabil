import re

class CommonPatterns:
    DATE_PTBR = re.compile(r'(\d{2}/\d{2}/\d{4})')
    MONETARY = re.compile(r'-?\d{1,3}(?:\.\d{3})*,\d{2}') # Formato PT-BR comum (1.000,00)
    NUMERIC_ONLY = re.compile(r'[^0-9]')
