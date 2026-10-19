import hashlib
import hmac
import time
from urllib.parse import parse_qsl, quote, urlencode, urlsplit


def build_canonical_string(
    method: str,
    path_with_query: str,
    timestamp: int,
    nonce: str,
    wp_user_id: int,
    body: bytes,
) -> str:

    body_hash = hashlib.sha256(body).hexdigest()

    campos = [
        method.upper(),
        normalizar_path_query(path_with_query),
        str(timestamp),
        nonce,
        str(wp_user_id),
        body_hash,
    ]

    return "\n".join(campos)


def gerar_assinatura(canonical_string: str, chave: bytes) -> str:
    assinatura = hmac.new(
        chave,
        canonical_string.encode("utf-8"),
        hashlib.sha256,
    )

    return assinatura.hexdigest()


def validar_assinatura(
    canonical_string: str,
    chave: bytes,
    assinatura_recebida: str,
) -> bool:

    assinatura_esperada = gerar_assinatura(
        canonical_string,
        chave,
    )

    return hmac.compare_digest(
        assinatura_esperada,
        assinatura_recebida,
    )


def validar_timestamp(
    timestamp: int,
    agora: int | None = None,
) -> bool:
    if type(timestamp) is not int:
        return False

    if agora is None:
        agora = int(time.time())

    diferenca = abs(agora - timestamp)

    return diferenca <= 300


def validar_timestamp_header(
    valor: str | None,
    agora: int | None = None,
) -> bool:
    if valor is None:
        return False

    if not valor.isascii() or not valor.isdecimal():
        return False

    if len(valor) > 20:
        return False

    timestamp = int(valor)

    return validar_timestamp(timestamp, agora)


def normalizar_path_query(path_with_query: str) -> str:
    partes = urlsplit(path_with_query)

    if partes.scheme or partes.netloc:
        raise ValueError("A URL deve conter apenas path e query.")

    if not partes.path.startswith("/"):
        raise ValueError("O path deve começar com '/'.")

    if "#" in path_with_query:
        raise ValueError("Fragmentos não são permitidos.")

    parametros = parse_qsl(
        partes.query,
        keep_blank_values=True,
        errors="strict",
    )

    parametros.sort(key=lambda item: item[0])

    if not parametros:
        return partes.path

    query = urlencode(
        parametros,
        quote_via=quote,
        safe="",
    )

    return f"{partes.path}?{query}"
