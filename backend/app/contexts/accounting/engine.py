import uuid
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.financeiro import TituloFinanceiro, TipoTitulo, MovimentacaoFinanceira, TipoMovimentacao
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

    def translate_movimentacao_to_lancamento(self, mov: MovimentacaoFinanceira) -> LancamentoCabecalho:
        if not mov.valor or not mov.data_transacao:
            return None

        val = abs(float(mov.valor))
        if val == 0:
            return None

        cabecalho = LancamentoCabecalho(
            id=self._to_uuid(uuid.uuid4()),
            empresa_id=self._to_uuid(self.empresa_id),
            data_competencia=mov.data_transacao,
            historico_padrao=f"Movimentação Bancária: {mov.descricao_extrato or ''}",
            numero_lote=f"EXT-{mov.data_transacao.strftime('%Y%m')}",
            modulo_origem=ModuloOrigem.FINANCEIRO,
            status=StatusLancamento.CONFIRMADO
        )
        self.db.add(cabecalho)

        tipo_str = str(mov.tipo.value if hasattr(mov.tipo, 'value') else mov.tipo)
        desc_lower = str(mov.descricao_extrato or '').lower()

        # ENTRADA / CRÉDITO
        if tipo_str in ["ENTRADA", "CREDITO"] or float(mov.valor) > 0:
            # 1. Resgate de Aplicação ou Transferência Interna (Movimento Permutativo do Ativo - Sem DRE)
            if "resgate" in desc_lower or "aplicacao" in desc_lower or "aplicação" in desc_lower or "transf" in desc_lower:
                conta_debito_id = self._get_or_create_conta(
                    codigo="1.1.1.01",
                    descricao="Caixa / Bancos Conta Movimento",
                    grupo=GrupoConta.ATIVO,
                    natureza=NaturezaConta.DEVEDORA
                )
                conta_credito_id = self._get_or_create_conta(
                    codigo="1.1.2.01",
                    descricao="Aplicações Financeiras de Curto Prazo",
                    grupo=GrupoConta.ATIVO,
                    natureza=NaturezaConta.DEVEDORA,
                    classificacao_dre=None
                )
                hist_cred = f"Resgate / Transferência Interna: {mov.descricao_extrato or ''}"
            # 2. Rendimentos de Aplicação / Juros (Outras Receitas)
            elif "rendimento" in desc_lower or "juros" in desc_lower:
                conta_debito_id = self._get_or_create_conta(
                    codigo="1.1.1.01",
                    descricao="Caixa / Bancos Conta Movimento",
                    grupo=GrupoConta.ATIVO,
                    natureza=NaturezaConta.DEVEDORA
                )
                conta_credito_id = self._get_or_create_conta(
                    codigo="3.1.2.REC",
                    descricao="Rendimentos e Receitas Financeiras",
                    grupo=GrupoConta.RESULTADO,
                    natureza=NaturezaConta.CREDORA,
                    classificacao_dre=ClassificacaoDRE.OUTRAS_RECEITAS
                )
                hist_cred = f"Receita Financeira: {mov.descricao_extrato or ''}"
            # 3. Receita Bruta de Vendas / Serviços / Pix Recebido
            else:
                cat_name = mov.categoria or "Receita de Vendas e Serviços"
                classificacao = MAPA_DRE.get(mov.categoria, ClassificacaoDRE.RECEITA_BRUTA)
                conta_debito_id = self._get_or_create_conta(
                    codigo="1.1.1.01",
                    descricao="Caixa / Bancos Conta Movimento",
                    grupo=GrupoConta.ATIVO,
                    natureza=NaturezaConta.DEVEDORA
                )
                conta_credito_id = self._get_or_create_conta(
                    codigo=f"3.1.1.{cat_name[:3].upper()}",
                    descricao=f"Receita com {cat_name}",
                    grupo=GrupoConta.RESULTADO,
                    natureza=NaturezaConta.CREDORA,
                    classificacao_dre=classificacao
                )
                hist_cred = f"Crédito Bancário: {mov.descricao_extrato or ''}"

            partida_deb = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_debito_id,
                natureza=TipoPartida.DEBITO,
                valor=val,
                historico_complementar=mov.descricao_extrato
            )
            
            partida_cred = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=val,
                historico_complementar=hist_cred
            )
            self.db.add(partida_deb)
            self.db.add(partida_cred)

        # SAÍDA / DÉBITO sem título ERP conciliado = Despesa / Custo Direto
        else:
            cat_name = mov.categoria or "Despesas Diversas"
            classificacao = MAPA_DRE.get(mov.categoria, ClassificacaoDRE.DESPESAS_ADMINISTRATIVAS)
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
                valor=val,
                historico_complementar=mov.descricao_extrato
            )
            
            partida_cred = PartidaItem(
                id=self._to_uuid(uuid.uuid4()),
                empresa_id=self._to_uuid(self.empresa_id),
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=val,
                historico_complementar=f"Débito Bancário: {mov.descricao_extrato or ''}"
            )
            self.db.add(partida_deb)
            self.db.add(partida_cred)

        return cabecalho

    def process_all_liquidated(self) -> int:
        from app.models.financeiro import StatusTitulo, MovimentacaoFinanceira
        from app.models.domain import ConciliacaoItem
        emp_uuid = self._to_uuid(self.empresa_id)

        count = 0

        # 1. Processar Títulos Liquidados (Pagar e Receber do ERP)
        titulos = self.db.query(TituloFinanceiro).filter(
            TituloFinanceiro.empresa_id == emp_uuid,
            TituloFinanceiro.status == StatusTitulo.LIQUIDADO
        ).all()

        for t in titulos:
            try:
                self.translate_titulo_to_lancamento(t)
                self.db.commit()
                count += 1
            except Exception as e:
                self.db.rollback()

        # 2. Processar Movimentações Bancárias do Extrato Inter & Razão SCI
        movs = self.db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.empresa_id == emp_uuid
        ).all()

        conciliados_mov = self.db.query(ConciliacaoItem.movimentacao_financeira_id).all()
        conciliados_mov_ids = {c[0] for c in conciliados_mov if c[0]}

        for m in movs:
            if m.id in conciliados_mov_ids:
                continue
            try:
                res = self.translate_movimentacao_to_lancamento(m)
                if res:
                    self.db.commit()
                    count += 1
            except Exception as e:
                self.db.rollback()

        return count
