"""
Módulo: Plano de Contas
Estrutura hierárquica baseada na Resolução CFC 1.374/2011 e NBC TG 1000.

O plano de contas é o backbone de toda a escrituração.
Sem ele, não é possível gerar lançamentos em partida dobrada.

Referências:
- Resolução CFC 1.374/2011 (Plano de Contas Referencial)
- ITG 2000 (R1) - Escrituração Contábil
- NBC TG 1000 (PMEs)
"""
from sqlalchemy import Column, String, Enum, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import AuditableBase
import enum


class NaturezaConta(str, enum.Enum):
    """Natureza do saldo da conta (orienta o raciocínio de débito/crédito)."""
    DEVEDORA = "DEVEDORA"    # Ativo e Despesas → saldo normal a débito
    CREDORA = "CREDORA"      # Passivo, PL e Receitas → saldo normal a crédito


class TipoConta(str, enum.Enum):
    SINTETICA = "SINTETICA"  # Conta de agrupamento (não recebe lançamentos)
    ANALITICA = "ANALITICA"  # Conta de lançamento (recebe débitos/créditos)


class GrupoConta(str, enum.Enum):
    """Grupos do Plano de Contas (primeiro nível)."""
    ATIVO = "ATIVO"                    # 1
    PASSIVO = "PASSIVO"                # 2
    PATRIMONIO_LIQUIDO = "PL"          # 3
    RECEITA = "RECEITA"                # 4
    DESPESA = "DESPESA"                # 5
    CUSTO = "CUSTO"                    # 6 (Custo dos Produtos/Obras)
    RESULTADO = "RESULTADO"            # 7 (Contas de Resultado - encerramento)


class ClassificacaoDRE(str, enum.Enum):
    """Classificação específica para montagem estruturada do DRE em cascata."""
    RECEITA_BRUTA = "RECEITA_BRUTA"
    DEDUCOES_RECEITA = "DEDUCOES_RECEITA"
    CSP = "CSP" # Custo dos Serviços Prestados
    DESPESAS_PESSOAL = "DESPESAS_PESSOAL"
    DESPESAS_ADMINISTRATIVAS = "DESPESAS_ADMINISTRATIVAS"
    DESPESAS_INSTALACOES = "DESPESAS_INSTALACOES"
    DESPESAS_COMERCIAIS = "DESPESAS_COMERCIAIS"
    OUTRAS_RECEITAS = "OUTRAS_RECEITAS"
    DISTRIBUICAO_LUCROS = "DISTRIBUICAO_LUCROS"
    NAO_MAPEADO = "NAO_MAPEADO"



class PlanoDeContas(AuditableBase):
    """
    Conta contábil do plano de contas da empresa.
    
    Estrutura hierárquica:
    1 - ATIVO (SINTÉTICA)
      1.1 - ATIVO CIRCULANTE (SINTÉTICA)
        1.1.1 - DISPONIBILIDADES (SINTÉTICA)
          1.1.1.01 - Caixa Geral (ANALÍTICA) ← recebe lançamentos
          1.1.1.02 - Banco Inter C/C 0001 (ANALÍTICA)
    
    Para construtoras:
    1.2.1.01 - Obras em Andamento - Residencial Vila Marina
    2.1.2.01 - ISS Retido a Recolher
    2.1.2.02 - INSS Retido a Recolher
    2.1.2.03 - IR Retido a Recolher - PJ
    2.1.2.04 - PIS/COFINS/CSLL Retidos
    """
    __tablename__ = 'plano_de_contas'

    empresa_id = Column(UUID(as_uuid=True), ForeignKey('empresas.id'), nullable=True)  # NULL = padrão global

    # Hierarquia
    codigo_contabil = Column(String(30), nullable=False, index=True)   # Ex: 1.1.1.01
    conta_pai_id = Column(UUID(as_uuid=True), ForeignKey('plano_de_contas.id'), nullable=True)
    nivel = Column(Integer, nullable=False, default=1)  # 1=grupo, 2=subgrupo, etc.

    # Identificação
    descricao = Column(String(255), nullable=False)
    descricao_reduzida = Column(String(50), nullable=True)  # Para relatórios compactos

    # Classificação
    grupo = Column(Enum(GrupoConta), nullable=False)
    natureza = Column(Enum(NaturezaConta), nullable=False)
    tipo = Column(Enum(TipoConta), default=TipoConta.ANALITICA, nullable=False)
    classificacao_dre = Column(Enum(ClassificacaoDRE), nullable=True)

    # Flags operacionais
    ativa = Column(Boolean, default=True, nullable=False)
    aceita_lancamentos = Column(Boolean, default=True, nullable=False)  # False para sintéticas
    conta_caixa_banco = Column(Boolean, default=False)  # True para contas do grupo disponibilidades
    conta_resultado = Column(Boolean, default=False)    # True para receitas e despesas

    # Referências externas (mapeamento com sistemas de destino)
    codigo_dominio = Column(String(20), nullable=True)     # Código no Domínio Sistemas
    codigo_alterdata = Column(String(20), nullable=True)   # Código no Alterdata
    codigo_sped = Column(String(20), nullable=True)        # Código referencial SPED

    # Observações para o contador
    observacoes = Column(Text, nullable=True)

    # Relacionamentos
    conta_pai = relationship("PlanoDeContas", remote_side="PlanoDeContas.id")
    subcontas = relationship("PlanoDeContas", foreign_keys=[conta_pai_id])


