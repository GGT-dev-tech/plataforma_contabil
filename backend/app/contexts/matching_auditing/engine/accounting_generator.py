import logging
import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.domain import MatchCandidate
from app.models.financeiro import MovimentacaoFinanceira, TituloFinanceiro, TipoMovimentacao
from app.models.ledger import LancamentoCabecalho, PartidaItem, TipoPartida, StatusLancamento, ModuloOrigem
from app.core.uow import SQLAlchemyUnitOfWork
from app.api.deps import SessionLocal

logger = logging.getLogger(__name__)

def generate_accounting_entry(cand_id: str):
    """
    Listener assíncrono para o Evento de Decisão de Match.
    Gera as Partidas Dobradas (LancamentoCabecalho + PartidaItem) ao aprovar a conciliação.
    Segue o Princípio das Partidas Dobradas:
      - Pagamento a Fornecedor: D-Fornecedores a Pagar (2.1.1.01) / C-Banco (1.1.2.01)
      - Recebimento: D-Banco (1.1.2.01) / C-Clientes (1.1.3.01)
    """
    db: Session = SessionLocal()
    with SQLAlchemyUnitOfWork(db) as uow:
        cand = uow.session.query(MatchCandidate).filter_by(id=cand_id).first()
        if not cand or cand.status.name != "APROVADO":
            return

        mov = uow.session.query(MovimentacaoFinanceira).filter_by(id=cand.movimentacao_financeira_id).first()
        if not mov:
            return

        # Evitar duplicidade
        if cand.lancamento_cabecalho_id:
            return

        titulo = None
        if cand.titulo_id:
            titulo = uow.session.query(TituloFinanceiro).filter_by(id=cand.titulo_id).first()

        # Determinar naturaleza
        is_saida = mov.tipo == TipoMovimentacao.SAIDA
        valor = Decimal(str(abs(mov.valor)))

        # Histórico contextualizado
        if is_saida and titulo and titulo.fornecedor_cliente_nome:
            historico = f"Pgto Fornecedor: {titulo.fornecedor_cliente_nome}"
        elif not is_saida and titulo and titulo.fornecedor_cliente_nome:
            historico = f"Recebimento: {titulo.fornecedor_cliente_nome}"
        else:
            historico = f"Conciliação Auto: {mov.descricao_extrato}"

        empresa_id = mov.empresa_id

        # Criação do Cabeçalho
        cabecalho = LancamentoCabecalho(
            id=str(uuid.uuid4()),
            empresa_id=empresa_id,
            data_competencia=mov.data_transacao,
            historico_padrao=historico,
            numero_lote=f"CONC-{cand_id[:8].upper()}",
            modulo_origem=ModuloOrigem.FINANCEIRO,
            status=StatusLancamento.CONFIRMADO
        )
        uow.session.add(cabecalho)
        uow.session.flush()

        # Contas Contábeis (simplificado — em produção busca do PlanoDeContas da empresa)
        if is_saida:
            # D-Fornecedores a Pagar / C-Banco
            conta_debito_codigo = "2.1.1.01"   # Fornecedores a Pagar
            conta_credito_codigo = "1.1.2.01"  # Banco
        else:
            # D-Banco / C-Clientes
            conta_debito_codigo = "1.1.2.01"   # Banco
            conta_credito_codigo = "1.1.3.01"  # Clientes

        partida_debito = PartidaItem(
            id=str(uuid.uuid4()),
            empresa_id=empresa_id,
            cabecalho_id=cabecalho.id,
            conta_contabil_id=uuid.uuid4(),  # TODO: resolver via PlanoDeContas.buscar_por_codigo(conta_debito_codigo)
            natureza=TipoPartida.DEBITO,
            valor=valor,
            historico_complementar=f"D: {conta_debito_codigo}"
        )
        partida_credito = PartidaItem(
            id=str(uuid.uuid4()),
            empresa_id=empresa_id,
            cabecalho_id=cabecalho.id,
            conta_contabil_id=uuid.uuid4(),  # TODO: resolver via PlanoDeContas.buscar_por_codigo(conta_credito_codigo)
            natureza=TipoPartida.CREDITO,
            valor=valor,
            historico_complementar=f"C: {conta_credito_codigo}"
        )
        uow.session.add(partida_debito)
        uow.session.add(partida_credito)

        # Vincular candidato ao novo lançamento
        cand.lancamento_cabecalho_id = cabecalho.id

        uow.commit()
        logger.info(f"[EDA] LancamentoCabecalho gerado: {cabecalho.id} (2 partidas) para Candidato: {cand_id}")
