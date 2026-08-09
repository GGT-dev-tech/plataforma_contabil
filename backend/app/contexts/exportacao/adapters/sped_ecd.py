from typing import List
from datetime import datetime
from app.contexts.exportacao.adapters.base import ExportAdapter
from app.models.lancamento_v2 import LancamentoContabilV2

class SpedEcdAdapter(ExportAdapter):
    """
    Gerador do arquivo SPED Contábil (ECD).
    Layout simplificado MVP: Abertura (Bloco 0) + Lançamentos (Bloco I).
    """

    def get_nome_formato(self) -> str:
        return "sped_ecd"

    def get_extensao_arquivo(self) -> str:
        return "txt"

    def _gerar_bloco_0(self, cnpj: str, nome: str, data_ini: str, data_fim: str) -> List[str]:
        # Registro 0000: Abertura do Arquivo Digital e Identificação da Pessoa Jurídica
        # Layout: REG|LEIAUTE|DT_INI|DT_FIN|NOME|CNPJ|UF|IE|COD_MUN|IM|IND_SIT_ESP|IND_SIT_INI_PER|IND_NIRE|IND_FIN_ENT|COD_HASH_SUB|IND_GRANDE_PORTE|TIP_ECD|COD_SCP|IDENT_MF|IND_ESC_CONS|IND_NIRE_SUB|HASH_SUB
        linhas = []
        linhas.append(f"|0000|9|{data_ini}|{data_fim}|{nome}|{cnpj}||||||0|0|0||0|0|||||")
        # Registro 0001: Abertura do Bloco 0
        linhas.append("|0001|0|")
        # Registro 0990: Encerramento do Bloco 0
        linhas.append("|0990|3|")
        return linhas

    def _gerar_bloco_i(self, lancamentos: List[LancamentoContabilV2]) -> List[str]:
        linhas = []
        linhas.append("|I001|0|")
        
        # Agrupa lançamentos pelo Lote / Data
        lotes = {}
        for lanc in lancamentos:
            key = (lanc.numero_lote, lanc.data_lancamento)
            if key not in lotes:
                lotes[key] = []
            lotes[key].append(lanc)
        
        total_i200 = 0
        total_i250 = 0

        for (lote, data), grupo in lotes.items():
            # Registro I200: Lançamento Contábil
            data_str = data.strftime("%d%m%Y")
            valor_lote = sum(l.valor for l in grupo if l.partida.name == 'DEBITO')
            valor_lote_str = f"{valor_lote:.2f}".replace(".", ",")
            
            linhas.append(f"|I200|{lote}|{data_str}|{valor_lote_str}|N|")
            total_i200 += 1
            
            for lanc in grupo:
                # Registro I250: Partidas do Lançamento Contábil
                # REG|COD_CTA|COD_CCUS|VL_DC|IND_DC|NUM_ARQ|COD_HIST_PAD|HIST|COD_PART
                conta = lanc.conta_contabil_codigo
                valor_str = f"{lanc.valor:.2f}".replace(".", ",")
                ind_dc = "D" if lanc.partida.name == 'DEBITO' else "C"
                hist = lanc.historico.replace("|", " ").strip()
                
                linhas.append(f"|I250|{conta}||{valor_str}|{ind_dc}|||{hist}||")
                total_i250 += 1

        linhas.append(f"|I990|{len(linhas) + 1}|")
        return linhas

    def exportar(self, lancamentos: List[LancamentoContabilV2]) -> bytes:
        if not lancamentos:
            return b""
            
        # Pega as datas do primeiro e último lançamento para o Bloco 0
        datas = sorted([l.data_lancamento for l in lancamentos])
        dt_ini = datas[0].strftime("%d%m%Y")
        dt_fim = datas[-1].strftime("%d%m%Y")
        
        # TODO: Recuperar da empresa logada no contexto, mockado para o MVP
        cnpj = "12345678000199"
        nome = "EMPRESA EXEMPLO S.A."
        
        todas_linhas = []
        todas_linhas.extend(self._gerar_bloco_0(cnpj, nome, dt_ini, dt_fim))
        todas_linhas.extend(self._gerar_bloco_i(lancamentos))
        
        # Encerramento Bloco 9
        todas_linhas.append("|9001|0|")
        # Conta a quantidade de registros no bloco 9 (9001, 9900s, 9990, 9999)
        todas_linhas.append("|9990|3|") 
        # Encerramento Geral
        # REG | QTD_LIN
        todas_linhas.append(f"|9999|{len(todas_linhas) + 1}|")
        
        conteudo = "\r\n".join(todas_linhas)
        return conteudo.encode('windows-1252', errors='replace')
