from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from app.models.ledger import (
    LancamentoCabecalho, 
    PartidaItem, 
    PeriodoContabil, 
    StatusPeriodo,
    TipoPartida,
    ModuloOrigem,
    StatusLancamento
)
from app.models.plano_contas import PlanoDeContas, TipoConta

class PeriodoFechadoError(Exception):
    pass

class PartidaDesbalanceadaError(Exception):
    pass

class ContaSinteticaError(Exception):
    pass

class LedgerController:
    """
    Serviço central de registro contábil.
    Garante integridade ACID e os princípios das Partidas Dobradas.
    """
    def __init__(self, db: Session):
        self.db = db

    def registrar_lancamento(
        self,
        empresa_id: str,
        data_competencia: date,
        historico: str,
        modulo: ModuloOrigem,
        partidas: List[dict],
        numero_lote: Optional[str] = None,
        documento_fiscal_id: Optional[str] = None,
        obra_id: Optional[str] = None,
    ) -> LancamentoCabecalho:
        """
        Registra um lançamento em partida dobrada.
        
        Args:
            partidas: Lista de dicionários contendo:
                - conta_contabil_id: str
                - natureza: TipoPartida (D ou C)
                - valor: Decimal
                - centro_custo_id: str (opcional)
                - historico_complementar: str (opcional)
        """
        # 1. Validar Período Contábil
        self._validar_periodo(empresa_id, data_competencia)

        # 2. Validar Balanceamento (D = C)
        self._validar_balanceamento(partidas)

        # 3. Validar Contas (Não podem ser sintéticas)
        self._validar_contas(empresa_id, partidas)

        # Criação do Lote/Cabeçalho
        if not numero_lote:
            numero_lote = f"LTC-{uuid.uuid4().hex[:8].upper()}"

        cabecalho = LancamentoCabecalho(
            empresa_id=empresa_id,
            data_competencia=data_competencia,
            historico_padrao=historico,
            numero_lote=numero_lote,
            modulo_origem=modulo,
            status=StatusLancamento.RASCUNHO,
            documento_fiscal_id=documento_fiscal_id,
            obra_id=obra_id
        )

        # Criação das Partidas
        for p in partidas:
            item = PartidaItem(
                empresa_id=empresa_id,
                conta_contabil_id=p['conta_contabil_id'],
                natureza=p['natureza'],
                valor=p['valor'],
                centro_custo_id=p.get('centro_custo_id'),
                historico_complementar=p.get('historico_complementar')
            )
            cabecalho.partidas.append(item)

        self.db.add(cabecalho)
        # Flush is required so calling function can handle exceptions before commit
        self.db.flush() 
        return cabecalho

    def _validar_periodo(self, empresa_id: str, data: date):
        ano_mes = data.strftime("%Y-%m")
        periodo = self.db.query(PeriodoContabil).filter(
            PeriodoContabil.empresa_id == empresa_id,
            PeriodoContabil.ano_mes == ano_mes
        ).first()

        if periodo and periodo.status == StatusPeriodo.FECHADO:
            raise PeriodoFechadoError(f"O período {ano_mes} já está fechado.")

    def _validar_balanceamento(self, partidas: List[dict]):
        total_debito = Decimal('0.00')
        total_credito = Decimal('0.00')

        for p in partidas:
            v = Decimal(str(p['valor']))
            if p['natureza'] == TipoPartida.DEBITO:
                total_debito += v
            else:
                total_credito += v

        if total_debito != total_credito:
            raise PartidaDesbalanceadaError(
                f"Lançamento desbalanceado. Débitos: {total_debito}, Créditos: {total_credito}"
            )
        
        if total_debito == 0:
             raise PartidaDesbalanceadaError("Um lançamento contábil não pode ter valor zero.")

    def _validar_contas(self, empresa_id: str, partidas: List[dict]):
        conta_ids = [p['conta_contabil_id'] for p in partidas]
        contas = self.db.query(PlanoDeContas).filter(
            PlanoDeContas.id.in_(conta_ids)
        ).all()
        
        map_contas = {str(c.id): c for c in contas}
        
        for p in partidas:
            conta_id = str(p['conta_contabil_id'])
            conta = map_contas.get(conta_id)
            if not conta:
                raise ValueError(f"Conta contábil {conta_id} não encontrada.")
            if conta.tipo == TipoConta.SINTETICA:
                raise ContaSinteticaError(
                    f"A conta {conta.codigo_contabil} - {conta.descricao} é sintética e não aceita lançamentos."
                )
            if not conta.aceita_lancamentos:
                 raise ContaSinteticaError(f"A conta {conta.codigo_contabil} não aceita lançamentos.")
