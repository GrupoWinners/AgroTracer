from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.bridge_dependency import exigir_usuario_wordpress
from app.db.database import obter_db
from app.models.fazenda import Fazenda
from app.models.produtor import Produtor
from app.models.talhao import Talhao
from app.schemas.fazenda import FazendaCreate, FazendaResponse, FazendaUpdate
from app.schemas.talhao import TalhaoCreate, TalhaoResponse
from app.services.audit_service import registrar_auditoria

router = APIRouter(prefix="/fazendas", tags=["Fazendas"])


def _obter_ou_criar_produtor(db: Session, wp_user_id: int) -> Produtor:
    query = select(Produtor).where(Produtor.wordpress_user_id == wp_user_id)
    produtor = db.execute(query).scalar_one_or_none()

    if not produtor:
        produtor = Produtor(wordpress_user_id=wp_user_id)
        db.add(produtor)
        db.commit()
        db.refresh(produtor)

    return produtor


def _obter_fazenda_autorizada(
    fazenda_id: int,
    produtor_id: int,
    db: Session,
) -> Fazenda:
    query = select(Fazenda).where(
        Fazenda.id == fazenda_id,
        Fazenda.produtor_id == produtor_id,
    )
    fazenda = db.execute(query).scalar_one_or_none()

    if not fazenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fazenda não encontrada ou acesso não autorizado.",
        )

    return fazenda


@router.get("", response_model=list[FazendaResponse])
def listar_fazendas(
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)
    query = (
        select(Fazenda)
        .where(Fazenda.produtor_id == produtor.id)
        .order_by(Fazenda.id)
    )
    fazendas = db.execute(query).scalars().all()
    return fazendas


@router.post(
    "",
    response_model=FazendaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_fazenda(
    dados: FazendaCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)

    # RN-02: deduplicação declarada de CAR quando informado
    if dados.numero_car_informado:
        query_car = select(Fazenda).where(
            Fazenda.numero_car_informado == dados.numero_car_informado
        )
        if db.execute(query_car).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este CAR já está cadastrado em outra fazenda.",
            )

    fazenda = Fazenda(
        produtor_id=produtor.id,
        nome=dados.nome,
        municipio=dados.municipio,
        uf=dados.uf.upper(),
        numero_car_informado=dados.numero_car_informado,
    )
    db.add(fazenda)
    db.flush()

    correlation_id = getattr(request.state, "correlation_id", None)
    registrar_auditoria(
        db=db,
        entidade="fazendas",
        acao="CRIAR_FAZENDA",
        entidade_id=fazenda.id,
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={"nome": fazenda.nome, "municipio": fazenda.municipio},
        commit=False,
    )

    db.commit()
    db.refresh(fazenda)

    return fazenda


@router.get("/{fazenda_id}", response_model=FazendaResponse)
def detalhar_fazenda(
    fazenda_id: int,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)
    return _obter_fazenda_autorizada(fazenda_id, produtor.id, db)


@router.put("/{fazenda_id}", response_model=FazendaResponse)
def editar_fazenda(
    fazenda_id: int,
    dados: FazendaUpdate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)
    fazenda = _obter_fazenda_autorizada(fazenda_id, produtor.id, db)

    if (
        dados.numero_car_informado
        and dados.numero_car_informado != fazenda.numero_car_informado
    ):
        query_car = select(Fazenda).where(
            Fazenda.numero_car_informado == dados.numero_car_informado,
            Fazenda.id != fazenda_id,
        )
        if db.execute(query_car).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este CAR já está cadastrado em outra fazenda.",
            )

    if dados.nome is not None:
        fazenda.nome = dados.nome
    if dados.municipio is not None:
        fazenda.municipio = dados.municipio
    if dados.uf is not None:
        fazenda.uf = dados.uf.upper()
    if dados.numero_car_informado is not None:
        fazenda.numero_car_informado = dados.numero_car_informado

    db.flush()

    correlation_id = getattr(request.state, "correlation_id", None)
    registrar_auditoria(
        db=db,
        entidade="fazendas",
        acao="EDITAR_FAZENDA",
        entidade_id=fazenda.id,
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={"nome": fazenda.nome},
        commit=False,
    )

    db.commit()
    db.refresh(fazenda)

    return fazenda


@router.get("/{fazenda_id}/talhoes", response_model=list[TalhaoResponse])
def listar_talhoes_fazenda(
    fazenda_id: int,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)
    fazenda = _obter_fazenda_autorizada(fazenda_id, produtor.id, db)

    query = (
        select(Talhao)
        .where(Talhao.fazenda_id == fazenda.id)
        .order_by(Talhao.id)
    )
    talhoes = db.execute(query).scalars().all()
    return talhoes


@router.post(
    "/{fazenda_id}/talhoes",
    response_model=TalhaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_talhao(
    fazenda_id: int,
    dados: TalhaoCreate,
    request: Request,
    wp_user_id: int = Depends(exigir_usuario_wordpress),
    db: Session = Depends(obter_db),
):
    produtor = _obter_ou_criar_produtor(db, wp_user_id)
    fazenda = _obter_fazenda_autorizada(fazenda_id, produtor.id, db)

    query_duplicado = select(Talhao).where(
        Talhao.fazenda_id == fazenda.id,
        Talhao.identificador == dados.identificador,
    )
    if db.execute(query_duplicado).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Talhão com identificador '{dados.identificador}' "
                f"já cadastrado nesta fazenda."
            ),
        )

    talhao = Talhao(
        fazenda_id=fazenda.id,
        identificador=dados.identificador,
        area_hectares=dados.area_hectares,
    )
    db.add(talhao)
    db.flush()

    correlation_id = getattr(request.state, "correlation_id", None)
    registrar_auditoria(
        db=db,
        entidade="talhoes",
        acao="CRIAR_TALHAO",
        entidade_id=talhao.id,
        wordpress_user_id=wp_user_id,
        correlation_id=correlation_id,
        detalhes={
            "fazenda_id": fazenda.id,
            "identificador": talhao.identificador,
        },
        commit=False,
    )

    db.commit()
    db.refresh(talhao)

    return talhao
