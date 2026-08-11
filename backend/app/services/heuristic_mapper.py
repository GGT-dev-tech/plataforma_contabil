import hashlib
import json
import difflib
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.domain import ClientSchemaMapping

class HeuristicMapper:
    """
    Motor Heurístico para inferência de colunas (Data, Valor, Fornecedor, etc)
    em planilhas de formato desconhecido.
    """
    
    # Dicionário estendido de sinônimos para o Fuzzy Matching
    CANONICAL_TARGETS = {
        "data": ["data de competência", "data", "emissao", "vencimento", "data pagamento"],
        "valor": ["valor total", "valor", "montante", "quantia", "total", "saida", "entrada", "r$"],
        "descricao": ["historico", "descrição", "detalhes", "observação", "nome", "projeto", "documento", "id"],
        "fornecedor": ["fornecedor", "cliente", "empresa", "favorecido", "razao social", "nome fantasia"],
        "categoria": ["categoria", "tipo", "grupo", "plano de contas", "classificação", "despesa", "receita", "natureza"]
    }
    
    @staticmethod
    def _generate_signature(headers: List[str]) -> str:
        """Gera um hash único para a combinação exata de cabeçalhos."""
        normalized = ",".join([str(h).strip().lower() for h in headers if h])
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    @staticmethod
    def get_or_infer_mapping(db: Session, empresa_id: str, headers: List[str]) -> Dict[str, str]:
        """
        Retorna o mapeamento de colunas.
        1. Tenta buscar da memória (ClientSchemaMapping).
        2. Se não achar, roda a Heurística (Fuzzy Match).
        """
        if not empresa_id:
            return HeuristicMapper.infer_mapping(headers)
            
        signature = HeuristicMapper._generate_signature(headers)
        
        # 1. Checa memória
        saved = db.query(ClientSchemaMapping).filter_by(
            empresa_id=empresa_id, 
            file_signature=signature
        ).first()
        
        if saved and saved.mapping_json:
            return saved.mapping_json
            
        # 2. Se não tem na memória, inferir heurística
        mapping = HeuristicMapper.infer_mapping(headers)
        
        # No futuro, podemos salvar automaticamente ou esperar validação do usuário.
        # Por enquanto, retornamos o que a Heurística achou.
        return mapping

    @staticmethod
    def infer_mapping(headers: List[str]) -> Dict[str, str]:
        """
        Usa Similaridade de Strings para descobrir qual coluna da planilha 
        equivale a qual coluna do Modelo Canônico (StagingRegistro).
        """
        mapping = {}
        
        for header in headers:
            if not header or not isinstance(header, str): continue
            
            best_match = None
            highest_score = 0.0
            
            header_lower = header.lower().strip()
            
            for canonical_key, synonyms in HeuristicMapper.CANONICAL_TARGETS.items():
                # Tenta match exato ou parcial direto primeiro
                if header_lower in synonyms:
                    best_match = canonical_key
                    break
                    
                # Fuzzy Match com difflib
                matches = difflib.get_close_matches(header_lower, synonyms, n=1, cutoff=0.6)
                if matches:
                    # Encontrou uma boa similaridade
                    # difflib não dá um score float nativo facilmente na API get_close_matches, 
                    # mas o fato de retornar significa que passou do cutoff 0.6
                    best_match = canonical_key
                    break
            
            if best_match:
                mapping[header] = best_match
                
        return mapping

    @staticmethod
    def save_mapping(db: Session, empresa_id: str, headers: List[str], mapping: Dict[str, str]):
        """Salva a memória validada pelo usuário para uso futuro."""
        if not empresa_id: return
        signature = HeuristicMapper._generate_signature(headers)
        
        saved = db.query(ClientSchemaMapping).filter_by(
            empresa_id=empresa_id, 
            file_signature=signature
        ).first()
        
        if saved:
            saved.mapping_json = mapping
        else:
            new_map = ClientSchemaMapping(
                empresa_id=empresa_id,
                file_signature=signature,
                mapping_json=mapping
            )
            db.add(new_map)
        db.commit()
