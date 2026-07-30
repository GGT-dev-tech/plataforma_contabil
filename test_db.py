import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.domain import ExecucaoPipeline, MatchCandidate, ImportacaoArquivo, MovimentacaoBancaria, Despesa

engine = create_engine("postgresql://postgres:postgres@localhost:5432/plataforma")
Session = sessionmaker(bind=engine)
db = Session()

execs = db.query(ExecucaoPipeline).order_by(ExecucaoPipeline.data_inicio.desc()).all()
if not execs:
    print("No executions found.")
    sys.exit(0)

ex = execs[0]
print(f"Latest Exec: {ex.id} - Status: {ex.status}")
print(f"Error: {ex.erro_codigo} | {ex.erro_mensagem}")

imports = db.query(ImportacaoArquivo).filter_by(execucao_id=ex.id).all()
print(f"Imports: {len(imports)}")
for i in imports:
    print(f"  {i.tipo} -> {i.storage_path}")

movs = db.query(MovimentacaoBancaria).filter_by(execucao_id=ex.id).count()
desps = db.query(Despesa).filter_by(execucao_id=ex.id).count()
print(f"Movs: {movs} | Despesas: {desps}")

candidates = db.query(MatchCandidate).filter_by(execucao_id=ex.id).count()
print(f"Candidates: {candidates}")

