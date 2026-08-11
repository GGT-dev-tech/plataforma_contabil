import os
import sys
# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.models.base import Base
import app.models

engine = create_engine(os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/contabil"))
Base.metadata.create_all(engine)
print("Banco de dados sincronizado com sucesso!")
