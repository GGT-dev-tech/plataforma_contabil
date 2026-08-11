import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.domain import MatchCandidate, MovimentacaoBancaria, Conciliacao, Despesa, ParcelaDespesa, ExecucaoPipeline, ConciliacaoItem

db = sessionmaker(bind=create_engine(os.environ.get('DATABASE_URL')))()

execucao = db.query(ExecucaoPipeline).order_by(ExecucaoPipeline.data_inicio.desc()).first()

if not execucao:
    print("Nenhuma execução encontrada.")
    exit(0)

movs = db.query(MovimentacaoBancaria).filter(MovimentacaoBancaria.execucao_id == execucao.id).count()
despesas = db.query(Despesa).filter(Despesa.execucao_id == execucao.id).count()
parcelas = db.query(ParcelaDespesa).join(Despesa).filter(Despesa.execucao_id == execucao.id).count()
candidatos = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == execucao.id).count()
conciliacoes = db.query(Conciliacao).count()

print(f"Execução: {execucao.id}")
print(f"Movimentações importadas: {movs}")
print(f"Despesas importadas: {despesas}")
print(f"Parcelas importadas: {parcelas}")
print(f"Candidatos gerados: {candidatos}")
print(f"Conciliações criadas (total db): {conciliacoes}")
print("-" * 40)

from sqlalchemy import func
status_counts = db.query(MatchCandidate.status, func.count(MatchCandidate.id)).filter(MatchCandidate.execucao_id == execucao.id).group_by(MatchCandidate.status).all()
print("Distribuição de Status:")
for status, count in status_counts:
    print(f"{status.name}: {count}")

print("-" * 40)

candidato = db.query(MatchCandidate).filter(MatchCandidate.execucao_id == execucao.id, MatchCandidate.status == 'APROVADO').first()
if candidato:
    print("Exemplo de Candidato APROVADO:")
    cand_dict = {
        "score": candidato.score_total,
        "status": candidato.status.name,
        "explanation_snapshot": json.loads(candidato.explanation_snapshot) if candidato.explanation_snapshot else None
    }
    print(json.dumps(cand_dict, indent=2))
else:
    print("Nenhum candidato aprovado encontrado.")

print("-" * 40)

conciliacao = db.query(Conciliacao).first()
if conciliacao:
    print("Exemplo de Conciliação Criada:")
    
    mov_id = None
    par_id = None
    for item in conciliacao.itens:
        if item.movimentacao_id:
            mov_id = str(item.movimentacao_id)
        if item.parcela_id:
            par_id = str(item.parcela_id)

    conc_dict = {
        "id": str(conciliacao.id),
        "movimentacao_id": mov_id,
        "parcela_id": par_id,
        "status": conciliacao.status.name,
        "approved_by": str(conciliacao.aprovado_por) if conciliacao.aprovado_por else "SYSTEM"
    }
    print(json.dumps(conc_dict, indent=2))
else:
    print("Nenhuma conciliação encontrada.")
