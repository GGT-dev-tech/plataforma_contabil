import os
from alembic.config import Config
from alembic import command
import logging

logger = logging.getLogger(__name__)

def run_startup_tasks():
    logger.info("Executando tarefas de startup...")
    try:
        # Pega o caminho absoluto da pasta raiz do backend
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
        
        # Mudar o diretório de trabalho temporariamente para o backend_dir para o alembic rodar corretamente
        original_cwd = os.getcwd()
        os.chdir(backend_dir)
        
        # Rodar as migrações do Alembic
        logger.info("Aplicando migrations do banco de dados (alembic upgrade head)...")
        alembic_cfg = Config(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations aplicadas com sucesso.")
        
        # Restaurar o diretório de trabalho
        os.chdir(original_cwd)
        
        # Popula o banco com os usuários iniciais
        from scripts.create_first_user import create_initial_users
        logger.info("Criando usuários iniciais...")
        create_initial_users()
        logger.info("Usuários criados com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro durante o startup: {e}")
        # Retorna ao dir original em caso de erro
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
