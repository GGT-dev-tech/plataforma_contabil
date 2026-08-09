"""
Seed de Dados: Plano de Contas para Construtoras (CFC 1.374/2011)
e Regras Fiscais dos 20 municípios com maior volume de obras no Brasil.

Execute:
    docker exec plataforma_contabil-backend-1 sh -c "cd /app && PYTHONPATH=. python scripts/seed_plano_contas.py"
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from app.api.deps import SessionLocal
from app.models.plano_contas import PlanoDeContas, RegraFiscalMunicipio, NaturezaConta, TipoConta, GrupoConta

# ============================================================
# PLANO DE CONTAS — CONSTRUTORAS
# Baseado em CFC 1.374/2011 + NBC TG 1000
# ============================================================

PLANO_CONTAS = [
    # (codigo, descricao, grupo, natureza, tipo, aceita_lancamentos)
    # ── ATIVO ─────────────────────────────────────────────────
    ("1",         "ATIVO",                                          GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1",       "ATIVO CIRCULANTE",                               GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1.1",     "DISPONIBILIDADES",                               GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1.1.01",  "Caixa Geral",                                    GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.1.02",  "Banco - Conta Corrente",                         GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.1.03",  "Banco - Conta Poupança",                         GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.1.04",  "Aplicações Financeiras de Curto Prazo",          GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.2",     "CRÉDITOS",                                       GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1.2.01",  "Clientes - Unidades a Receber",                  GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.2.02",  "Clientes - Parcelas Vencidas",                   GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.3",     "TRIBUTOS A RECUPERAR",                           GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1.3.01",  "PIS a Recuperar",                                GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.3.02",  "COFINS a Recuperar",                             GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.3.03",  "IRPJ Antecipado",                                GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.3.04",  "CSLL Antecipada",                                GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.4",     "OUTROS CRÉDITOS CIRCULANTES",                    GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.1.4.01",  "Adiantamentos a Fornecedores",                   GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.4.02",  "Adiantamentos a Empregados",                     GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.1.4.03",  "Seguros a Vencer",                               GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2",       "ATIVO NÃO CIRCULANTE",                           GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.2.1",     "OBRAS EM ANDAMENTO",                             GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.2.1.01",  "Obras em Andamento - Material",                  GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.1.02",  "Obras em Andamento - Mão de Obra Própria",       GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.1.03",  "Obras em Andamento - Subempreitada",             GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.1.04",  "Obras em Andamento - Locação Equipamentos",      GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.1.05",  "Obras em Andamento - Outros Custos Diretos",     GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.2",     "IMOBILIZADO",                                    GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.SINTETICA, False),
    ("1.2.2.01",  "Máquinas e Equipamentos",                        GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.2.02",  "Veículos",                                       GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.2.03",  "Móveis e Utensílios",                            GrupoConta.ATIVO, NaturezaConta.DEVEDORA,  TipoConta.ANALITICA, True),
    ("1.2.2.09",  "(-) Depreciação Acumulada",                      GrupoConta.ATIVO, NaturezaConta.CREDORA,   TipoConta.ANALITICA, True),

    # ── PASSIVO ───────────────────────────────────────────────
    ("2",         "PASSIVO",                                         GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1",       "PASSIVO CIRCULANTE",                              GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.1",     "FORNECEDORES",                                    GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.1.01",  "Fornecedores a Pagar - Material",                 GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.1.02",  "Fornecedores a Pagar - Serviços",                 GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.1.03",  "Fornecedores a Pagar - Subempreitadas",           GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.2",     "TRIBUTOS RETIDOS A RECOLHER",                     GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.2.01",  "ISS Retido a Recolher",                           GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.2.02",  "INSS Retido a Recolher (PJ)",                     GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.2.03",  "IRRF Retido a Recolher - PJ (DARF 6147)",         GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.2.04",  "IRRF Retido a Recolher - PF (DARF 0588)",         GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.2.05",  "PIS/COFINS/CSLL Retidos (CSRF)",                  GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.3",     "OBRIGAÇÕES TRABALHISTAS E PREVIDENCIÁRIAS",       GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.3.01",  "Salários a Pagar",                                GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.3.02",  "INSS a Recolher (Patronal)",                      GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.3.03",  "FGTS a Recolher",                                 GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.4",     "TRIBUTOS A PAGAR (APURAÇÃO PRÓPRIA)",             GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.4.01",  "IRPJ a Pagar",                                    GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.4.02",  "CSLL a Pagar",                                    GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.4.03",  "PIS a Pagar",                                     GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.4.04",  "COFINS a Pagar",                                  GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.4.05",  "RET - IRPJ/CSLL/PIS/COFINS (4%)",                GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.5",     "OUTRAS OBRIGAÇÕES",                               GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("2.1.5.01",  "Adiantamentos de Clientes (Sinais)",              GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("2.1.5.02",  "Tarifas e Encargos a Pagar",                      GrupoConta.PASSIVO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),

    # ── PATRIMÔNIO LÍQUIDO ────────────────────────────────────
    ("3",         "PATRIMÔNIO LÍQUIDO",                              GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("3.1",       "CAPITAL SOCIAL",                                  GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("3.1.1.01",  "Capital Social Integralizado",                    GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("3.2",       "RESERVAS E LUCROS",                               GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("3.2.1.01",  "Lucros ou Prejuízos Acumulados",                  GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("3.2.1.02",  "Reserva Legal",                                   GrupoConta.PATRIMONIO_LIQUIDO, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),

    # ── RECEITAS ──────────────────────────────────────────────
    ("4",         "RECEITAS",                                        GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("4.1",       "RECEITAS OPERACIONAIS",                           GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("4.1.1.01",  "Receita com Venda de Unidades - Residencial",     GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("4.1.1.02",  "Receita com Venda de Unidades - Comercial",       GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("4.1.1.03",  "Receita com Construção por Empreitada",           GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("4.1.1.04",  "Receita com Locação de Imóveis",                  GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("4.2",       "RECEITAS FINANCEIRAS",                            GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.SINTETICA, False),
    ("4.2.1.01",  "Rendimentos de Aplicações Financeiras",           GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),
    ("4.2.1.02",  "Juros Ativos / Correção Monetária",               GrupoConta.RECEITA, NaturezaConta.CREDORA, TipoConta.ANALITICA, True),

    # ── CUSTOS ────────────────────────────────────────────────
    ("5",         "CUSTO DAS OBRAS VENDIDAS (CMV)",                  GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.SINTETICA, False),
    ("5.1",       "CUSTO DIRETO DE OBRAS",                           GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.SINTETICA, False),
    ("5.1.01",    "Custo Material de Construção",                    GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("5.1.02",    "Custo Mão de Obra Própria",                       GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("5.1.03",    "Custo Subempreitada",                             GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("5.1.04",    "Custo Locação de Equipamentos",                   GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("5.1.05",    "Custo Projetos e Licenças",                       GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("5.1.06",    "Custo Encargos da Obra (INSS, FGTS)",             GrupoConta.CUSTO, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),

    # ── DESPESAS ──────────────────────────────────────────────
    ("6",         "DESPESAS OPERACIONAIS",                           GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.SINTETICA, False),
    ("6.1",       "DESPESAS ADMINISTRATIVAS",                        GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.SINTETICA, False),
    ("6.1.01",    "Despesas Administrativas Gerais",                 GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.1.02",    "Salários Administrativos",                        GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.1.03",    "Aluguel de Imóveis",                              GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.1.04",    "Energia Elétrica / Água / Telefone",              GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.1.05",    "Honorários Contábeis",                            GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.1.06",    "Seguros",                                         GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.2",       "DESPESAS FINANCEIRAS",                            GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.SINTETICA, False),
    ("6.2.01",    "Despesas Financeiras",                            GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.2.02",    "Tarifas Bancárias",                               GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.2.03",    "IOF",                                             GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
    ("6.2.04",    "Juros e Multas",                                  GrupoConta.DESPESA, NaturezaConta.DEVEDORA, TipoConta.ANALITICA, True),
]

# ============================================================
# REGRAS FISCAIS — ISS POR MUNICÍPIO
# Fonte: legislação municipal de cada cidade (2026)
# Alíquotas para "Construção Civil" — Lista Anexo da LC 116/2003, item 7
# ============================================================

REGRAS_MUNICIPIOS = [
    # (ibge, nome, uf, aliq_construcao, aliq_empreitada, aliq_subempr, retencao_obrig)
    ("3550308", "São Paulo",        "SP", "3.00", "3.00", "3.00", True),
    ("3304557", "Rio de Janeiro",   "RJ", "5.00", "5.00", "5.00", True),
    ("3106200", "Belo Horizonte",   "MG", "2.00", "2.00", "2.00", True),
    ("2927408", "Salvador",         "BA", "3.00", "3.00", "3.00", True),
    ("2611606", "Recife",           "PE", "5.00", "5.00", "5.00", True),
    ("2304400", "Fortaleza",        "CE", "2.00", "2.00", "2.00", True),
    ("1302603", "Manaus",           "AM", "3.00", "3.00", "3.00", True),
    ("4314902", "Porto Alegre",     "RS", "3.00", "3.00", "3.00", True),
    ("4106902", "Curitiba",         "PR", "5.00", "5.00", "5.00", True),
    ("5300108", "Brasília",         "DF", "2.00", "2.00", "2.00", True),
    ("3518800", "Guarulhos",        "SP", "2.00", "2.00", "2.00", True),
    ("3509502", "Campinas",         "SP", "3.00", "3.00", "3.00", True),
    ("3548708", "São Bernardo",     "SP", "2.00", "2.00", "2.00", True),
    ("3529401", "Manaus",           "AM", "3.00", "3.00", "3.00", True),
    ("1501402", "Belém",            "PA", "3.00", "3.00", "3.00", True),
    ("2111300", "São Luís",         "MA", "3.00", "3.00", "3.00", True),
    ("2800308", "Aracaju",          "SE", "2.00", "2.00", "2.00", True),
    ("5208707", "Goiânia",          "GO", "3.00", "3.00", "3.00", True),
    ("3170206", "Uberlândia",       "MG", "2.00", "2.00", "2.00", True),
    ("3543402", "Ribeirão Preto",   "SP", "2.00", "2.00", "2.00", True),
]


def seed_plano_contas(db):
    existing = db.query(PlanoDeContas).filter(PlanoDeContas.empresa_id == None).count()
    if existing > 0:
        print(f"  ⏭  Plano de contas global já existe ({existing} contas). Pulando.")
        return

    # Criar mapa de código → id para resolver hierarquia
    id_map = {}

    for (codigo, descricao, grupo, natureza, tipo, aceita) in PLANO_CONTAS:
        # Determinar conta pai
        partes = codigo.split('.')
        pai_codigo = '.'.join(partes[:-1]) if len(partes) > 1 else None
        pai_id = id_map.get(pai_codigo) if pai_codigo else None

        conta = PlanoDeContas(
            id=uuid.uuid4(),
            empresa_id=None,  # NULL = padrão global
            codigo_contabil=codigo,
            descricao=descricao,
            grupo=grupo,
            natureza=natureza,
            tipo=tipo,
            nivel=len(partes),
            aceita_lancamentos=aceita,
            conta_caixa_banco="1.1.1" in codigo,
            conta_resultado=grupo in (GrupoConta.RECEITA, GrupoConta.DESPESA, GrupoConta.CUSTO),
            conta_pai_id=pai_id,
            ativa=True,
        )
        db.add(conta)
        db.flush()  # para obter o id gerado
        id_map[codigo] = conta.id

    db.commit()
    print(f"  ✅ {len(PLANO_CONTAS)} contas do Plano de Contas inseridas.")


def seed_regras_municipios(db):
    existing = db.query(RegraFiscalMunicipio).count()
    if existing > 0:
        print(f"  ⏭  Regras fiscais já existem ({existing} municípios). Pulando.")
        return

    for (ibge, nome, uf, aliq_c, aliq_e, aliq_s, retencao) in REGRAS_MUNICIPIOS:
        regra = RegraFiscalMunicipio(
            id=uuid.uuid4(),
            municipio_ibge=ibge,
            municipio_nome=nome,
            uf=uf,
            aliquota_iss_construcao=aliq_c,
            aliquota_iss_empreitada=aliq_e,
            aliquota_iss_subempreitada=aliq_s,
            retencao_iss_obrigatoria_pj=retencao,
            retencao_iss_obrigatoria_pf=retencao,
            fonte="Legislação municipal 2026 — verificar vigência",
        )
        db.add(regra)

    db.commit()
    print(f"  ✅ {len(REGRAS_MUNICIPIOS)} regras fiscais municipais inseridas.")


if __name__ == '__main__':
    print("\n===== SEED: Plano de Contas + Regras Fiscais =====\n")
    db = SessionLocal()
    try:
        seed_plano_contas(db)
        seed_regras_municipios(db)
        print("\n✅ Seed concluído com sucesso!\n")
    finally:
        db.close()
