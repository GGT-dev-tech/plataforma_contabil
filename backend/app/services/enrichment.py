import re
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro
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
    def enrich_movimentacoes(movimentacoes: List[MovimentacaoFinanceira]):
        for mov in movimentacoes:
            features = EnrichmentFeatures()
            features.chave_pix = EnrichmentService.extract_pix_key(mov.descricao_extrato)
            features.cnpj_cpf = EnrichmentService.extract_cnpj(mov.descricao_extrato)
            features.numero_nf = EnrichmentService.extract_nf(mov.descricao_extrato)
            features.palavras_chave = EnrichmentService.tokenize(mov.descricao_extrato)
            
            # Fingerprint bancário básico (Data + Valor + Documento)
            target = mov.documento_banco or features.chave_pix or ""
            features.fingerprint_financeiro = EnrichmentService.generate_fingerprint(
                str(mov.data_transacao), str(abs(mov.valor)), target
            )
            
            mov._features = features

    @staticmethod
    def enrich_titulos(titulos: List[TituloFinanceiro]):
        for t in titulos:
            features = EnrichmentFeatures()
            if t.fornecedor_cliente_cnpj_cpf:
                features.cnpj_cpf = t.fornecedor_cliente_cnpj_cpf
            if t.fornecedor_cliente_nome:
                features.palavras_chave = EnrichmentService.tokenize(t.fornecedor_cliente_nome)
                
            features.fingerprint_financeiro = EnrichmentService.generate_fingerprint(
                str(t.data_vencimento), str(abs(t.valor_nominal)), str(features.palavras_chave)
            )
            
            t._features = features
