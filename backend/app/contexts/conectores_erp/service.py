from typing import Optional, List, Dict, Any
from app.contexts.conectores_erp.adapters.sienge import SiengeConnector

class ConectorErpService:
    def __init__(self):
        # Para este MVP, mapeamos apenas o Sienge. Pode ser estendido.
        self.adapters = {
            "sienge": SiengeConnector()
        }
        
    def fetch_obras(self, erp_name: str = "sienge") -> List[Dict[str, Any]]:
        """
        Retorna os dados brutos de obras diretamente do ERP, sem persistir.
        """
        if erp_name not in self.adapters:
            raise ValueError("ERP não suportado")
            
        adapter = self.adapters[erp_name]
        adapter.autenticar({})
        
        return adapter.listar_obras()

    def fetch_documentos(self, obra_codigo_interno: str, data_inicio: str = "2026-08-01", data_fim: str = "2026-08-31", erp_name: str = "sienge") -> List[Dict[str, Any]]:
        """
        Retorna os dados brutos de documentos fiscais da obra, sem persistir.
        """
        if erp_name not in self.adapters:
            raise ValueError("ERP não suportado")
            
        adapter = self.adapters[erp_name]
        adapter.autenticar({})
        
        return adapter.listar_documentos_fiscais(obra_codigo_interno, data_inicio, data_fim)
