from app.core.hmac_protocol import (
    build_canonical_string,
    gerar_assinatura,
    validar_assinatura,
    validar_timestamp,
    validar_timestamp_header,
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


def test_timestamp_valido():
    agora = 1800000000

    assert validar_timestamp(agora - 120, agora) is True
    assert validar_timestamp(agora + 120, agora) is True


def test_timestamp_limite():
    agora = 1800000000

    assert validar_timestamp(agora - 300, agora) is True
    assert validar_timestamp(agora + 300, agora) is True


def test_timestamp_expirado():
    agora = 1800000000

    assert validar_timestamp(agora - 301, agora) is False


def test_timestamp_futuro():
    agora = 1800000000

    assert validar_timestamp(agora + 301, agora) is False


def test_timestamp_header_valido():
    agora = 1800000000

    assert validar_timestamp_header("1800000000", agora) is True
    assert validar_timestamp_header("1799999700", agora) is True


def test_timestamp_header_invalido():
    agora = 1800000000

    valores_invalidos = [
        None,
        "",
        "abc",
        "-1800000000",
        "1800000000.0",
        " 1800000000",
        "9" * 100,
    ]

    for valor in valores_invalidos:
        assert validar_timestamp_header(valor, agora) is False


def test_vetor_hmac_compartilhado():
    chave = b"agrotracer_chave_exclusivamente_teste_2026"

    canonical = build_canonical_string(
        method="POST",
        path_with_query="/api/v1/fazendas",
        timestamp=1792020000,
        nonce="00112233445566778899aabbccddeeff",
        wp_user_id=42,
        body=b"{}",
    )

    assinatura_esperada = (
        "ca62dbbd01854e311b419ff2e64d3721"
        "e0ccb6bf698ebcf94f9026e5d562c9bc"
    )

    assert gerar_assinatura(
        canonical, chave
    ) == assinatura_esperada

    assert validar_assinatura(
        canonical, chave, assinatura_esperada
    ) is True


def test_canonical_string_com_query():
    resultado = build_canonical_string(
        method="GET",
        path_with_query=(
            "/api/v1/fazendas?"
            "status=ativo&nome=Fazenda+Azul"
        ),
        timestamp=1792020000,
        nonce="00112233445566778899aabbccddeeff",
        wp_user_id=42,
        body=b"",
    )

    caminho_esperado = (
        "/api/v1/fazendas?"
        "nome=Fazenda%20Azul&status=ativo"
    )

    assert resultado.split("\n")[1] == caminho_esperado
