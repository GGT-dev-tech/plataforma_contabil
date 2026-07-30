from abc import ABC, abstractmethod
from typing import List, Any
import datetime
import hashlib
import time
from sqlalchemy.orm import Session
from app.models.domain import ImportacaoArquivo, TipoArquivo
from app.parsers.models import ParserResult, ParserMetrics, ParserReport

class ParserBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do parser."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Versão do parser."""
        pass

    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """Tipos de arquivo suportados (ex: ['.xlsx', '.pdf'])."""
        pass
        
    @abstractmethod
    def extract(self, file_path: str, result: ParserResult) -> Any:
        """Lê o arquivo RAW e retorna as entidades da camada STAGING."""
        pass

    @abstractmethod
    def validate(self, staging_data: Any, result: ParserResult) -> bool:
        """Valida os dados da camada STAGING antes da transformação."""
        pass
        
    @abstractmethod
    def transform(self, staging_data: Any, result: ParserResult) -> Any:
        """Normaliza da camada STAGING para o modelo CANONICAL."""
        pass
        
    @abstractmethod
    def load(self, canonical_data: Any, importacao: ImportacaoArquivo, db_session: Session) -> None:
        """Persiste o modelo CANONICAL no banco atrelado à ImportacaoArquivo."""
        pass

    def calculate_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def execute(self, file_path: str, tipo_arquivo: TipoArquivo, db_session: Session, action_if_exists: str = "BLOCK") -> ParserReport:
        """
        Main pipeline execution: RAW -> STAGING -> CANONICAL -> DB
        action_if_exists = BLOCK | REPROCESS | NEW_VERSION
        """
        start_time = time.time()
        file_hash = self.calculate_hash(file_path)
        nome_arquivo = file_path.split('/')[-1]
        
        # Idempotency check
        existing = db_session.query(ImportacaoArquivo).filter(
            ImportacaoArquivo.hash_arquivo == file_hash,
            ImportacaoArquivo.status == "SUCESSO"
        ).first()
        
        if existing:
            if action_if_exists == "BLOCK":
                raise ValueError(f"Arquivo já processado anteriormente. (Hash: {file_hash})")
            elif action_if_exists == "REPROCESS":
                # To be implemented: cascade delete from Canonical tables based on arquivo_origem = existing.id
                pass
            elif action_if_exists == "NEW_VERSION":
                pass
                
        importacao = ImportacaoArquivo(
            nome_arquivo=nome_arquivo,
            tipo=tipo_arquivo,
            status="EM_PROCESSAMENTO",
            data_importacao=datetime.date.today(),
            hash_arquivo=file_hash,
            quantidade_registros=0,
            erros_encontrados=0
        )
        db_session.add(importacao)
        db_session.flush() # Gerar ID
        
        result = ParserResult()
        result.metrics.hash_arquivo = file_hash
        result.metrics.versao_parser = self.version
        
        try:
            # 1. RAW -> STAGING
            staging = self.extract(file_path, result)
            result.staging_records = staging if isinstance(staging, list) else [staging]
            
            # 2. VALIDAÇÃO
            is_valid = self.validate(staging, result)
            if not is_valid:
                importacao.status = "FALHA_VALIDACAO"
                importacao.erros_encontrados = result.metrics.erros
                db_session.commit()
                return self._generate_report(nome_arquivo, "FALHA_VALIDACAO", result, start_time)
                
            importacao.quantidade_registros = result.metrics.linhas_validas
            
            # 3. STAGING -> CANONICAL
            canonical = self.transform(staging, result)
            
            # 4. LOAD
            self.load(canonical, importacao, db_session)
            
            importacao.status = "SUCESSO"
            db_session.commit()
            
            return self._generate_report(nome_arquivo, "SUCESSO", result, start_time)
            
        except Exception as e:
            db_session.rollback()
            importacao.status = "ERRO_INTERNO"
            importacao.erros_encontrados += 1
            db_session.commit()
            result.errors.append(str(e))
            result.metrics.erros += 1
            return self._generate_report(nome_arquivo, "ERRO_INTERNO", result, start_time)

    def _generate_report(self, file_name: str, status: str, result: ParserResult, start_time: float) -> ParserReport:
        result.metrics.tempo_execucao_ms = int((time.time() - start_time) * 1000)
        return ParserReport(
            arquivo=file_name,
            status=status,
            metrics=result.metrics,
            warnings=result.warnings,
            errors=result.errors
        )
