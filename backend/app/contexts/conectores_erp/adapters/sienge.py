from typing import List, Dict, Any
from app.contexts.conectores_erp.adapters.base import BaseErpConnector

class SiengeConnector(BaseErpConnector):
    """
    Simulador de Conector para o Sienge Plataforma (Softplan).
    Na versão real, usaria chamadas REST para api.sienge.com.br
    """
    
    def __init__(self):
        self.autenticado = False
        
    def get_nome_erp(self) -> str:
        return "Sienge"
        
    def autenticar(self, credenciais: Dict[str, str]) -> bool:
        # Mock de autenticação JWT / Basic
        self.autenticado = True
        return True
        
    def listar_obras(self) -> List[Dict[str, Any]]:
        if not self.autenticado:
            raise PermissionError("Não autenticado no Sienge.")
            
        # Mock de resposta da API /api/v1/enterprises
        return [
            {
                "id": 101,
                "name": "Residencial Alphaville",
                "cno": "123456789012",
                "address": "Av. Principal, 100",
                "city": "São Paulo",
                "state": "SP",
                "spe_cnpj": "12345678000199",
                "status": "EM_ANDAMENTO"
            },
            {
                "id": 102,
                "name": "Torre Empresarial Sul",
                "cno": "987654321098",
                "address": "Rua Comercial, 500",
                "city": "Curitiba",
                "state": "PR",
                "spe_cnpj": "98765432000188",
                "status": "EM_ANDAMENTO"
            }
        ]
        
    def listar_documentos_fiscais(self, obra_erp_id: str, data_inicio: str, data_fim: str) -> List[Dict[str, Any]]:
        if not self.autenticado:
            raise PermissionError("Não autenticado no Sienge.")
            
        # Mock de resposta da API /api/v1/invoices ou similar
        return [
            {
                "invoiceNumber": "5501",
                "invoiceKey": "35231012345678000199550010000055011234567890",
                "issueDate": "2026-08-01",
                "grossValue": 15000.00,
                "providerName": "Cimentos do Brasil Ltda",
                "providerCnpj": "99888777000155",
                "type": "NFE_MATERIAL",
                "taxes": {
                    "iss": 0,
                    "inss": 0,
                    "irrf": 0
                }
            },
            {
                "invoiceNumber": "992",
                "invoiceKey": None,
                "issueDate": "2026-08-05",
                "grossValue": 25000.00,
                "providerName": "Empreiteira Silva (Mão de Obra)",
                "providerCnpj": "44333222000111",
                "type": "NFSE_SERVICO",
                "taxes": {
                    "iss": 1250.00,
                    "inss": 2750.00,
                    "irrf": 375.00
                }
            }
        ]
