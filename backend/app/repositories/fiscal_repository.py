from app.repositories.base import BaseRepository
from app.models.fiscal import ApuracaoFiscal

class FiscalRepository(BaseRepository[ApuracaoFiscal]):
    """
    Repositório específico para Apuração Fiscal.
    Herdará toda a lógica de filtro Multi-Tenant de BaseRepository.
    """
    pass
