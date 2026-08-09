"""
Testes do MotorFiscal — Cálculos tributários brasileiros para construtoras.

Cenários reais de construção civil:
1. NFS-e empreitada (ISS + INSS + IRRF + CSRF)
2. NF-e material (sem ISS, sem INSS)
3. RPA autônomo (IRRF tabela PF)
4. Serviço simples (ISS + CSRF)
5. Tarifa bancária (nenhuma retenção)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from decimal import Decimal
from app.services.motor_fiscal import MotorFiscal
from app.models.documento_fiscal import NaturezaOperacao, TipoDocumentoFiscal


motor = MotorFiscal()


def test_nfse_empreitada_pj():
    """
    NFS-e de subempreitada PJ: R$ 50.000
    ISS 3%, INSS 11%, IRRF 1,5%, CSRF 4,65%
    """
    r = motor.calcular(
        valor_bruto=Decimal('50000.00'),
        natureza=NaturezaOperacao.EMPREITADA,
        tipo_doc=TipoDocumentoFiscal.NFSE,
        emitente_pj=True,
        emitente_simples=False,
        aliquota_iss_municipio=Decimal('0.03'),
        retencao_iss_obrigatoria=True,
    )
    assert r.iss_retido is True,   f"ISS deveria ser retido: {r.iss_valor}"
    assert r.inss_retido is True,  f"INSS deveria ser retido: {r.inss_valor}"
    assert r.ir_retido is True,    f"IRRF deveria ser retido: {r.ir_valor}"
    assert r.csrf_retido is True,  f"CSRF deveria ser retido"

    assert r.iss_valor   == Decimal('1500.00'), f"ISS incorreto: {r.iss_valor}"
    assert r.inss_valor  == Decimal('5500.00'), f"INSS incorreto: {r.inss_valor}"
    assert r.ir_valor    == Decimal('750.00'),  f"IRRF incorreto: {r.ir_valor}"

    csrf_esperado = Decimal('325.00') + Decimal('1500.00') + Decimal('500.00')  # PIS+COFINS+CSLL
    assert (r.pis_valor + r.cofins_valor + r.csll_valor) == csrf_esperado, \
        f"CSRF incorreto: {r.pis_valor+r.cofins_valor+r.csll_valor}"

    liquido_esperado = Decimal('50000.00') - r.total_retencoes
    assert abs(r.valor_liquido_pagar - liquido_esperado) <= Decimal('0.01'), \
        f"Valor líquido incorreto: {r.valor_liquido_pagar}"

    print(f"✅ NFS-e empreitada PJ: R$ {r.valor_liquido_pagar:.2f} líquido")
    print(f"   ISS: R$ {r.iss_valor:.2f} | INSS: R$ {r.inss_valor:.2f} | IRRF: R$ {r.ir_valor:.2f} | CSRF: R$ {r.pis_valor+r.cofins_valor+r.csll_valor:.2f}")
    print(f"   Total retenções: R$ {r.total_retencoes:.2f}")
    for j in r.justificativas:
        print(f"   📌 {j}")


def test_nfe_material():
    """NF-e compra de material: nenhuma retenção (apenas IPI/ICMS no documento, não retidos)"""
    r = motor.calcular(
        valor_bruto=Decimal('132500.00'),
        natureza=NaturezaOperacao.MATERIAL,
        tipo_doc=TipoDocumentoFiscal.NFE,
        emitente_pj=True,
    )
    assert r.iss_retido is False,  "Material não tem ISS"
    assert r.inss_retido is False, "Material não tem INSS"
    assert r.ir_retido is False,   "Material não tem IRRF"
    assert r.csrf_retido is False, "Material não tem CSRF"
    assert r.valor_liquido_pagar == Decimal('132500.00'), "Nenhuma retenção esperada"
    print(f"✅ NF-e material: R$ {r.valor_liquido_pagar:.2f} (sem retenções)")


def test_rpa_pf():
    """RPA pessoa física: apenas IRRF se acima do mínimo"""
    r = motor.calcular(
        valor_bruto=Decimal('5000.00'),
        natureza=NaturezaOperacao.EMPREITADA,
        tipo_doc=TipoDocumentoFiscal.RPA,
        emitente_pj=False,  # PF
        aliquota_iss_municipio=Decimal('0.03'),
        retencao_iss_obrigatoria=True,
    )
    # PF não tem CSRF
    assert r.csrf_retido is False, "PF não tem CSRF"
    # INSS aplicável (empreitada de PF)
    assert r.inss_retido is True, "PF com empreitada tem INSS"
    # IRRF: R$ 5.000 acima do mínimo
    assert r.ir_retido is True, "PF acima do mínimo tem IRRF"
    print(f"✅ RPA PF: R$ {r.valor_liquido_pagar:.2f} líquido | INSS: {r.inss_valor:.2f} | IRRF: {r.ir_valor:.2f}")


def test_tarifa_bancaria():
    """Tarifa bancária: nenhuma retenção"""
    r = motor.calcular(
        valor_bruto=Decimal('150.00'),
        natureza=NaturezaOperacao.FINANCEIRO,
        tipo_doc=TipoDocumentoFiscal.BOLETO,
        emitente_pj=True,
    )
    assert r.total_retencoes == Decimal('0.00'), f"Tarifas não têm retenção: {r.total_retencoes}"
    print(f"✅ Tarifa bancária: R$ {r.valor_liquido_pagar:.2f} (sem retenções)")


def test_csrf_abaixo_minimo():
    """Serviço PJ abaixo do mínimo da CSRF (R$ 215,05): não retém CSRF"""
    r = motor.calcular(
        valor_bruto=Decimal('200.00'),
        natureza=NaturezaOperacao.SERVICO,
        tipo_doc=TipoDocumentoFiscal.NFSE,
        emitente_pj=True,
    )
    assert r.csrf_retido is False, f"CSRF não deve ser retido abaixo de R$215,05: {r.cofins_valor}"
    print(f"✅ Serviço PJ R$200 (abaixo mínimo CSRF): ISS retido={r.iss_retido}, CSRF retido={r.csrf_retido}")


if __name__ == '__main__':
    print("\n===== TESTES DO MOTOR FISCAL BRASILEIRO =====\n")
    test_nfse_empreitada_pj()
    print()
    test_nfe_material()
    print()
    test_rpa_pf()
    print()
    test_tarifa_bancaria()
    print()
    test_csrf_abaixo_minimo()
    print("\n===== TODOS OS TESTES PASSARAM ✅ =====\n")
