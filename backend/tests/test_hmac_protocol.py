from app.core.hmac_protocol import (
    build_canonical_string,
    gerar_assinatura,
    validar_assinatura,
)


def test_canonical_string():
    resultado = build_canonical_string(
        method="post",
        path_with_query="/api/v1/fazendas",
        timestamp=1792020000,
        nonce="00112233445566778899aabbccddeeff",
        wp_user_id=42,
        body=b"{}",
    )

    esperado = (
        "POST\n"
        "/api/v1/fazendas\n"
        "1792020000\n"
        "00112233445566778899aabbccddeeff\n"
        "42\n"
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
    )

    assert resultado == esperado


def test_assinatura_valida():
    chave = b"chave_ficticia_apenas_para_testes"

    canonical = "POST\n/api/v1/fazendas\n123456"

    assinatura = gerar_assinatura(canonical, chave)

    assert validar_assinatura(
        canonical,
        chave,
        assinatura,
    ) is True


def test_assinatura_invalida():
    chave = b"chave_ficticia_apenas_para_testes"

    canonical = "POST\n/api/v1/fazendas\n123456"

    assinatura = gerar_assinatura(canonical, chave)

    canonical_alterada = "POST\n/api/v1/fazendas\n999999"

    assert validar_assinatura(
        canonical_alterada,
        chave,
        assinatura,
    ) is False
