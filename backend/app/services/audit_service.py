from sqlalchemy.orm import Session

from app.models.auditoria_evento import AuditoriaEvento


def registrar_auditoria(
    db: Session,
    entidade: str,
    acao: str,
    entidade_id: int | None = None,
    wordpress_user_id: int | None = None,
    correlation_id: str | None = None,
    detalhes: dict | None = None,
) -> AuditoriaEvento:
    evento = AuditoriaEvento(
        entidade=entidade,
        acao=acao,
        entidade_id=entidade_id,
        wordpress_user_id=wordpress_user_id,
        correlation_id=correlation_id,
        detalhes=detalhes,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento
