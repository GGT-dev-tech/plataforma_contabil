from app.repositories.base import BaseRepository
from app.models.financeiro import TituloFinanceiro

class TituloRepository(BaseRepository[TituloFinanceiro]):
    """
    Repositório específico para Títulos Financeiros.
    Herdará toda a lógica de filtro Multi-Tenant de BaseRepository.
    """
    pass
