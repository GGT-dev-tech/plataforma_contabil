import logging
import pandas as pd
from sqlalchemy.orm import Session
import uuid
from app.models.domain import (
    TipoArquivo, Despesa, ParcelaDespesa, Fornecedor, 
    Projeto, ContaBancaria, CategoriaFinanceira, Empresa
)
from app.services.parsers.base import ImportAdapter

logger = logging.getLogger(__name__)

class DespesasERPAdapter(ImportAdapter):
    
    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if tipo_arquivo != TipoArquivo.DESPESA:
            return False
        try:
            # Lemos a primeira linha de dados reais para ver as colunas
            df = pd.read_excel(file_path, nrows=5)
            cols = set([str(c).lower().strip() for c in df.columns])
            # Se tiver ID Parcela e Valor parcela, é o ERP Despesas
            if 'id parcela' in cols and 'valor parcela' in cols and 'fornecedor' in cols:
                return True
        except Exception:
            pass
        return False
        
    def _get_or_create(self, db_session: Session, model, cache: dict, name: str, name_field='nome', **kwargs):
        if not name or str(name).strip() == "" or pd.isna(name):
            return None
        name_clean = str(name).strip()
        name_upper = name_clean.upper()
        
        if name_upper in cache:
            return cache[name_upper]
            
        kwargs[name_field] = name_clean
        obj = model(**kwargs)
        if hasattr(model, 'nome_normalizado'):
            obj.nome_normalizado = name_upper
            
        db_session.add(obj)
        db_session.flush() # pra gerar ID
        cache[name_upper] = obj
        return obj

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        logger.info(f"Usando DespesasERPAdapter para arquivo {file_path}")
        df = pd.read_excel(file_path)
        
        # Mapeamento para lower
        df.columns = df.columns.str.lower().str.strip()
        
        # Caches
        cache_forn = {f.nome_normalizado: f for f in db_session.query(Fornecedor).all()}
        cache_proj = {p.nome.upper(): p for p in db_session.query(Projeto).all()}
        cache_conta = {c.banco.upper(): c for c in db_session.query(ContaBancaria).all() if c.banco}
        cache_categ = {c.nome.upper(): c for c in db_session.query(CategoriaFinanceira).all()}
        cache_emp = {e.razao_social.upper(): e for e in db_session.query(Empresa).all() if e.razao_social}
        
        despesas_por_id = {}
        novas_parcelas = 0
        
        for idx, row in df.iterrows():
            id_despesa = str(row.get('id', '')).strip()
            if not id_despesa or pd.isna(row.get('id')):
                continue
                
            valor_parcela = self._parse_float(row.get('valor parcela', 0.0))
            if valor_parcela == 0.0:
                continue
                
            # Recuperar Despesa Pai (ou criar)
            if id_despesa not in despesas_por_id:
                forn = self._get_or_create(db_session, Fornecedor, cache_forn, row.get('fornecedor'))
                proj = self._get_or_create(db_session, Projeto, cache_proj, row.get('projeto'))
                # 'conta bancária' vai pra ContaBancaria(banco=nome) como fallback pro modelo atual
                conta = self._get_or_create(db_session, ContaBancaria, cache_conta, row.get('conta bancária'), name_field='banco')
                categ = self._get_or_create(db_session, CategoriaFinanceira, cache_categ, row.get('categoria financeira'))
                
                despesa = Despesa(
                    execucao_id=execucao_id,
                    id_uuid_origem=id_despesa,
                    fornecedor_id=forn.id if forn else None,
                    projeto_id=proj.id if proj else None,
                    categoria_id=categ.id if categ else None,
                    valor_total=self._parse_float(row.get('valor total', 0.0)),
                    data_emissao=self._parse_date(row.get('data de competência')),
                    # O status da despesa em si:
                    # 'status': 'Pago' ou 'Em aberto' (não temos esse campo diretamente, ou temos? 
                    # status_parcela que nos importa mais)
                )
                db_session.add(despesa)
                db_session.flush()
                despesas_por_id[id_despesa] = despesa

            despesa_pai = despesas_por_id[id_despesa]
            
            # Criar Parcela
            id_parcela = str(row.get('id parcela', str(uuid.uuid4()))).strip()
            
            # extrair numero da parcela de "1/4" ou algo assim em "parcela"
            desc_parcela = str(row.get('parcela', ''))
            
            parcela = ParcelaDespesa(
                despesa_id=despesa_pai.id,
                id_parcela_origem=id_parcela,
                valor=valor_parcela,
                data_vencimento=self._parse_date(row.get('vencimento parcela')),
                data_pagamento_esperada=self._parse_date(row.get('data de pagamento parcela')),
                numero_parcela=novas_parcelas + 1 # Pode ser melhorado depois
            )
            db_session.add(parcela)
            novas_parcelas += 1
            
        db_session.commit()
        logger.info(f"DespesasERPAdapter: {novas_parcelas} parcelas inseridas")
        return True
