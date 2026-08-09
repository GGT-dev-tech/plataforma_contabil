"""
API de Documentos Fiscais — CRUD e Processamento

Endpoints para gestão do ciclo de vida de um documento fiscal:
1. Consultar documentos importados
2. Vincular a uma Obra (centro de custo)
3. Calcular retenções fiscais (MotorFiscal)
4. Gerar lançamentos contábeis (GeradorLancamentos)
5. Aprovar documento para pagamento
"""
import uuid
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
from app.contexts.identity.auth_utils import get_current_user
from app.models.domain import Usuario, Role
from app.models.documento_fiscal import (
    DocumentoFiscalV2,
    ParcelaDocumentoFiscal,
    TipoDocumentoFiscal,
    NaturezaOperacao,
    StatusDocumentoFiscal,
)
from app.models.financeiro import TituloFinanceiro, TipoTitulo, StatusTitulo
from app.services.motor_fiscal import MotorFiscal
from app.services.gerador_lancamentos import GeradorLancamentos

router = APIRouter(prefix="/documentos-fiscais", tags=["documentos-fiscais"])
motor_fiscal = MotorFiscal()


def _doc_to_dict(doc: DocumentoFiscalV2) -> dict:
    return {
        "id": str(doc.id),
        "empresa_id": str(doc.empresa_id) if doc.empresa_id else None,
        "obra_id": str(doc.obra_id) if doc.obra_id else None,
        "tipo": doc.tipo.value,
        "natureza_operacao": doc.natureza_operacao.value,
        "status": doc.status.value,
        "numero": doc.numero,
        "serie": doc.serie,
        "chave_acesso": doc.chave_acesso,
        "data_emissao": doc.data_emissao.isoformat() if doc.data_emissao else None,
        "data_entrada": doc.data_entrada.isoformat() if doc.data_entrada else None,
        "emitente_cnpj_cpf": doc.emitente_cnpj_cpf,
        "emitente_nome": doc.emitente_nome,
        "emitente_municipio_nome": doc.emitente_municipio_nome,
        "valor_bruto": float(doc.valor_bruto),
        "valor_desconto": float(doc.valor_desconto or 0),
        "iss_valor": float(doc.iss_valor or 0),
        "iss_retido": doc.iss_retido_fonte,
        "inss_valor": float(doc.inss_valor or 0),
        "inss_retido": doc.inss_retido,
        "ir_valor": float(doc.ir_valor or 0),
        "ir_retido": doc.ir_retido,
        "pis_valor": float(doc.pis_valor or 0),
        "cofins_valor": float(doc.cofins_valor or 0),
        "csll_valor": float(doc.csll_valor or 0),
        "total_retencoes": float(doc.total_retencoes or 0),
        "valor_liquido_pagar": float(doc.valor_liquido_pagar or doc.valor_bruto),
        "importado_via": doc.importado_via,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
    }


