import hashlib
import hmac


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
        path_with_query,
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
