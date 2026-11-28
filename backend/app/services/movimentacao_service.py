from datetime import timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.fazenda import Fazenda
from app.models.lote import Lote
from app.models.movimentacao import Movimentacao
from app.models.produtor import Produtor
from app.models.talhao import Talhao
from app.schemas.movimentacao import MovimentacaoCreate
from app.services.audit_service import registrar_auditoria


class ErroMovimentacao(Exception):
    def __init__(self, status_code, codigo, mensagem):
        self.status_code = status_code
        self.codigo = codigo
        self.mensagem = mensagem
        super().__init__(mensagem)


def criar_movimentacao(
    db: Session,
    dados: MovimentacaoCreate,
    wp_user_id: int,
    correlation_id: str | None = None,
) -> Movimentacao:
    # RN-07: exatamente um alvo.
    if (dados.animal_id is None) == (dados.lote_id is None):
        raise ErroMovimentacao(
            422,
            "MOVIMENTACAO_ALVO_INVALIDO",
            "Informe exatamente um animal ou lote.",
        )

    fazenda_do_lote = None

    if dados.animal_id is not None:
        # RN-19: autoriza e bloqueia o animal para serializar
        # movimentacoes concorrentes do mesmo alvo.
        alvo = db.scalar(
            select(Animal)
            .join(Produtor, Animal.produtor_id == Produtor.id)
            .where(
                Animal.id == dados.animal_id,
                Produtor.wordpress_user_id == wp_user_id,
            )
            .with_for_update(of=Animal)
        )

        if alvo is None:
            raise ErroMovimentacao(
                404,
                "ANIMAL_NAO_ENCONTRADO",
                "Animal nao encontrado ou nao autorizado.",
            )

        filtro_historico = (
            Movimentacao.animal_id == dados.animal_id
        )

    else:
        alvo = db.scalar(
            select(Lote)
            .join(Fazenda, Lote.fazenda_id == Fazenda.id)
            .join(Produtor, Fazenda.produtor_id == Produtor.id)
            .where(
                Lote.id == dados.lote_id,
                Produtor.wordpress_user_id == wp_user_id,
            )
            .with_for_update(of=Lote)
        )

        if alvo is None:
            raise ErroMovimentacao(
                404,
                "LOTE_NAO_ENCONTRADO",
                "Lote nao encontrado ou nao autorizado.",
            )

        fazenda_do_lote = alvo.fazenda_id
        filtro_historico = (
            Movimentacao.lote_id == dados.lote_id
        )

    # RN-19: valida tambem os talhoes informados.
    ids_talhoes = {
        valor
        for valor in (
            dados.origem_talhao_id,
            dados.destino_talhao_id,
        )
        if valor is not None
    }

    if (
        dados.origem_talhao_id is not None
        and dados.origem_talhao_id == dados.destino_talhao_id
    ):
        raise ErroMovimentacao(
            422,
            "MOVIMENTACAO_ORIGEM_DESTINO_IGUAIS",
            "Origem e destino nao podem ser iguais.",
        )

    for talhao_id in ids_talhoes:
        consulta = (
            select(Talhao)
            .join(Fazenda, Talhao.fazenda_id == Fazenda.id)
            .join(Produtor, Fazenda.produtor_id == Produtor.id)
            .where(
                Talhao.id == talhao_id,
                Produtor.wordpress_user_id == wp_user_id,
            )
        )

        # Movimentacao de lote usa talhoes da propria fazenda.
        if fazenda_do_lote is not None:
            consulta = consulta.where(
                Talhao.fazenda_id == fazenda_do_lote
            )

        if db.scalar(consulta) is None:
            raise ErroMovimentacao(
                404,
                "TALHAO_NAO_ENCONTRADO",
                "Talhao nao encontrado ou nao autorizado.",
            )

    # RN-07: a sequencia e avaliada por alvo.
    data_nova = dados.data_hora.astimezone(timezone.utc)

    ultima_data = db.scalar(
        select(func.max(Movimentacao.data_hora))
        .where(filtro_historico)
    )

    if ultima_data is not None:
        # SQLite dos testes pode devolver datetime sem timezone.
        if ultima_data.tzinfo is None:
            ultima_data = ultima_data.replace(
                tzinfo=timezone.utc
            )

        if data_nova <= ultima_data:
            raise ErroMovimentacao(
                409,
                "MOVIMENTACAO_FORA_DE_ORDEM",
                "A data/hora deve ser posterior "
                "a ultima movimentacao do alvo.",
            )

    movimentacao = Movimentacao(
        animal_id=dados.animal_id,
        lote_id=dados.lote_id,
        origem_talhao_id=dados.origem_talhao_id,
        destino_talhao_id=dados.destino_talhao_id,
        tipo=dados.tipo,
        data_hora=data_nova,
        observacao=dados.observacao,
    )

    db.add(movimentacao)
    db.flush()

    registrar_auditoria(
        db=db,
        entidade="movimentacoes",
        acao="CRIAR_MOVIMENTACAO",
        entidade_id=movimentacao.id,
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={
            "animal_id": dados.animal_id,
            "lote_id": dados.lote_id,
            "tipo": dados.tipo,
            "data_hora": data_nova.isoformat(),
        },
        commit=False,
    )

    return movimentacao
