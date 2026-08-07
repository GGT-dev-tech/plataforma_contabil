import logging
import pandas as pd
from app.services.parsers.razao_sucessor import RazaoSucessorAdapter
from app.api.deps import SessionLocal

logging.basicConfig(level=logging.INFO)
db = SessionLocal()
adapter = RazaoSucessorAdapter()
adapter.parse("Architecture/Razão SUCESSOR.xlsx", db, "test")
