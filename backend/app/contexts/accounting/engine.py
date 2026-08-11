import uuid
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.financeiro import TituloFinanceiro, TipoTitulo
from app.models.ledger import LancamentoCabecalho, PartidaItem, ModuloOrigem, TipoPartida, StatusLancamento
from app.models.plano_contas import PlanoDeContas, GrupoConta, ClassificacaoDRE, NaturezaConta

MAPA_DRE = {
    "Receitas de Vendas": ClassificacaoDRE.RECEITA_BRUTA,
    "Receitas de Serviços": ClassificacaoDRE.RECEITA_BRUTA,
    "Cartão Maquininha Recebimento": ClassificacaoDRE.RECEITA_BRUTA,
    "PMBC (Prefeitura de Balneário Camboriú)": ClassificacaoDRE.RECEITA_BRUTA,
    "Impostos": ClassificacaoDRE.DEDUCOES_RECEITA,
    "Impostos sobre Serviços (ISS)": ClassificacaoDRE.DEDUCOES_RECEITA,
    "Materiais Aplicados na Prestação de Serviços": ClassificacaoDRE.CSP,
    "Agulhas biópsias": ClassificacaoDRE.CSP,
    "Honorários Médicos": ClassificacaoDRE.CSP,
    "Dr. Wagner (Honorários)": ClassificacaoDRE.CSP,
    "Dr. Deison (Honorários)": ClassificacaoDRE.CSP,
    "Salários": ClassificacaoDRE.DESPESAS_PESSOAL,
    "INSS sobre Salários - GPS": ClassificacaoDRE.DESPESAS_PESSOAL,
    "FGTS e Multa de FGTS": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Vale-Alimentação": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Uniformes": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Honorários Contábeis": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Honorários Consultoria": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "certificadora": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Bens de Pequeno Valor": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Computadores e Periféricos": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Aluguel": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Energia Elétrica": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Água e Saneamento": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Agua Bombona": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Telefonia e Internet": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Telefonia Móvel": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Vigilância e Segurança Patrimonial": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Manutenção Predial": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Split Manutenção": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Materiais de Limpeza e de Higiene": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Marketing": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Google": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Brindes para Clientes": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Descontos financeiros obtidos": ClassificacaoDRE.OUTRAS_RECEITAS,
    "Antecipação de Lucros": ClassificacaoDRE.DISTRIBUICAO_LUCROS,
    "antecipação de lucros - Honorários": ClassificacaoDRE.CSP,
    "Taxas Bancárias": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Tarifas": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Material de Escritório": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Combustível": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Estacionamento": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Viagens": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Refeições": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Software": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Assinaturas": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Treinamentos": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Uniforme Equipe": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Manutenção Equipamentos": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Reposição Materiais": ClassificacaoDRE.CSP,
    "Exames Externos": ClassificacaoDRE.CSP,
    "Descarte Resíduos": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Seguros": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Licenças": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Certificados Digitais": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Contribuições Sindicais": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Benefícios": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Confraternizações": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Juros Pagos": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Multas Pagas": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Correios": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Limpeza e Conservação": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Reparos Gerais": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Equipamentos Médicos": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Cursos de Aperfeiçoamento": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Palestras": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Eventos": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Taxas Públicas": ClassificacaoDRE.DEDUCOES_RECEITA,
    "Outras Despesas Administrativas": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "IRRF Darf 567": ClassificacaoDRE.DEDUCOES_RECEITA,
    "Retenção - ISS Serviços Tomados": ClassificacaoDRE.DEDUCOES_RECEITA,
    "Agulhas Biópsias": ClassificacaoDRE.CSP,
    "Adiantamento Salarial": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Férias": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Rescisões": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Remuneração de Estagiários": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Seguro de Vida": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Exames Médicos": ClassificacaoDRE.DESPESAS_PESSOAL,
    "reembolso": ClassificacaoDRE.DESPESAS_PESSOAL,
    "reembolso de APP transporte": ClassificacaoDRE.DESPESAS_PESSOAL,
    "Honorários Advocatícios": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Alvara Sanitário": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Alvará de Funcionamento": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "CRM": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Cursos e Treinamentos": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "ACORDO JUDICIAL": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "PASTAS E FOLHAS": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "Materiais de Escritório": ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS,
    "IPTU": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Taxa de Lixo": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Manutenção de Equipamentos": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Material de limpeza + bombona": ClassificacaoDRE.DESPESAS_INSTALACOES,
    "Marketing e Publicidade": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "google": ClassificacaoDRE.DESPESAS_COMERCIAIS,
    "Empréstimos de Sócios": ClassificacaoDRE.OUTRAS_RECEITAS,
    "Rendimentos de Aplicações": ClassificacaoDRE.OUTRAS_RECEITAS,
}

