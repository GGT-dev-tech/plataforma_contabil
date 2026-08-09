import logging
import uuid
from sqlalchemy.orm import Session
from app.models.domain import (
    MatchCandidate, MovimentacaoBancaria, ParcelaDespesa, LancamentoContabil
)
from app.core.uow import SQLAlchemyUnitOfWork
from app.api.deps import SessionLocal

logger = logging.getLogger(__name__)

def generate_accounting_entry(cand_id: str):
    """
    Listener assíncrono para o Evento de Decisão de Match.
    Gera as Partidas Dobradas (LancamentoContabil) ao aprovar a conciliação.
    """
    db: Session = SessionLocal()
    with SQLAlchemyUnitOfWork(db) as uow:
        cand = uow.session.query(MatchCandidate).filter_by(id=cand_id).first()
        if not cand or cand.status.name != "APROVADO":
            return
            
        mov = uow.session.query(MovimentacaoBancaria).filter_by(id=cand.movimentacao_id).first()
        if not mov:
            return
            
        # Verificar se já gerou um lançamento para evitar duplicidade
        if cand.lancamento_id:
            # Já existia lançamento mapeado ou gerado
            return
            
        parcela = None
        if cand.parcela_id:
            parcela = uow.session.query(ParcelaDespesa).filter_by(id=cand.parcela_id).first()
            
        novo_lancamento = LancamentoContabil(
            id=str(uuid.uuid4()),
            execucao_id=cand.execucao_id,
            chave_origem_sci=f"LANC-{mov.id}",
            data=mov.data,
            # No futuro, buscaremos o plano de contas da Empresa.
            # conta_contabil_id: precisa de um ID real no BD.
            # Para manter simples, omitimos conta_contabil_id se nullable ou preenchemos o que puder
            conta_contrapartida="1.01.01.01" if mov.valor < 0 else "3.01.01.01",
            valor=abs(mov.valor),
            tipo="D" if mov.valor < 0 else "C",
            historico=f"Pgto Fornecedor: {parcela.fornecedor.nome if parcela and parcela.fornecedor else mov.historico}" if mov.valor < 0 else f"Recebimento: {mov.historico}",
            lote="CONCILIACAO_AUTO"
        )
        
        uow.session.add(novo_lancamento)
        
        # Atrelar o candidato ao novo lancamento
        cand.lancamento_id = novo_lancamento.id
        uow.commit()
        logger.info(f"[EDA] Lançamento Contábil gerado: {novo_lancamento.id} para Candidato: {cand.id}")