# ============================================================
# TABELA DE REGRAS FISCAIS POR MUNICÍPIO
# ============================================================

class RegraFiscalMunicipio(AuditableBase):
    """
    Regras de ISS e retenções por município.
    
    ISS é um imposto municipal — cada prefeitura define:
    - Alíquota (geralmente entre 2% e 5%, LC 116/2003 art. 8°)
    - Se é obrigatória a retenção na fonte pelo tomador
    - Lista de serviços sujeitos à retenção
    
    Para construção civil, o ISS incide no município da obra (não da empresa).
    """
    __tablename__ = 'regras_fiscais_municipio'

    municipio_ibge = Column(String(7), nullable=False, unique=True, index=True)
    municipio_nome = Column(String(100), nullable=False)
    uf = Column(String(2), nullable=False)

    # Alíquotas de ISS (para serviços de construção civil)
    aliquota_iss_construcao = Column(String(10), nullable=True)  # Ex: "3.00" (%)
    aliquota_iss_empreitada = Column(String(10), nullable=True)
    aliquota_iss_subempreitada = Column(String(10), nullable=True)
    aliquota_iss_projetos = Column(String(10), nullable=True)  # Arquitetura, engenharia

    # Retenção na fonte obrigatória (art. 6° LC 116/2003)
    retencao_iss_obrigatoria_pj = Column(Boolean, default=True)
    retencao_iss_obrigatoria_pf = Column(Boolean, default=True)

    # Valor mínimo de ISS para retenção (alguns municípios isentam valores pequenos)
    valor_minimo_retencao_iss = Column(String(15), nullable=True)

    # Dados de recolhimento
    codigo_tributario_municipal = Column(String(20), nullable=True)
    link_legislacao = Column(String(255), nullable=True)

    # Última atualização da legislação
    data_vigencia = Column(String(10), nullable=True)  # YYYY-MM-DD
    fonte = Column(String(100), nullable=True)


# ============================================================
# TABELA DE TABELAS IRRF
# ============================================================

class TabelaIRRF(AuditableBase):
    """
    Tabela progressiva do IRRF conforme RIR/2018.
    Atualizada periodicamente por decreto presidencial.
    
    Aplicável a:
    - Pessoa Física (PF): serviços, aluguéis (art. 627 RIR)
    - Pessoa Jurídica (PJ): serviços específicos (art. 720 RIR)
    """
    __tablename__ = 'tabela_irrf'

    tipo_beneficiario = Column(String(5), nullable=False)  # PF ou PJ
    natureza_pagamento = Column(String(100), nullable=False)  # Ex: "Serviços de Construção Civil PJ"
    codigo_darf = Column(String(10), nullable=False)
    aliquota = Column(String(8), nullable=False)  # Ex: "1.50"
    deducao_parcela = Column(String(15), nullable=True)  # Para PF: parcela dedutível da tabela
    valor_minimo_retencao = Column(String(15), nullable=True)  # Valor mínimo para reter (R$)
    base_legal = Column(String(100), nullable=True)  # Ex: "RIR/2018, Art. 720, §2°"
    vigencia_inicio = Column(String(10), nullable=False)  # YYYY-MM-DD
    vigencia_fim = Column(String(10), nullable=True)
