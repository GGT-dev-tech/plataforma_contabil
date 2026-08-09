from typing import List
from datetime import datetime
from app.contexts.exportacao.adapters.base import ExportAdapter
from app.models.lancamento_v2 import LancamentoContabilV2

class DominioSistemasAdapter(ExportAdapter):
    """
    Adapter simplificado para geração do arquivo de Lançamentos Contábeis (LCT) 
    para o Domínio Sistemas.
    
    Layout adotado (Múltiplas Partidas, delimitador pipe '|'):
    0000 | DATA (DD/MM/YYYY) | CONTA DEBITO | CONTA CREDITO | VALOR | HISTORICO
    Quando há múltiplas partidas, o sistema contábil aceita que ou a conta debito ou credito
    venha preenchida (a outra em branco), agrupando pela data e lote.
    """
    
    def get_nome_formato(self) -> str:
        return "dominio_sistemas"
        
    def get_extensao_arquivo(self) -> str:
        return "txt"

    def exportar(self, lancamentos: List[LancamentoContabilV2]) -> bytes:
        linhas = []
        
        # Cabeçalho opcional do domínio
        linhas.append("// FORMATO: Lote Domínio Sistemas (Exportação Plataforma)")
        linhas.append("// COD_EMPRESA|DATA|CONTA_DEBITO|CONTA_CREDITO|VALOR|HISTORICO")
        
        for lanc in lancamentos:
            data_str = lanc.data_lancamento.strftime("%d/%m/%Y")
            valor_str = f"{lanc.valor:.2f}".replace(".", ",")
            
            conta_debito = lanc.conta_contabil_codigo if lanc.partida.name == 'DEBITO' else ""
            conta_credito = lanc.conta_contabil_codigo if lanc.partida.name == 'CREDITO' else ""
            
            historico = lanc.historico.replace("|", "").replace("\n", " ").strip()
            # Limitar histórico a 250 caracteres (tamanho comum em ERPs)
            historico = historico[:250]
            
            # Aqui simulamos cod_empresa = 1 fixo para demonstração, 
            # na prática viria de um de-para de empresas no escritório.
            cod_empresa = "1"
            
            linha = f"{cod_empresa}|{data_str}|{conta_debito}|{conta_credito}|{valor_str}|{historico}"
            linhas.append(linha)
            
        conteudo_txt = "\r\n".join(linhas)
        return conteudo_txt.encode('windows-1252', errors='replace')
