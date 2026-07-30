import re
import unicodedata

class NormalizationService:
    @staticmethod
    def normalize_fornecedor(nome: str) -> str:
        """
        Normaliza o nome de um fornecedor:
        - Maiúsculo
        - Remove acentos
        - Remove caracteres não alfanuméricos
        - Remove sufixos societários e preposições comuns (LTDA, ME, S A, DE)
        """
        if not nome:
            return ""
            
        val = str(nome).upper()
        # Remove acentos
        val = ''.join(c for c in unicodedata.normalize('NFD', val) if unicodedata.category(c) != 'Mn')
        # Remove especiais
        val = re.sub(r'[^A-Z0-9\s]', '', val)
        # Remove sufixos e preposições (isoladas)
        val = re.sub(r'\b(LTDA|ME|EIRELI|SA|S A|DE|DA|DO|DAS|DOS)\b', '', val).strip()
        # Remove espaços duplos
        return re.sub(r'\s+', ' ', val)
