import os
import sys

sys.path.insert(0, os.path.abspath('backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

from app.services.parsers import parse_despesas, parse_extrato, parse_razao

import uuid
execucao_id = str(uuid.uuid4())

try:
    with open('test_data/despesas_sample.csv', 'rb') as f:
        parse_despesas(f, db, execucao_id)
        
    with open('test_data/extrato_sample.csv', 'rb') as f:
        parse_extrato(f, db, execucao_id)
        
    with open('test_data/razao_sample.csv', 'rb') as f:
        parse_razao(f, db, execucao_id)
        
    print("Parsers ran without raising exceptions.")
    
    from app.models.domain import Despesa, ParcelaDespesa, MovimentacaoBancaria
    print("Despesas:", db.query(Despesa).count())
    print("MovimentacaoBancaria:", db.query(MovimentacaoBancaria).count())
    
except Exception as e:
    import traceback
    traceback.print_exc()

