from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseErpConnector(ABC):
    """
    Interface abstrata para conectores de ERP.
    Define os métodos padrão que todo ERP deve implementar para que a Plataforma 
    possa sincronizar dados de forma agnóstica.
    """
    
    @abstractmethod
    def get_nome_erp(self) -> str:
        """Nome do ERP (Ex: Sienge, UAU, Mega)"""
        pass
        
    @abstractmethod
    def autenticar(self, credenciais: Dict[str, str]) -> bool:
        """Autentica na API do ERP usando as credenciais configuradas"""
        pass
        
    @abstractmethod
    def listar_obras(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de obras (centros de custo) cadastradas no ERP.
        O retorno é um dicionário bruto que será mapeado pelo serviço principal.
        """
        pass
        
    @abstractmethod
    def listar_documentos_fiscais(self, obra_erp_id: str, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
        """
        Busca os documentos fiscais (Notas Fiscais de Entrada, Serviços, RPAs)
        registrados no ERP para uma determinada obra em um período.
        """
        pass
