import abc
import os
import shutil
from typing import BinaryIO

class StorageProvider(abc.ABC):
    @abc.abstractmethod
    def save(self, execution_id: str, filename: str, file_stream: BinaryIO) -> str:
        """Salva o arquivo e retorna o path ou URI de acesso"""
        pass
        
    @abc.abstractmethod
    def get(self, path: str) -> BinaryIO:
        """Recupera o stream do arquivo"""
        pass
        
    @abc.abstractmethod
    def delete(self, path: str) -> bool:
        """Deleta o arquivo armazenado"""
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "uploads/executions"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def save(self, execution_id: str, filename: str, file_stream: BinaryIO) -> str:
        exec_dir = os.path.join(self.base_dir, execution_id)
        os.makedirs(exec_dir, exist_ok=True)
        
        file_path = os.path.join(exec_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_stream, buffer)
            
        return file_path
        
    def get(self, path: str) -> BinaryIO:
        return open(path, "rb")
        
    def delete(self, path: str) -> bool:
        if os.path.exists(path):
            os.remove(path)
            return True
        return False
