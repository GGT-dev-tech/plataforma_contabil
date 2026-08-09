from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.lancamento_v2 import LancamentoContabilV2
from app.contexts.exportacao.adapters.base import ExportAdapter
from app.contexts.exportacao.adapters.dominio_sistemas import DominioSistemasAdapter

class ExportacaoService:
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "dominio_sistemas": DominioSistemasAdapter()
        }
        
    def obter_lancamentos(self, empresa_id: Optional[str] = None, obra_id: Optional[str] = None) -> List[LancamentoContabilV2]:
        query = self.db.query(LancamentoContabilV2).filter(LancamentoContabilV2.is_deleted == False)
        
        if empresa_id:
            query = query.filter(LancamentoContabilV2.empresa_id == empresa_id)
            
        if obra_id:
            query = query.filter(LancamentoContabilV2.obra_id == obra_id)
            
        return query.order_by(LancamentoContabilV2.data_lancamento, LancamentoContabilV2.id).all()
        
    def exportar_arquivos(self, formato: str, empresa_id: Optional[str] = None, obra_id: Optional[str] = None) -> bytes:
        if formato not in self.adapters:
            raise ValueError(f"Formato de exportação '{formato}' não suportado.")
            
        adapter: ExportAdapter = self.adapters[formato]
        lancamentos = self.obter_lancamentos(empresa_id, obra_id)
        
        if not lancamentos:
            raise ValueError("Não há lançamentos contábeis para exportar com os filtros informados.")
            
        return adapter.exportar(lancamentos)
