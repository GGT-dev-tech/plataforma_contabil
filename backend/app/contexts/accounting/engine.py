import uuid
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.financeiro import TituloFinanceiro, TipoTitulo
from app.models.ledger import LancamentoCabecalho, PartidaItem, ModuloOrigem, TipoPartida, StatusLancamento
from app.models.plano_contas import PlanoDeContas, GrupoConta

class AccountingEngine:
    def __init__(self, db: Session, empresa_id: str):
        self.db = db
        self.empresa_id = empresa_id
        self._cache_contas = {}

    def _get_or_create_conta(self, codigo: str, descricao: str, grupo: GrupoConta, natureza: str) -> str:
        """
        Busca uma conta pelo código ou cria caso não exista (mock simplificado para o MVP).
        Na arquitetura ideal, o plano de contas deve ser pre-populado.
        """
        if codigo in self._cache_contas:
            return self._cache_contas[codigo]
            
        conta = self.db.query(PlanoDeContas).filter_by(
            empresa_id=self.empresa_id,
            codigo_contabil=codigo
        ).first()
        
        if not conta:
            conta = PlanoDeContas(
                id=str(uuid.uuid4()),
                empresa_id=self.empresa_id,
                codigo_contabil=codigo,
                descricao=descricao,
                grupo=grupo,
                natureza=natureza
            )
            self.db.add(conta)
            self.db.flush()
            
        self._cache_contas[codigo] = conta.id
        return conta.id

    def translate_titulo_to_lancamento(self, titulo: TituloFinanceiro) -> LancamentoCabecalho:
        """
        Traduz um Título Financeiro para um Lançamento Contábil de Partidas Dobradas.
        Se o título for do tipo DESPESA e estiver PAGO:
        - Débito: Despesa (DRE) - baseada na categoria
        - Crédito: Banco / Caixa (Ativo)
        """
        if not titulo.valor_pago or not titulo.data_pagamento:
            raise ValueError("O título precisa estar liquidado (valor e data de pagamento) para gerar o lançamento contábil neste escopo simplificado.")

        # 1. Cria o Cabeçalho
        cabecalho = LancamentoCabecalho(
            id=str(uuid.uuid4()),
            empresa_id=self.empresa_id,
            data_competencia=titulo.data_pagamento,
            historico_padrao=f"Pgto. ref. a {titulo.descricao} - {titulo.fornecedor_cliente_nome or ''}",
            numero_lote=f"FIN-{titulo.data_pagamento.strftime('%Y%m')}",
            modulo_origem=ModuloOrigem.FINANCEIRO,
            status=StatusLancamento.CONFIRMADO,
            documento_fiscal_id=titulo.documento_fiscal_id,
            obra_id=titulo.obra_id
        )
        self.db.add(cabecalho)

        # 2. Mapeia as Contas (Simplificação)
        if titulo.tipo == TipoTitulo.DESPESA:
            # Conta a Debitar (Despesa)
            # Idealmente, haveria um de-para de 'categoria' para 'conta_id'
            cat_name = titulo.categoria or "Despesas Gerais"
            conta_debito_id = self._get_or_create_conta(
                codigo=f"3.1.1.{cat_name[:3].upper()}", # Fake code
                descricao=f"Despesa com {cat_name}",
                grupo=GrupoConta.RESULTADO,
                natureza="DEVEDORA"
            )
            
            # Conta a Creditar (Caixa/Banco)
            conta_credito_id = self._get_or_create_conta(
                codigo="1.1.1.01",
                descricao="Caixa / Bancos Conta Movimento",
                grupo=GrupoConta.ATIVO,
                natureza="DEVEDORA"
            )
            
            partida_deb = PartidaItem(
                id=str(uuid.uuid4()),
                empresa_id=self.empresa_id,
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_debito_id,
                natureza=TipoPartida.DEBITO,
                valor=titulo.valor_pago,
                historico_complementar=titulo.descricao
            )
            
            partida_cred = PartidaItem(
                id=str(uuid.uuid4()),
                empresa_id=self.empresa_id,
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=titulo.valor_pago,
                historico_complementar=f"Pagamento via {titulo.fornecedor_cliente_nome or 'Caixa'}"
            )
            
            self.db.add(partida_deb)
            self.db.add(partida_cred)
            
        elif titulo.tipo == TipoTitulo.RECEITA:
            # Conta a Debitar (Caixa/Banco)
            conta_debito_id = self._get_or_create_conta(
                codigo="1.1.1.01",
                descricao="Caixa / Bancos Conta Movimento",
                grupo=GrupoConta.ATIVO,
                natureza="DEVEDORA"
            )
            
            # Conta a Creditar (Receita)
            cat_name = titulo.categoria or "Serviços Prestados"
            conta_credito_id = self._get_or_create_conta(
                codigo=f"3.1.1.{cat_name[:3].upper()}",
                descricao=f"Receita com {cat_name}",
                grupo=GrupoConta.RESULTADO,
                natureza="CREDORA"
            )
            
            partida_deb = PartidaItem(
                id=str(uuid.uuid4()),
                empresa_id=self.empresa_id,
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_debito_id,
                natureza=TipoPartida.DEBITO,
                valor=titulo.valor_pago,
                historico_complementar=f"Recebimento de {titulo.fornecedor_cliente_nome or 'Cliente'}"
            )
            
            partida_cred = PartidaItem(
                id=str(uuid.uuid4()),
                empresa_id=self.empresa_id,
                cabecalho_id=cabecalho.id,
                conta_contabil_id=conta_credito_id,
                natureza=TipoPartida.CREDITO,
                valor=titulo.valor_pago,
                historico_complementar=titulo.descricao
            )
            
            self.db.add(partida_deb)
            self.db.add(partida_cred)
            
        self.db.flush()
        return cabecalho

    def process_all_liquidated(self):
        """
        Gera lançamentos contábeis para todos os títulos liquidados que ainda não possuem lançamento.
        (Em um sistema real, haveria um campo 'lancamento_id' no titulo ou uma tabela associativa)
        """
        # Simplificação: Busca títulos pagos que não estão vinculados a um LancamentoCabecalho
        titulos_pagos = self.db.query(TituloFinanceiro).filter(
            TituloFinanceiro.empresa_id == self.empresa_id,
            TituloFinanceiro.valor_pago != None,
            TituloFinanceiro.data_pagamento != None
        ).all()
        
        processados = 0
        for titulo in titulos_pagos:
            # Verifica se já existe um cabecalho que refere a este titulo
            existe = self.db.query(LancamentoCabecalho).filter(
                LancamentoCabecalho.empresa_id == self.empresa_id,
                LancamentoCabecalho.historico_padrao.like(f"%{titulo.descricao}%") # heurística por falta de FK direta no MVP
            ).first()
            
            if not existe:
                try:
                    self.translate_titulo_to_lancamento(titulo)
                    processados += 1
                except Exception as e:
                    # Log the error but continue
                    print(f"Erro ao contabilizar titulo {titulo.id}: {e}")
                    
        self.db.commit()
        return processados
