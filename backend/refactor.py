import os
import shutil

BASE_DIR = "app"

# 1. Mapeamento de movimentação de arquivos
MOVES = [
    # Identity
    ("api/routers/auth.py", "contexts/identity/api.py"),
    ("api/auth.py", "contexts/identity/auth_utils.py"),

    # Staging & Ingestion
    ("api/routers/staging.py", "contexts/staging_ingestion/api_staging.py"),
    ("api/routers/executions.py", "contexts/staging_ingestion/api_executions.py"),
    ("services/staging_service.py", "contexts/staging_ingestion/service.py"),
    ("services/parsers", "contexts/staging_ingestion/parsers"),
    ("services/template_service.py", "contexts/staging_ingestion/template_service.py"),

    # Matching & Auditing
    ("api/routers/matching.py", "contexts/matching_auditing/api_matching.py"),
    ("engine", "contexts/matching_auditing/engine"),
    ("pipeline", "contexts/matching_auditing/pipeline"),
    ("cqrs/queries", "contexts/matching_auditing/queries"),
    ("worker.py", "contexts/matching_auditing/worker.py"),
]

# 2. Mapeamento de refatoração de Imports
REPLACEMENTS = [
    ("app.api.routers.auth", "app.contexts.identity.api"),
    ("app.api.auth", "app.contexts.identity.auth_utils"),
    
    ("app.api.routers.staging", "app.contexts.staging_ingestion.api_staging"),
    ("app.api.routers.executions", "app.contexts.staging_ingestion.api_executions"),
    ("app.services.staging_service", "app.contexts.staging_ingestion.service"),
    ("app.services.parsers", "app.contexts.staging_ingestion.parsers"),
    ("app.services.template_service", "app.contexts.staging_ingestion.template_service"),
    
    ("app.api.routers.matching", "app.contexts.matching_auditing.api_matching"),
    ("app.engine", "app.contexts.matching_auditing.engine"),
    ("app.pipeline", "app.contexts.matching_auditing.pipeline"),
    ("app.cqrs.queries", "app.contexts.matching_auditing.queries"),
    ("app.worker", "app.contexts.matching_auditing.worker"),
]

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def move_files():
    print("Mapeando arquivos para Vertical Slices...")
    for src_rel, dst_rel in MOVES:
        src = os.path.join(BASE_DIR, src_rel)
        dst = os.path.join(BASE_DIR, dst_rel)
        if os.path.exists(src):
            ensure_dir(dst)
            if os.path.isdir(src):
                if not os.path.exists(dst):
                    shutil.move(src, dst)
                    print(f"MOVED DIR: {src} -> {dst}")
            else:
                shutil.move(src, dst)
                print(f"MOVED FILE: {src} -> {dst}")
        else:
            print(f"NOT FOUND: {src}")

def refactor_imports():
    print("Atualizando Importações em todo o projeto...")
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                new_content = content
                for old, new in REPLACEMENTS:
                    new_content = new_content.replace(old, new)
                
                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"UPDATED IMPORTS IN: {path}")

def update_main():
    main_path = os.path.join(BASE_DIR, "main.py")
    if os.path.exists(main_path):
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = content.replace("from app.api.routers import auth, executions, matching, staging", 
            "from app.contexts.identity import api as auth\nfrom app.contexts.staging_ingestion import api_executions as executions, api_staging as staging\nfrom app.contexts.matching_auditing import api_matching as matching")
        
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("UPDATED main.py manual mappings.")

if __name__ == "__main__":
    move_files()
    refactor_imports()
    update_main()
    print("DONE!")
