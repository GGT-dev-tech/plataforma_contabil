from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass
from datetime import date, timedelta
from app.models.domain import MovimentacaoBancaria, ParcelaDespesa, LancamentoContabil
import difflib

@dataclass
class RuleResult:
    score: float # 0 a 100
    confidence: float # 0.0 a 1.0
    weight: float # multiplicador de agregacao
    reason: str

class IMatchingRule(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass
    
    @property
    @abstractmethod
    def weight(self) -> float: pass

    @abstractmethod
    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        pass

class ValueRule(IMatchingRule):
    def __init__(self, tolerance_cents: Decimal = Decimal('0.01'), weight: float = 2.0):
        self._weight = weight
        self.tolerance = tolerance_cents

    @property
    def name(self) -> str: return "ValueRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        # Pega valor da parcela ou lancamento
        target_val = abs(parcela.valor) if parcela else (abs(lanc.valor) if lanc else Decimal('0.0'))
        mov_val = abs(mov.valor)
        
        diff = abs(target_val - mov_val)
        
        if diff == 0:
            return RuleResult(score=100.0, confidence=1.0, weight=self.weight, reason="Match exato de valor")
        elif diff <= self.tolerance:
            return RuleResult(score=95.0, confidence=0.9, weight=self.weight, reason=f"Match de valor com tolerancia de {diff}")
        
        # Penalti exponencial se diferir muito
        score = max(0.0, 100.0 - float(diff)*10)
        return RuleResult(score=score, confidence=0.5, weight=self.weight, reason=f"Diferença de valor: {diff}")

class LancamentoValueRule(IMatchingRule):
    def __init__(self, weight: float = 2.0):
        self._weight = weight

    @property
    def name(self) -> str: return "LancamentoValueRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        if not lanc:
            return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Sem lancamento")
        
        diff = abs(abs(lanc.valor) - abs(mov.valor))
        if diff == 0:
            return RuleResult(score=100.0, confidence=1.0, weight=self.weight, reason="Match exato de valor lancamento")
        
        score = max(0.0, 100.0 - float(diff) * 5)
        return RuleResult(score=score, confidence=0.6, weight=self.weight, reason=f"Diferença de valor lancamento: {diff}")

class DateRule(IMatchingRule):
    def __init__(self, tolerance_days: int = 2, weight: float = 1.5):
        self._weight = weight
        self.tolerance = timedelta(days=tolerance_days)

    @property
    def name(self) -> str: return "DateRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        target_date = parcela.data_vencimento if parcela else (lanc.data if lanc else None)
        if not target_date or not mov.data:
            return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Data ausente")
            
        diff = abs((target_date - mov.data).days)
        
        if diff == 0:
            return RuleResult(score=100.0, confidence=1.0, weight=self.weight, reason="Datas coincidem")
        elif diff <= self.tolerance.days:
            # -10 pts por dia de diferenca
            return RuleResult(score=100.0 - (diff * 10), confidence=0.8, weight=self.weight, reason=f"Diferença de {diff} dia(s)")
            
        return RuleResult(score=0.0, confidence=0.1, weight=self.weight, reason=f"Data muito distante ({diff} dias)")

class LancamentoDateRule(IMatchingRule):
    def __init__(self, weight: float = 1.5):
        self._weight = weight

    @property
    def name(self) -> str: return "LancamentoDateRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        if not lanc or not lanc.data or not mov.data:
            return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Data ausente")
        
        diff = abs((lanc.data - mov.data).days)
        if diff <= 1:
            return RuleResult(score=100.0, confidence=0.9, weight=self.weight, reason="Data lancamento próxima")
        
        return RuleResult(score=max(0.0, 100.0 - (diff * 20)), confidence=0.4, weight=self.weight, reason=f"Distancia de {diff} dias")

class FornecedorNameRule(IMatchingRule):
    def __init__(self, weight: float = 1.0, threshold: float = 0.6):
        self._weight = weight
        self.threshold = threshold

    @property
    def name(self) -> str: return "FornecedorNameRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        s1 = (parcela.fornecedor.nome if parcela and parcela.fornecedor else "").lower()
        s2 = (mov.descricao or "").lower()
        
        if not s1 or not s2:
            return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Sem nomes para comparar")
        
        similarity = difflib.SequenceMatcher(None, s1, s2).ratio()
        if similarity >= self.threshold:
            return RuleResult(score=similarity * 100, confidence=similarity, weight=self.weight, reason="Match de nome fornecedor")
        
        return RuleResult(score=0.0, confidence=0.2, weight=self.weight, reason="Nome fornecedor incompativel")

class PixRule(IMatchingRule):
    def __init__(self, weight: float = 3.0):
        self._weight = weight

    @property
    def name(self) -> str: return "PixRule"
    
    @property
    def weight(self) -> float: return self._weight

    def evaluate(self, parcela: Optional[ParcelaDespesa], mov: MovimentacaoBancaria, lanc: Optional[LancamentoContabil]) -> RuleResult:
        # Somente avalia se houver extracao de PIX ou features táticas no Staging
        # features do enrichment
        mov_f = getattr(mov, '_features', None)
        parc_f = getattr(parcela, '_features', None) if parcela else None
        
        if not mov_f or not parc_f:
            return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Sem features de enrichment para PIX")
            
        # Match por CPF/CNPJ
        if mov_f.cnpj_cpf and parc_f.cnpj_cpf:
            if mov_f.cnpj_cpf == parc_f.cnpj_cpf:
                return RuleResult(score=100.0, confidence=1.0, weight=self.weight, reason="Match exato de CPF/CNPJ via PIX")
                
        # Match string de PIX key vs Fornecedor
        if mov_f.chave_pix and parc_f.palavras_chave:
            tokens_match = sum(1 for t in parc_f.palavras_chave if t in mov_f.chave_pix)
            if tokens_match > 0 and len(parc_f.palavras_chave) > 0:
                pct = (tokens_match / len(parc_f.palavras_chave)) * 100
                return RuleResult(score=pct, confidence=0.8, weight=self.weight, reason=f"Match parcial na chave PIX/Nome ({pct}%)")
                
        return RuleResult(score=0.0, confidence=0.0, weight=self.weight, reason="Sem match de regras PIX")