@router.get("", response_model=List[dict])
def list_documentos(
    empresa_id: Optional[str] = Query(None),
    obra_id: Optional[str] = Query(None),
    execucao_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(DocumentoFiscalV2)

    if current_user.role == Role.ADMIN:
        if empresa_id:
            query = query.filter(DocumentoFiscalV2.empresa_id == empresa_id)
    else:
        query = query.filter(DocumentoFiscalV2.empresa_id == current_user.empresa_id)

    if obra_id:
        query = query.filter(DocumentoFiscalV2.obra_id == obra_id)
    if execucao_id:
        query = query.filter(DocumentoFiscalV2.execucao_id == execucao_id)
    if status:
        query = query.filter(DocumentoFiscalV2.status == status)

    docs = query.order_by(DocumentoFiscalV2.data_emissao.desc()).limit(limit).all()
    return [_doc_to_dict(d) for d in docs]


@router.get("/{doc_id}", response_model=dict)
def get_documento(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    doc = db.query(DocumentoFiscalV2).filter(DocumentoFiscalV2.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(doc.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)
    return _doc_to_dict(doc)


class VincularObraPayload(BaseModel):
    obra_id: str


@router.patch("/{doc_id}/vincular-obra", response_model=dict)
def vincular_obra(
    doc_id: str,
    payload: VincularObraPayload,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Vincula um documento fiscal a uma obra (centro de custo)."""
    doc = db.query(DocumentoFiscalV2).filter(DocumentoFiscalV2.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(doc.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)

    doc.obra_id = payload.obra_id
    db.commit()
    db.refresh(doc)
    return _doc_to_dict(doc)


class CalcularRetencoesPayload(BaseModel):
    emitente_pj: bool = True
    emitente_simples: bool = False
    aliquota_iss: Optional[float] = None
    retencao_iss_obrigatoria: bool = True


@router.post("/{doc_id}/calcular-retencoes", response_model=dict)
def calcular_retencoes(
    doc_id: str,
    payload: CalcularRetencoesPayload,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Calcula e persiste as retenções fiscais do documento.
    Usa o MotorFiscal com legislação brasileira vigente.
    """
    doc = db.query(DocumentoFiscalV2).filter(DocumentoFiscalV2.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(doc.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)

    aliq_iss = Decimal(str(payload.aliquota_iss)) if payload.aliquota_iss else None

    resultado = motor_fiscal.calcular(
        valor_bruto=Decimal(str(doc.valor_bruto)),
        natureza=doc.natureza_operacao,
        tipo_doc=doc.tipo,
        emitente_pj=payload.emitente_pj,
        emitente_simples=payload.emitente_simples,
        aliquota_iss_municipio=aliq_iss,
        retencao_iss_obrigatoria=payload.retencao_iss_obrigatoria,
        valor_desconto=Decimal(str(doc.valor_desconto or 0)),
    )

    # Persistir resultado no documento
    doc.iss_valor = resultado.iss_valor
    doc.iss_aliquota = resultado.iss_aliquota
    doc.iss_retido_fonte = resultado.iss_retido
    doc.inss_valor = resultado.inss_valor
    doc.inss_aliquota = resultado.inss_aliquota
    doc.inss_retido = resultado.inss_retido
    doc.ir_valor = resultado.ir_valor
    doc.ir_aliquota = resultado.ir_aliquota
    doc.ir_retido = resultado.ir_retido
    doc.ir_codigo_darf = resultado.ir_codigo_darf
    doc.pis_valor = resultado.pis_valor
    doc.cofins_valor = resultado.cofins_valor
    doc.csll_valor = resultado.csll_valor
    doc.csrf_retido = resultado.csrf_retido
    doc.total_retencoes = resultado.total_retencoes
    doc.valor_liquido_pagar = resultado.valor_liquido_pagar

    db.commit()
    db.refresh(doc)
    
    # Auto-gerar Título a Pagar
    titulo_existente = db.query(TituloFinanceiro).filter(TituloFinanceiro.documento_fiscal_id == doc.id).first()
    if not titulo_existente:
        import datetime
        data_vencimento = doc.data_emissao + datetime.timedelta(days=30) if doc.data_emissao else datetime.date.today()
        
        titulo = TituloFinanceiro(
            id=str(uuid.uuid4()),
            empresa_id=doc.empresa_id,
            obra_id=doc.obra_id,
            documento_fiscal_id=doc.id,
            tipo=TipoTitulo.PAGAR,
            status=StatusTitulo.ABERTO,
            descricao=f"NF {doc.numero or 'S/N'} - {doc.emitente_nome or 'Desconhecido'}",
            fornecedor_cliente_nome=doc.emitente_nome,
            fornecedor_cliente_cnpj_cpf=doc.emitente_cnpj_cpf,
            valor_nominal=float(resultado.valor_liquido_pagar),
            data_emissao=doc.data_emissao or datetime.date.today(),
            data_vencimento=data_vencimento,
            gerado_automaticamente=True
        )
        db.add(titulo)
        db.commit()

    return {
        **_doc_to_dict(doc),
        "justificativas": resultado.justificativas
    }


@router.post("/{doc_id}/gerar-lancamentos", response_model=dict)
def gerar_lancamentos(
    doc_id: str,
    conta_bancaria: Optional[str] = Query(None, description="Código contábil da conta bancária a creditar"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera lançamentos contábeis em partida dobrada para o documento fiscal.
    Os lançamentos ficam em status RASCUNHO até aprovação do contador.
    """
    if current_user.role not in [Role.ADMIN, Role.ANALISTA]:
        raise HTTPException(status_code=403)

    doc = db.query(DocumentoFiscalV2).filter(DocumentoFiscalV2.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if current_user.role != Role.ADMIN and str(doc.empresa_id) != str(current_user.empresa_id):
        raise HTTPException(status_code=403)

    gerador = GeradorLancamentos(db)
    try:
        lancamentos = gerador.gerar_para_documento(
            documento=doc,
            conta_bancaria_codigo=conta_bancaria,
        )
        for l in lancamentos:
            db.add(l)
        db.commit()

        return {
            "mensagem": f"{len(lancamentos)} lançamentos gerados com sucesso",
            "lote": lancamentos[0].numero_lote if lancamentos else None,
            "lancamentos": [
                {
                    "partida": l.partida.value,
                    "conta": l.conta_contabil_codigo,
                    "descricao_conta": l.conta_contabil_descricao,
                    "valor": float(l.valor),
                    "historico": l.historico,
                }
                for l in lancamentos
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
