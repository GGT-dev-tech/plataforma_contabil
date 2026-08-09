"""
Parser de NF-e (Nota Fiscal Eletrônica) — XML SEFAZ
Substitui o GenericXMLAdapter com semântica fiscal real.

Suporta:
- NF-e 4.0 (layout vigente)
- NFS-e ABRASF 2.04 (padrão das prefeituras)
- Arquivo com múltiplas NF-e (lote de NF-e)
- Validação da chave de acesso (44 dígitos)

Ao invés de ir para StagingRegistro genérico, cria DocumentoFiscalV2
com todos os campos fiscais preenchidos.

Referências:
- NT 2019.001: NF-e 4.0 (schema nfe_v4.00.xsd)
- Schema ABRASF: NFS-e 2.04
"""
import logging
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional
from sqlalchemy.orm import Session

from app.contexts.staging_ingestion.parsers.base import ImportAdapter
from app.models.domain import TipoArquivo, TipoStaging, StagingRegistro, ExecucaoPipeline
from app.models.documento_fiscal import (
    DocumentoFiscalV2,
    TipoDocumentoFiscal,
    NaturezaOperacao,
    StatusDocumentoFiscal,
    ParcelaDocumentoFiscal,
)

logger = logging.getLogger(__name__)

# Namespace padrão NF-e 4.0
NFE_NS = "http://www.portalfiscal.inf.br/nfe"
# ABRASF NFS-e (padrão municipal)
NFSE_NS = "http://www.abrasf.org.br/nfse.xsd"


def _strip_ns(tag: str) -> str:
    """Remove namespace de uma tag XML."""
    return tag.split('}', 1)[1] if '}' in tag else tag


def _find(node, *paths) -> Optional[str]:
    """Busca texto em múltiplos caminhos possíveis (compatibilidade NF-e 3.x e 4.0)."""
    for path in paths:
        el = node.find(path)
        if el is not None and el.text:
            return el.text.strip()
    return None


def _decimal(val: Optional[str]) -> Decimal:
    if not val:
        return Decimal('0.00')
    try:
        return Decimal(val.replace(',', '.'))
    except InvalidOperation:
        return Decimal('0.00')


def _parse_date_nfe(val: Optional[str]) -> Optional[date]:
    """Parseia data no formato NF-e: '2026-06-11T00:00:00-03:00' ou '2026-06-11'."""
    if not val:
        return None
    try:
        return datetime.strptime(val[:10], '%Y-%m-%d').date()
    except Exception:
        return None


def _validar_chave_acesso(chave: str) -> bool:
    """
    Valida chave de acesso NF-e: 44 dígitos numéricos.
    Verificação completa do dígito verificador (módulo 11).
    """
    if not chave or not chave.isdigit() or len(chave) != 44:
        return False

    # Verificação do dígito verificador (último dígito)
    nums = [int(c) for c in chave[:43]]
    multiplicadores = list(range(2, 10)) * 6  # 2..9 repetido
    multiplicadores = multiplicadores[:43]

    soma = sum(n * m for n, m in zip(reversed(nums), multiplicadores))
    resto = soma % 11
    dv_calculado = 0 if resto < 2 else 11 - resto
    return int(chave[43]) == dv_calculado


def _inferir_natureza_cfop(cfop: Optional[str]) -> NaturezaOperacao:
    """
    Infere NaturezaOperacao com base no CFOP da NF-e.
    CFOPs relevantes para construção civil.
    """
    if not cfop:
        return NaturezaOperacao.MATERIAL

    cfop_map = {
        # Compra de material
        '1102': NaturezaOperacao.MATERIAL,  '2102': NaturezaOperacao.MATERIAL,
        '1101': NaturezaOperacao.MATERIAL,  '2101': NaturezaOperacao.MATERIAL,
        '1403': NaturezaOperacao.MATERIAL,  '2403': NaturezaOperacao.MATERIAL,
        # Serviços (NF-e de serviço, raro mas existe)
        '1933': NaturezaOperacao.SERVICO,   '2933': NaturezaOperacao.SERVICO,
        # Subcontratação
        '1925': NaturezaOperacao.SUBEMPREITADA,
    }
    return cfop_map.get(cfop[:4], NaturezaOperacao.MATERIAL)