class AccountingEngine:
    def __init__(self, db: Session, empresa_id: str):
        self.db = db
        self.empresa_id = str(empresa_id)
        self._cache_contas = {}

    def _to_uuid(self, val):
        if not val: return None
        if isinstance(val, uuid.UUID): return val
        try:
            return uuid.UUID(str(val))
        except Exception:
            return None

    def _get_or_create_conta(self, codigo: str, descricao: str, grupo: GrupoConta, natureza: str, classificacao_dre: ClassificacaoDRE = None) -> uuid.UUID:
        if codigo in self._cache_contas:
            return self._cache_contas[codigo]
            
        conta = self.db.query(PlanoDeContas).filter_by(
            empresa_id=self._to_uuid(self.empresa_id),
            codigo_contabil=codigo
        ).first()
        
        if not conta:
            conta = PlanoDeContas(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                codigo_contabil=codigo,
                descricao=descricao,
                grupo=grupo,
                natureza=natureza,
                classificacao_dre=classificacao_dre
            )
            self.db.add(conta)
            self.db.flush()
            
        self._cache_contas[codigo] = conta.id
        return conta.id

    def translate_titulo_to_lancamento(self, titulo: TituloFinanceiro) -> LancamentoCabecalho:
        if not titulo.valor_pago or not titulo.data_pagamento:
            raise ValueError("O título precisa estar liquidado (valor e data de pagamento) para gerar o lançamento contábil neste escopo simplificado.")

        cabecalho = LancamentoCabecalho(
            id=self._to_uuid(uuid.uuid4()),
            empresa_id=self._to_uuid(self.empresa_id),
            data_competencia=titulo.data_pagamento,
            historico_padrao=f"Pgto. ref. a {titulo.descricao} - {titulo.fornecedor_cliente_nome or ''}",
            numero_lote=f"FIN-{titulo.data_pagamento.strftime('%Y%m')}",
            modulo_origem=ModuloOrigem.FINANCEIRO,
            status=StatusLancamento.CONFIRMADO,
            documento_fiscal_id=self._to_uuid(titulo.documento_fiscal_id),
            obra_id=self._to_uuid(titulo.obra_id)
        )
        self.db.add(cabecalho)

        tipo_str = str(titulo.tipo.value if hasattr(titulo.tipo, 'value') else titulo.tipo)

        if tipo_str in ["PAGAR", "DESPESA"]:
            cat_name = titulo.categoria or "Despesas Gerais"
            classificacao = MAPA_DRE.get(titulo.categoria, ClassificacaoDRE.NAO_MAPEADO)
            conta_debito_id = self._get_or_create_conta(
                codigo=f"3.1.1.{cat_name[:3].upper()}",
                descricao=f"Despesa com {cat_name}",
                grupo=GrupoConta.RESULTADO,
                natureza=NaturezaConta.DEVEDORA,
                classificacao_dre=classificacao
            )
            
            conta_credito_id = self._get_or_create_conta(
                codigo="1.1.1.01",
                descricao="Caixa / Bancos Conta Movimento",
                grupo=GrupoConta.ATIVO,
                natureza=NaturezaConta.DEVEDORA
            )
            
            partida_deb = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_debito_id,
                natureza=TipoPartida.DEBITO,
                valor=abs(titulo.valor_pago),
                historico_complementar=titulo.descricao
            )
            
            partida_cred = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=abs(titulo.valor_pago),
                historico_complementar=f"Pagamento via {titulo.fornecedor_cliente_nome or 'Caixa'}"
            )
            
            self.db.add(partida_deb)
            self.db.add(partida_cred)
            
        elif tipo_str in ["RECEBER", "RECEITA"]:
            conta_debito_id = self._get_or_create_conta(
                codigo="1.1.1.01",
                descricao="Caixa / Bancos Conta Movimento",
                grupo=GrupoConta.ATIVO,
                natureza=NaturezaConta.DEVEDORA
            )
            
            cat_name = titulo.categoria or "Serviços Prestados"
            classificacao = MAPA_DRE.get(titulo.categoria, ClassificacaoDRE.RECEITA_BRUTA)
            conta_credito_id = self._get_or_create_conta(
                codigo=f"3.1.1.{cat_name[:3].upper()}",
                descricao=f"Receita com {cat_name}",
                grupo=GrupoConta.RESULTADO,
                natureza=NaturezaConta.CREDORA,
                classificacao_dre=classificacao
            )
            
            partida_deb = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_debito_id,
                natureza=TipoPartida.DEBITO,
                valor=abs(titulo.valor_pago),
                historico_complementar=f"Recebimento de {titulo.fornecedor_cliente_nome or 'Cliente'}"
            )
            
            partida_cred = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=abs(titulo.valor_pago),
                historico_complementar=titulo.descricao
            )
            
            self.db.add(partida_deb)
            self.db.add(partida_cred)

        return cabecalho

    def process_all_liquidated(self) -> int:
        from app.models.financeiro import StatusTitulo
        titulos = self.db.query(TituloFinanceiro).filter(
            TituloFinanceiro.empresa_id == self._to_uuid(self.empresa_id),
            TituloFinanceiro.status == StatusTitulo.LIQUIDADO
        ).all()

        count = 0
        for t in titulos:
            try:
                self.translate_titulo_to_lancamento(t)
                self.db.commit()
                count += 1
            except Exception as e:
                self.db.rollback()
                import logging
                logging.getLogger(__name__).warning(f"Erro ao contabilizar titulo {t.id}: {e}")

        return count
