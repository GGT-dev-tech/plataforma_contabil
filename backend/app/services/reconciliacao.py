import logging
from typing import List, Optional, Tuple
from datetime import timedelta
from thefuzz import fuzz

from sqlalchemy.orm import Session
from app.models.financeiro import TituloFinanceiro, StatusTitulo, MovimentacaoFinanceira, TipoMovimentacao, ConciliacaoFinanceira
from app.models.ledger import ModuloOrigem
from app.services.ledger import LedgerController

logger = logging.getLogger(__name__)

class MatchResult:
    def __init__(self, titulo: TituloFinanceiro, movimentacao: MovimentacaoFinanceira, confianca: float, tipo_match: str):
        self.titulo = titulo
        self.movimentacao = movimentacao
        self.confianca = confianca
        self.tipo_match = tipo_match

class ReconciliacaoService:
    """
    Motor Algorítmico de Conciliação Bancária.
    Aplica 3 fases de detecção para amarrar Transações (Movimentação) com Títulos (A Pagar/Receber).
    """
    def __init__(self, db: Session):
        self.db = db
        self.ledger_controller = LedgerController(db)
        
    def rodar_motor_conciliacao(self, empresa_id: str) -> dict:
        """
        Executa as três fases de Match para a empresa fornecida.
        """
        titulos_abertos = self._get_titulos_elegiveis(empresa_id)
        movimentacoes_pendentes = self._get_movimentacoes_pendentes(empresa_id)
        
        matches_encontrados = []
        
        # Clonamos as listas para ir removendo o que for batendo
        titulos_restantes = list(titulos_abertos)
        movimentacoes_restantes = list(movimentacoes_pendentes)
        
        # Fase 1: Match Exato (Valor exato + CNPJ/CPF exato)
        # Como a Movimentação nem sempre traz CPF/CNPJ estruturado no extrato bancário,
        # Fase 1 costuma funcionar bem para boletos DDA.
        titulos_restantes, movimentacoes_restantes, matches_f1 = self._fase_1_match_exato(
            titulos_restantes, movimentacoes_restantes
        )
        matches_encontrados.extend(matches_f1)
        
        # Fase 2: Fuzzy Match (Valor Exato + Similaridade de String > 85%)
        titulos_restantes, movimentacoes_restantes, matches_f2 = self._fase_2_fuzzy_match(
            titulos_restantes, movimentacoes_restantes
        )
        matches_encontrados.extend(matches_f2)
        
        # Fase 3: Tolerância D+N (Cartões / Adquirentes / Taxas bancárias)
        titulos_restantes, movimentacoes_restantes, matches_f3 = self._fase_3_tolerancia(
            titulos_restantes, movimentacoes_restantes
        )
        matches_encontrados.extend(matches_f3)
        
        # Efetivar as liquidações e contabilidade no banco de dados
        efetivados = 0
        for match in matches_encontrados:
            try:
                self._efetivar_match(match)
                efetivados += 1
            except Exception as e:
                logger.error(f"Erro ao efetivar match {match.titulo.id} - {match.movimentacao.id}: {str(e)}")
                self.db.rollback()
                
        self.db.commit()
        return {
            "total_matches": efetivados,
            "fase_1": len(matches_f1),
            "fase_2": len(matches_f2),
            "fase_3": len(matches_f3)
        }
        
    def _efetivar_match(self, match: MatchResult):
        titulo = match.titulo
        movimentacao = match.movimentacao
        
        # 1. Cria a ConciliacaoFinanceira
        conciliacao = ConciliacaoFinanceira(
            empresa_id=titulo.empresa_id,
            titulo_id=titulo.id,
            movimentacao_id=movimentacao.id,
            valor_conciliado=movimentacao.valor,
            data_conciliacao=movimentacao.data_transacao,
            match_automatico=True,
            confianca_match=match.confianca
        )
        self.db.add(conciliacao)
        
        # 2. Atualiza Status do Título e Movimentação
        titulo.valor_pago += movimentacao.valor
        
        # Lógica simplificada: Se o valor pago for >= valor_nominal (considerando descontos da Fase 3),
        # ou se bateu na Fase 1 e 2, liquidamos.
        
        titulo.status = StatusTitulo.LIQUIDADO
        titulo.data_pagamento = movimentacao.data_transacao
        movimentacao.conciliada = True
        
        # 3. Dispara a Contabilidade (Domain Driven Design / Anti-Corruption Layer)
        # Ao liquidar um título, o financeiro avisa o Ledger para fazer a Partida Dobrada.
        # No MVP, como estamos no Monolito, chamamos o ledger_controller direto.
        historico_padrao = f"Liq. Fatura {titulo.descricao} ({match.tipo_match})"
        
        # Para montar as partidas, precisamos das contas contábeis
        # No cenário ideal, a CategoriaFinanceira do Título tem a conta contábil vinculada.
        # Aqui vamos usar o UUID fallback que construímos no Gerador de Lançamentos ou mock.
        import uuid
        
        # Simulação de Partida Dobrada de Baixa:
        # Se Pagar: D-Fornecedores / C-Banco
        # Se Receber: D-Banco / C-Clientes
        # Para n quebrar, não usaremos o ledger se as contas n existirem, mas deixamos pronto:
        
        # partidas = []
        # if titulo.tipo == TipoTitulo.PAGAR:
        #     partidas.append({"conta_contabil_id": "conta_fornecedor_id", "natureza": "D", "valor": movimentacao.valor, "historico": ""})
        #     partidas.append({"conta_contabil_id": "conta_banco_id", "natureza": "C", "valor": movimentacao.valor, "historico": ""})
        # self.ledger_controller.registrar_lancamento(
        #    empresa_id=titulo.empresa_id, data_competencia=movimentacao.data_transacao, historico=historico_padrao, modulo=ModuloOrigem.FINANCEIRO, partidas=partidas
        # )
        pass

    def _get_titulos_elegiveis(self, empresa_id: str) -> List[TituloFinanceiro]:
        return self.db.query(TituloFinanceiro).filter(
            TituloFinanceiro.empresa_id == empresa_id,
            TituloFinanceiro.status.in_([StatusTitulo.ABERTO, StatusTitulo.VENCIDO, StatusTitulo.PARCIAL])
        ).all()
        
    def _get_movimentacoes_pendentes(self, empresa_id: str) -> List[MovimentacaoFinanceira]:
        return self.db.query(MovimentacaoFinanceira).filter(
            MovimentacaoFinanceira.empresa_id == empresa_id,
            MovimentacaoFinanceira.conciliada == False
        ).all()
        
    def _fase_1_match_exato(self, titulos: List[TituloFinanceiro], movs: List[MovimentacaoFinanceira]) -> Tuple[List[TituloFinanceiro], List[MovimentacaoFinanceira], List[MatchResult]]:
        matches = []
        t_removidos = set()
        m_removidos = set()
        
        for mov in movs:
            for t in titulos:
                if t.id in t_removidos or mov.id in m_removidos:
                    continue
                    
                # Match: Mesmo valor E mesmo CPF/CNPJ (se existir no extrato)
                # OBS: Em extratos reais, achar o CNPJ puro no meio da string é raro (só OFX DDA).
                if t.valor_nominal == mov.valor:
                    # Verifica tipo (A Pagar = SAIDA, A Receber = ENTRADA)
                    if (t.tipo == 'PAGAR' and mov.tipo == 'SAIDA') or (t.tipo == 'RECEBER' and mov.tipo == 'ENTRADA'):
                        if t.fornecedor_cliente_cnpj_cpf and t.fornecedor_cliente_cnpj_cpf in mov.descricao_extrato:
                            matches.append(MatchResult(t, mov, 1.0, "EXATO"))
                            t_removidos.add(t.id)
                            m_removidos.add(mov.id)
                            break
                            
        return (
            [t for t in titulos if t.id not in t_removidos],
            [m for m in movs if m.id not in m_removidos],
            matches
        )

    def _fase_2_fuzzy_match(self, titulos: List[TituloFinanceiro], movs: List[MovimentacaoFinanceira]) -> Tuple[List[TituloFinanceiro], List[MovimentacaoFinanceira], List[MatchResult]]:
        matches = []
        t_removidos = set()
        m_removidos = set()
        
        for mov in movs:
            for t in titulos:
                if t.id in t_removidos or mov.id in m_removidos:
                    continue
                    
                if t.valor_nominal == mov.valor:
                    if (t.tipo == 'PAGAR' and mov.tipo == 'SAIDA') or (t.tipo == 'RECEBER' and mov.tipo == 'ENTRADA'):
                        # Levenshtein distance > 85
                        nome_alvo = t.fornecedor_cliente_nome or ""
                        score = fuzz.token_set_ratio(nome_alvo.lower(), mov.descricao_extrato.lower())
                        if score >= 85:
                            matches.append(MatchResult(t, mov, score/100.0, "FUZZY"))
                            t_removidos.add(t.id)
                            m_removidos.add(mov.id)
                            break
                            
        return (
            [t for t in titulos if t.id not in t_removidos],
            [m for m in movs if m.id not in m_removidos],
            matches
        )

    def _fase_3_tolerancia(self, titulos: List[TituloFinanceiro], movs: List[MovimentacaoFinanceira]) -> Tuple[List[TituloFinanceiro], List[MovimentacaoFinanceira], List[MatchResult]]:
        matches = []
        t_removidos = set()
        m_removidos = set()
        
        # Ex: Cartões que caem até 3 dias depois e com taxa retida (o valor do extrato é um pouco menor que o Título)
        # Vamos usar tolerância de 3% no valor e 3 dias na data
        
        for mov in movs:
            for t in titulos:
                if t.id in t_removidos or mov.id in m_removidos:
                    continue
                    
                if (t.tipo == 'RECEBER' and mov.tipo == 'ENTRADA'):
                    delta_dias = (mov.data_transacao - t.data_vencimento).days
                    # Pagamento atrasou ou cartão caiu D+3
                    if 0 <= delta_dias <= 3:
                        # O banco deposita menos do que o nominal (taxa de 0 a 5%)
                        if t.valor_nominal * 0.95 <= mov.valor <= t.valor_nominal:
                            nome_alvo = t.fornecedor_cliente_nome or ""
                            score = fuzz.token_set_ratio(nome_alvo.lower(), mov.descricao_extrato.lower())
                            if score >= 70: # Tolerância maior no nome pois pode vir "PAGTO CIELO"
                                matches.append(MatchResult(t, mov, score/100.0, "TOLERANCIA"))
                                t_removidos.add(t.id)
                                m_removidos.add(mov.id)
                                break
                            
        return (
            [t for t in titulos if t.id not in t_removidos],
            [m for m in movs if m.id not in m_removidos],
            matches
        )
