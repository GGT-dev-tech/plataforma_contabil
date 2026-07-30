import re
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.domain import MovimentacaoBancaria, ParcelaDespesa, Fornecedor
from app.services.normalization import NormalizationService

class EnrichmentFeatures:
    """Features injetadas dinamicamente nas entidades canônicas (em memória)."""
    def __init__(self):
        self.chave_pix: Optional[str] = None
        self.cnpj_cpf: Optional[str] = None
        self.numero_nf: Optional[str] = None
        self.palavras_chave: List[str] = []
        self.fingerprint_financeiro: str = ""

class EnrichmentService:
    @staticmethod
    def extract_pix_key(historico: str) -> Optional[str]:
        # Tenta achar CPFs ou emails mascarados ou explícitos
        match = re.search(r'Pix [enviadorec]+: "(?:Cp\s*:\d+-)?(.*?)"', historico, re.IGNORECASE)
        if match:
            # Não é exatamente a chave PIX, mas o nome do recebedor que o Inter coloca no lugar da chave muitas vezes
            return NormalizationService.normalize_fornecedor(match.group(1))
        return None

    @staticmethod
    def extract_cnpj(text: str) -> Optional[str]:
        match = re.search(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b', text)
        return match.group(0) if match else None

    @staticmethod
    def extract_nf(text: str) -> Optional[str]:
        match = re.search(r'\bNF\s*(\d+)\b', text, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def tokenize(text: str) -> List[str]:
        clean = NormalizationService.normalize_fornecedor(text)
        return clean.split() if clean else []

    @staticmethod
    def generate_fingerprint(data: str, valor: str, target: str) -> str:
        raw = f"{data}|{valor}|{target}".encode('utf-8')
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def enrich_movimentacoes(movimentacoes: List[MovimentacaoBancaria]):
        for mov in movimentacoes:
            features = EnrichmentFeatures()
            features.chave_pix = EnrichmentService.extract_pix_key(mov.historico)
            features.cnpj_cpf = EnrichmentService.extract_cnpj(mov.historico)
            features.numero_nf = EnrichmentService.extract_nf(mov.historico)
            features.palavras_chave = EnrichmentService.tokenize(mov.historico)
            
            # Fingerprint bancário básico (Data + Valor + CP/Chave)
            target = mov.codigo_cp or features.chave_pix or ""
            features.fingerprint_financeiro = EnrichmentService.generate_fingerprint(
                str(mov.data), str(abs(mov.valor)), target
            )
            
            mov._features = features

    @staticmethod
    def enrich_parcelas(parcelas: List[ParcelaDespesa], fornecedores_dict: dict):
        for p in parcelas:
            features = EnrichmentFeatures()
            fornecedor = fornecedores_dict.get(p.despesa.fornecedor_id)
            if fornecedor:
                features.cnpj_cpf = fornecedor.cnpj_cpf # Pode ser None
                features.palavras_chave = EnrichmentService.tokenize(fornecedor.nome_normalizado)
                
            features.fingerprint_financeiro = EnrichmentService.generate_fingerprint(
                str(p.data_vencimento), str(abs(p.valor)), str(features.palavras_chave)
            )
            
            p._features = features
