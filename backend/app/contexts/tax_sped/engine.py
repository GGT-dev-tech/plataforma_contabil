from sqlalchemy.orm import Session
from datetime import datetime
from app.models.domain import Empresa
from app.models.plano_contas import PlanoDeContas, GrupoConta
from app.models.ledger import LancamentoCabecalho, PartidaItem, StatusLancamento
import logging

logger = logging.getLogger(__name__)

class SpedEcdGenerator:
    """
    Gera o arquivo SPED ECD (Escrituração Contábil Digital).
    Neste MVP, estamos focando no Bloco 0 (Abertura) e Bloco I (Lançamentos Contábeis).
    """
    def __init__(self, db: Session, empresa_id: str, data_inicio: datetime, data_fim: datetime):
        self.db = db
        self.empresa_id = empresa_id
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.linhas = []
        
        self.empresa = self.db.query(Empresa).filter_by(id=self.empresa_id).first()
        if not self.empresa:
            raise ValueError(f"Empresa {self.empresa_id} não encontrada.")

    def _format_date(self, dt):
        return dt.strftime("%d%m%Y") if dt else ""

    def _format_float(self, val):
        return f"{val:.2f}".replace('.', ',') if val else "0,00"

    def gerar_bloco_0(self):
        """
        Gera os registros do Bloco 0 (Abertura, Identificação e Referências)
        """
        # Registro 0000: Abertura do Arquivo Digital e Identificação do Empresário ou da Sociedade Empresária
        cnpj = (self.empresa.cnpj or "").replace(".", "").replace("/", "").replace("-", "")
        nome = self.empresa.razao_social or ""
        
        # Layout: REG|LEIAUTE|DT_INI|DT_FIN|NOME|CNPJ|UF|IE|COD_MUN|IM|IND_SIT_ESP|IND_SIT_INI_PER|IND_NIRE|SUB_TRIB|UF_EXT|IE_EXT|IND_SCPA
        # Simplificado para o MVP
        self.linhas.append(f"|0000|LEIAUTE_9|{self._format_date(self.data_inicio)}|{self._format_date(self.data_fim)}|{nome}|{cnpj}|||||||||||")
        
        # Registro 0001: Abertura do Bloco 0
        self.linhas.append("|0001|0|")

    def gerar_bloco_i(self):
        """
        Gera os registros do Bloco I (Lançamentos Contábeis)
        """
        # Registro I001: Abertura do Bloco I
        self.linhas.append("|I001|0|")
        
        # Recupera Plano de Contas usado no período (simplificação: pega todo o plano ativo)
        contas = self.db.query(PlanoDeContas).filter_by(empresa_id=self.empresa_id).all()
        
        # Registro I050: Plano de Contas
        for conta in contas:
            # REG|DT_ALT|COD_NAT|IND_CTA|NIVEL|COD_CTA|COD_CTA_SUP|CTA
            cod_nat = "01" if conta.grupo == GrupoConta.ATIVO else "02" if conta.grupo == GrupoConta.PASSIVO else "03" if conta.grupo == GrupoConta.PATRIMONIO_LIQUIDO else "04"
            ind_cta = "S" if not conta.aceita_lancamentos else "A"
            nivel = str(conta.nivel)
            cod_cta = conta.codigo_contabil
            cod_cta_sup = "" # Simplificação
            cta = conta.descricao
            
            self.linhas.append(f"|I050|{self._format_date(self.data_inicio)}|{cod_nat}|{ind_cta}|{nivel}|{cod_cta}|{cod_cta_sup}|{cta}|")

        # Recupera Lançamentos do Período
        lancamentos = self.db.query(LancamentoCabecalho).filter(
            LancamentoCabecalho.empresa_id == self.empresa_id,
            LancamentoCabecalho.data_competencia >= self.data_inicio,
            LancamentoCabecalho.data_competencia <= self.data_fim,
            LancamentoCabecalho.status == StatusLancamento.CONFIRMADO
        ).all()

        for cabecalho in lancamentos:
            # Registro I200: Lançamento Contábil
            # REG|NUM_LCTO|DT_LCTO|VL_LCTO|IND_LCTO|DT_LCTO_EXT
            num_lcto = str(cabecalho.id)[:8] # Simplificação
            dt_lcto = self._format_date(cabecalho.data_competencia)
            
            # O valor do lançamento é a soma dos débitos (ou créditos)
            soma_debitos = sum([p.valor for p in cabecalho.partidas if p.natureza.value == "D"])
            vl_lcto = self._format_float(soma_debitos)
            
            self.linhas.append(f"|I200|{num_lcto}|{dt_lcto}|{vl_lcto}|N|")
            
            # Registro I250: Partidas do Lançamento Contábil
            for partida in cabecalho.partidas:
                # REG|COD_CTA|COD_CCUS|VL_DC|IND_DC|NUM_ARQ|COD_HIST_PAD|HIST|COD_PART
                cod_cta = partida.conta_contabil.codigo_contabil if partida.conta_contabil else ""
                vl_dc = self._format_float(partida.valor)
                ind_dc = partida.natureza.value # "D" ou "C"
                hist = partida.historico_complementar or cabecalho.historico_padrao or ""
                
                self.linhas.append(f"|I250|{cod_cta}||{vl_dc}|{ind_dc}|||{hist}||")

    def gerar_bloco_9(self):
        """
        Gera os registros do Bloco 9 (Encerramento do Arquivo Digital)
        """
        self.linhas.append("|9001|0|")
        self.linhas.append(f"|9999|{len(self.linhas) + 1}|")

    def exportar(self) -> str:
        """
        Orquestra a geração de todos os blocos e retorna o texto formatado.
        """
        self.gerar_bloco_0()
        self.gerar_bloco_i()
        self.gerar_bloco_9()
        
        return "\n".join(self.linhas)
