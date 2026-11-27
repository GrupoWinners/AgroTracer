"""Seed opt-in, sintetico e transacional; nunca carrega dados em producao."""

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal
import json
import os
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db.database import criar_engine
from app.models import Base
from app.models.animal import Animal
from app.models.certificado import Certificado
from app.models.fator import Fator
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.lote_animal import LoteAnimal
from app.models.manejo_nutricional import ManejoNutricional
from app.models.parametro_set import ParametroSet
from app.models.produtor import Produtor
from app.models.snapshot_fechamento import SnapshotFechamento
from app.models.talhao import Talhao
from app.schemas.fechamento import FechamentoEntrada
from app.services.certificacao_service import certificar
from app.services.certificado_pdf_service import obter_pdf


def validar_destino(engine):
    if (os.getenv("AGROTRACER_DEMO") != "1"
            or engine.url.get_backend_name() != "postgresql"
            or engine.url.database != "agrotracer_demo"):
        raise ValueError("DEMO_DESTINO_RECUSADO")


def semear(db, usuario):
    if usuario <= 0:
        raise ValueError("DEMO_USUARIO_INVALIDO")
    if db.bind.dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(7101)"))
    lote = db.scalar(select(Lote).where(
        Lote.codigo_lote == "S7-DEMO-CERTIFICADO",
    ))
    if lote:
        cert = db.scalar(select(Certificado).where(
            Certificado.lote_id == lote.id,
            Certificado.wordpress_user_id == usuario,
        ))
        if not cert:
            raise ValueError("DEMO_EXISTENTE_INCONSISTENTE")
        return {"criado": False, "certificado_id": cert.id}
    # Recusa bancos com qualquer dado de dominio; nao apaga nem faz upsert.
    if any(db.execute(select(t).limit(1)).first()
           for t in Base.metadata.sorted_tables):
        raise ValueError("DEMO_BANCO_NAO_VAZIO")
    produtor = Produtor(wordpress_user_id=usuario)
    fazenda = Fazenda(produtor=produtor, nome="Fazenda SYNTHETIC S7",
                      municipio="Demo", uf="MG")
    params = ParametroSet(versao="S7-DEMO-SYNTHETIC-1", status="RASCUNHO",
                          vigencia_inicio=date(2026, 1, 1))
    db.add_all([fazenda, params])
    db.flush()
    db.add(Talhao(fazenda_id=fazenda.id, identificador="DEMO-PASTO",
                  area_hectares=Decimal("10")))
    for chave, valor, unidade in [
        ("FE_BASE_DIETA:PASTAGEM", "2.10", "kg CO2e/cabeca/dia"),
        ("K_IDADE", "1", "1"), ("K_PASTAGEM", "1", "1"),
        ("K_SUPLEMENTACAO", "1", "1"),
    ]:
        db.add(Fator(parametro_set_id=params.id, chave=chave,
                     valor=Decimal(valor), unidade=unidade,
                     source_type="SYNTHETIC"))
    db.flush()  # Fatores somente podem ser inseridos enquanto RASCUNHO.
    params.status = "ATIVO"
    params.aprovado_por = "DEMO-SYNTHETIC"
    params.aprovado_em = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db.flush()
    lotes = []
    for nome in ("S7-DEMO-CERTIFICADO", "S7-DEMO-PARA-EMITIR"):
        lote = Lote(fazenda=fazenda, codigo_lote=nome, status="EM_MANEJO")
        animal = Animal(produtor=produtor, identificador=nome + "-ANIMAL")
        db.add_all([lote, animal])
        db.flush()
        db.add_all([
            LoteAnimal(lote_id=lote.id, animal_id=animal.id,
                       associado_em=datetime(2026, 1, 1, tzinfo=timezone.utc)),
            ManejoNutricional(lote_id=lote.id, parametro_set_id=params.id,
                              inicio=date(2026, 2, 1), fim=date(2026, 2, 1),
                              tipo_dieta="PASTAGEM"),
        ])
        lotes.append(lote)
    db.flush()
    dados = FechamentoEntrada(
        data_abate="2026-02-02", numero_animais_abate=1,
        peso_medio_abate_kg="540", rendimento_carcaca="0.53",
    )
    cert, token = certificar(db, lotes[0], dados, usuario,
                             "S7-DEMO-EMISSAO", str(uuid4()))
    pdf = obter_pdf(db, cert, db.get(SnapshotFechamento, cert.snapshot_id))
    return {"criado": True, "certificado_id": cert.id,
            "lote_para_emitir": lotes[1].id, "token": token,
            "pdf_sha256": pdf.pdf_sha256, "dados_abate": dados.model_dump(
                mode="json")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wp-user-id", type=int, required=True)
    args = parser.parse_args()
    engine = criar_engine()
    try:
        validar_destino(engine)
        with Session(engine) as db, db.begin():
            resultado = semear(db, args.wp_user_id)
        # Consumido pelo bootstrap; nunca publicar esta saida como artifact.
        print(json.dumps(resultado))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