class NFeXMLAdapter(ImportAdapter):
    """
    Parser NF-e 4.0 e NFS-e ABRASF.
    Cria DocumentoFiscalV2 com campos fiscais completos.
    """

    def can_parse(self, file_path: str, tipo_arquivo: TipoArquivo) -> bool:
        if not file_path.lower().endswith('.xml'):
            return False
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            tag = _strip_ns(root.tag)
            # NF-e: raiz nfeProc ou NFe; NFS-e: raiz CompNfse ou NFSe
            return tag in ('nfeProc', 'NFe', 'CompNfse', 'NFSe', 'loteNfe', 'enviNFe')
        except Exception:
            return False

    def parse(self, file_path: str, db_session: Session, execucao_id: str) -> bool:
        try:
            execucao = db_session.query(ExecucaoPipeline).filter_by(id=execucao_id).first()
            empresa_id = execucao.empresa_id if execucao else None

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                xml_content = f.read()

            tree = ET.fromstring(xml_content)

            # Normalizar namespaces
            for el in tree.iter():
                el.tag = _strip_ns(el.tag)

            root_tag = tree.tag
            logger.info(f"NFeXMLAdapter: processando {root_tag} — {file_path}")

            if root_tag in ('nfeProc', 'NFe', 'enviNFe', 'loteNfe'):
                return self._parse_nfe(tree, db_session, execucao_id, empresa_id, xml_content)
            elif root_tag in ('CompNfse', 'NFSe', 'ListaNfse'):
                return self._parse_nfse(tree, db_session, execucao_id, empresa_id, xml_content)
            else:
                logger.warning(f"NFeXMLAdapter: tag raiz desconhecida: {root_tag}")
                return False

        except Exception as e:
            logger.error(f"NFeXMLAdapter: falha ao processar {file_path}: {e}", exc_info=True)
            return False

    def _parse_nfe(self, root, db_session, execucao_id, empresa_id, xml_raw) -> bool:
        """Processa NF-e 4.0 (mercadorias/materiais)."""
        # Encontrar todos os nós infNFe (pode ser lote)
        inf_nodes = root.findall('.//infNFe')
        if not inf_nodes:
            inf_nodes = [root]

        count = 0
        for inf in inf_nodes:
            try:
                # Chave de acesso
                chave = inf.get('Id', '').replace('NFe', '')
                if not chave:
                    chave_el = root.find('.//chNFe')
                    chave = chave_el.text if chave_el is not None else ''

                # Emitente
                emit = inf.find('.//emit') or inf.find('emit')
                emit_cnpj = _find(emit, 'CNPJ') if emit is not None else None
                emit_nome = _find(emit, 'xNome', 'xFant') if emit is not None else None
                emit_mun = _find(emit, './/xMun') if emit is not None else None
                emit_mun_ibge = _find(emit, './/cMun') if emit is not None else None

                # Datas
                ide = inf.find('.//ide') or inf.find('ide')
                data_emissao = _parse_date_nfe(_find(ide, 'dhEmi', 'dEmi')) if ide is not None else date.today()

                # Valores
                total = inf.find('.//ICMSTot') or inf.find('.//total')
                valor_bruto = _decimal(_find(total, 'vNF', 'vTotBC')) if total is not None else Decimal('0')
                valor_desc = _decimal(_find(total, 'vDesc')) if total is not None else Decimal('0')

                # CFOP (primeiro item)
                primeiro_det = inf.find('.//det')
                cfop = _find(primeiro_det, './/CFOP') if primeiro_det is not None else None
                ncm = _find(primeiro_det, './/NCM') if primeiro_det is not None else None
                natureza = _inferir_natureza_cfop(cfop)

                # Número e série
                numero = _find(ide, 'nNF') if ide is not None else None
                serie = _find(ide, 'serie') if ide is not None else None

                # Verificar duplicidade pela chave
                if chave and len(chave) == 44:
                    existente = db_session.query(DocumentoFiscalV2).filter_by(
                        chave_acesso=chave
                    ).first()
                    if existente:
                        logger.info(f"NF-e {chave} já importada. Pulando.")
                        continue

                doc = DocumentoFiscalV2(
                    id=uuid.uuid4(),
                    empresa_id=empresa_id,
                    execucao_id=execucao_id,
                    tipo=TipoDocumentoFiscal.NFE,
                    natureza_operacao=natureza,
                    status=StatusDocumentoFiscal.PENDENTE,
                    numero=numero,
                    serie=serie,
                    chave_acesso=chave if len(chave) == 44 else None,
                    data_emissao=data_emissao or date.today(),
                    data_entrada=date.today(),
                    emitente_cnpj_cpf=emit_cnpj,
                    emitente_nome=emit_nome,
                    emitente_municipio_ibge=emit_mun_ibge,
                    emitente_municipio_nome=emit_mun,
                    valor_bruto=valor_bruto,
                    valor_desconto=valor_desc,
                    cfop=cfop,
                    ncm=ncm,
                    importado_via="XML_NFE",
                    xml_original=xml_raw[:65535] if xml_raw else None,
                    # NF-e de material geralmente não tem retenções (ISS/INSS)
                    iss_retido_fonte=False,
                    inss_retido=False,
                    ir_retido=False,
                    csrf_retido=False,
                )
                db_session.add(doc)
                db_session.flush()

                # Criar parcela padrão (1x, vencimento = data emissão)
                # Em produção: ler cobrança do XML para parcelas reais
                parcela = ParcelaDocumentoFiscal(
                    id=uuid.uuid4(),
                    documento_id=doc.id,
                    numero_parcela='1/1',
                    valor_parcela=valor_bruto - valor_desc,
                    data_vencimento=data_emissao or date.today(),
                    status='A_VENCER',
                )
                db_session.add(parcela)

                # Também criar StagingRegistro para exibição na tela de revisão
                staging = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=TipoStaging.DESPESA,
                    data=data_emissao or date.today(),
                    descricao=f"NF-e {numero} | {emit_nome or 'Fornecedor'}",
                    valor=-(float(valor_bruto - valor_desc)),
                    entidade_nome=emit_nome,
                    cnpj_cpf=emit_cnpj,
                    processado=False,
                )
                db_session.add(staging)
                count += 1

            except Exception as e:
                logger.error(f"Erro ao processar infNFe: {e}", exc_info=True)
                continue

        db_session.commit()
        logger.info(f"NFeXMLAdapter: {count} NF-e importadas.")
        return count > 0

    def _parse_nfse(self, root, db_session, execucao_id, empresa_id, xml_raw) -> bool:
        """Processa NFS-e ABRASF 2.04 (serviços)."""
        # Encontrar todos os nós Nfse
        nfse_nodes = root.findall('.//Nfse') or [root]

        count = 0
        for nfse in nfse_nodes:
            try:
                inf_nfse = nfse.find('.//InfNfse') or nfse

                numero = _find(inf_nfse, 'Numero', 'NumeroNfse')
                codigo_verif = _find(inf_nfse, 'CodigoVerificacao')
                data_emissao = _parse_date_nfe(
                    _find(inf_nfse, 'DataEmissao', 'DataEmissaoNfse'))

                # Prestador (emitente do serviço)
                prestador = nfse.find('.//PrestadorServico') or nfse.find('.//Prestador')
                emit_cnpj = _find(prestador, './/Cnpj', './/CNPJ') if prestador is not None else None
                emit_nome = _find(prestador, './/RazaoSocial', './/xNome') if prestador is not None else None
                emit_im = _find(prestador, './/InscricaoMunicipal') if prestador is not None else None

                # Município de prestação (determina ISS)
                mun_prest = nfse.find('.//Servico//MunicipioIncidencia') or nfse.find('.//cMunFG')
                mun_ibge = mun_prest.text if mun_prest is not None else None

                # Valores
                valores = nfse.find('.//Servico//Valores') or nfse.find('.//ValoresServico')
                valor_bruto = _decimal(_find(valores, 'ValorServicos', 'vNF')) if valores is not None else Decimal('0')
                valor_iss = _decimal(_find(valores, 'ValorIss', 'ValorISS')) if valores is not None else Decimal('0')
                iss_retido_str = _find(nfse, './/IssRetido', './/ISSRetido')
                iss_retido = iss_retido_str in ('1', 'S', 'true', 'True')
                aliq_iss = _decimal(_find(valores, 'Aliquota', 'AliquotaISS')) if valores is not None else Decimal('0')

                discriminacao = _find(nfse, './/Discriminacao', './/DescricaoServico')
                cod_servico = _find(nfse, './/CodigoTributacaoMunicipio', './/ItemListaServico')

                doc = DocumentoFiscalV2(
                    id=uuid.uuid4(),
                    empresa_id=empresa_id,
                    execucao_id=execucao_id,
                    tipo=TipoDocumentoFiscal.NFSE,
                    natureza_operacao=NaturezaOperacao.SERVICO,
                    status=StatusDocumentoFiscal.PENDENTE,
                    numero=numero,
                    codigo_verificacao=codigo_verif,
                    data_emissao=data_emissao or date.today(),
                    data_entrada=date.today(),
                    emitente_cnpj_cpf=emit_cnpj,
                    emitente_nome=emit_nome,
                    emitente_municipio_ibge=mun_ibge,
                    emitente_inscricao_municipal=emit_im,
                    valor_bruto=valor_bruto,
                    valor_desconto=Decimal('0'),
                    iss_valor=valor_iss,
                    iss_aliquota=aliq_iss / 100 if aliq_iss > 1 else aliq_iss,
                    iss_retido_fonte=iss_retido,
                    iss_municipio_recolhimento=mun_ibge,
                    codigo_servico_lc116=cod_servico,
                    discriminacao_servicos=discriminacao,
                    importado_via="XML_NFSE",
                    xml_original=xml_raw[:65535] if xml_raw else None,
                )
                db_session.add(doc)
                db_session.flush()

                parcela = ParcelaDocumentoFiscal(
                    id=uuid.uuid4(),
                    documento_id=doc.id,
                    numero_parcela='1/1',
                    valor_parcela=valor_bruto,
                    data_vencimento=data_emissao or date.today(),
                    status='A_VENCER',
                )
                db_session.add(parcela)

                staging = StagingRegistro(
                    id=str(uuid.uuid4()),
                    execucao_id=execucao_id,
                    empresa_id=empresa_id,
                    tipo=TipoStaging.DESPESA,
                    data=data_emissao or date.today(),
                    descricao=f"NFS-e {numero} | {emit_nome or 'Prestador de Serviço'}",
                    valor=-float(valor_bruto),
                    entidade_nome=emit_nome,
                    cnpj_cpf=emit_cnpj,
                    processado=False,
                )
                db_session.add(staging)
                count += 1

            except Exception as e:
                logger.error(f"Erro ao processar Nfse: {e}", exc_info=True)
                continue

        db_session.commit()
        logger.info(f"NFeXMLAdapter (NFS-e): {count} notas importadas.")
        return count > 0
