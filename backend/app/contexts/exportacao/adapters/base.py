from abc import ABC, abstractmethod
from typing import List
from app.models.lancamento_v2 import LancamentoContabilV2

class ExportAdapter(ABC):
    """
    Interface base para adaptadores de exportação contábil.
    Cada ERP ou sistema (Domínio, Alterdata, Protheus, SPED ECD) deve implementar esta classe.
    """
    
    @abstractmethod
    def get_nome_formato(self) -> str:
        """Retorna o nome do formato (Ex: 'dominio_sistemas', 'sped_ecd')"""
        pass
        
    @abstractmethod
    def get_extensao_arquivo(self) -> str:
        """Retorna a extensão do arquivo (Ex: 'txt', 'csv')"""
        pass

    @abstractmethod
    def exportar(self, lancamentos: List[LancamentoContabilV2]) -> bytes:
        """
        Recebe uma lista de lançamentos contábeis em partida dobrada,
        formata de acordo com o layout alvo, e retorna os bytes do arquivo gerado.
        """
        pass
