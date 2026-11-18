"""S5-T01: uma transacao, com commit exclusivamente na rota."""

import hashlib
import json
from decimal import Decimal

from sqlalchemy import select

from app.models.certificado import Certificado
from app.models.snapshot_fechamento import SnapshotFechamento
from app.services.audit_service import registrar_auditoria
from app.services.fechamento_service import (
    ErroFechamento, registrar_fechamento,
)
from app.services.token_service import emitir_token, hash_token


def sha256_json(valor):
    texto = json.dumps(
        valor, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def conteudo_snapshot(snapshot):
    return {
        "schema_version": 1,
        "versao_metodo": snapshot.versao_metodo,
        "versao_parametros": snapshot.versao_parametros,
        "entradas": snapshot.entradas,
        "resultados": snapshot.resultados,
    }


def _entrada_canonica(dados):
    entrada = dados.model_dump(mode="json")
    for campo in ("peso_medio_abate_kg", "rendimento_carcaca"):
        entrada[campo] = format(Decimal(entrada[campo]).normalize(), "f")
    return entrada


def certificar(db, lote, dados, usuario, chave, correlation_id):
    """Chamador deve autorizar e bloquear o lote antes desta chamada."""
    fingerprint = sha256_json({
        "lote_id": lote.id, "dados": _entrada_canonica(dados),
    })
    existente = db.scalar(select(Certificado).where(
        Certificado.wordpress_user_id == usuario,
        Certificado.idempotency_hash == hash_token(chave),
    ))
    if existente is not None:
        codigo = (
            "CERTIFICACAO_JA_PROCESSADA"
            if existente.request_hash == fingerprint
            else "IDEMPOTENCY_KEY_REUTILIZADA"
        )
        raise ErroFechamento(
            409, codigo, "Chave ja utilizada. Consulte o certificado emitido.",
        )
    if db.scalar(select(Certificado.id).where(
        Certificado.lote_id == lote.id, Certificado.status == "VALIDO",
    )) is not None:
        raise ErroFechamento(
            409, "CERTIFICADO_JA_EXISTENTE",
            "Lote ja possui certificado valido.",
        )

    if lote.status != "FECHADO":
        registrar_fechamento(db, lote, dados, usuario, correlation_id)
    snapshot = db.scalar(select(SnapshotFechamento).where(
        SnapshotFechamento.lote_id == lote.id,
    ))
    if snapshot is None:
        raise ErroFechamento(
            409, "SNAPSHOT_AUSENTE", "Lote fechado sem snapshot.",
        )
    # Lotes fechados na Sprint 4 reutilizam os valores imutaveis.
    entrada = _entrada_canonica(dados)
    for campo, valor in entrada.items():
        salvo = snapshot.entradas.get(campo)
        if campo in ("peso_medio_abate_kg", "rendimento_carcaca"):
            salvo = format(Decimal(salvo).normalize(), "f")
        if salvo != valor:
            raise ErroFechamento(
                409, "FECHAMENTO_DIVERGENTE",
                "Dados diferentes do fechamento imutavel.",
            )
    registro, token = emitir_token(db)
    certificado = Certificado(
        lote_id=lote.id, snapshot_id=snapshot.id, token_id=registro.id,
        status="VALIDO", wordpress_user_id=usuario,
        idempotency_hash=hash_token(chave), request_hash=fingerprint,
        snapshot_sha256=sha256_json(conteudo_snapshot(snapshot)),
    )
    db.add(certificado)
    db.flush()
    registrar_auditoria(
        db=db, entidade="certificados", acao="CERTIFICAR_LOTE",
        entidade_id=certificado.id, wordpress_user_id=usuario,
        correlation_id=correlation_id,
        detalhes={"lote_id": lote.id, "snapshot_id": snapshot.id},
    )
    db.flush()
    return certificado, token
