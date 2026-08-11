from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ledger import LancamentoCabecalho
from app.contexts.exportacao.adapters.base import ExportAdapter
from app.contexts.exportacao.adapters.dominio_sistemas import DominioSistemasAdapter
from app.contexts.exportacao.adapters.sped_ecd import SpedEcdAdapter

class ExportacaoService:
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "dominio_sistemas": DominioSistemasAdapter(),
            "sped_ecd": SpedEcdAdapter()
        }
        
    def obter_lancamentos(self, empresa_id: Optional[str] = None, obra_id: Optional[str] = None, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[LancamentoCabecalho]:
        query = self.db.query(LancamentoCabecalho).filter(LancamentoCabecalho.is_deleted == False)
        
        if empresa_id:
            query = query.filter(LancamentoCabecalho.empresa_id == empresa_id)
            
        if obra_id:
            query = query.filter(LancamentoCabecalho.obra_id == obra_id)
            
        if data_inicio:
            query = query.filter(LancamentoCabecalho.data_competencia >= data_inicio)
            
        if data_fim:
            query = query.filter(LancamentoCabecalho.data_competencia <= data_fim)
            
        return query.order_by(LancamentoCabecalho.data_competencia, LancamentoCabecalho.id).all()
        
    def exportar_arquivos(self, formato: str, empresa_id: Optional[str] = None, obra_id: Optional[str] = None, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> bytes:
        if formato not in self.adapters:
            raise ValueError(f"Formato de exportação '{formato}' não suportado.")
            
        adapter: ExportAdapter = self.adapters[formato]
        lancamentos = self.obter_lancamentos(empresa_id, obra_id, data_inicio, data_fim)
        
        if not lancamentos:
            raise ValueError("Não há lançamentos contábeis para exportar com os filtros informados.")
            
        return adapter.exportar(lancamentos)
