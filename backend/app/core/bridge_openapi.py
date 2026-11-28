"""Headers obrigatórios do contrato HMAC, sem valores secretos."""

BRIDGE_OPENAPI = {
    "parameters": [
        {
            "name": nome, "in": "header", "required": True,
            "schema": {"type": "string"}, "description": descricao,
        }
        for nome, descricao in [
            ("X-AgroTracer-Signature", "HMAC-SHA256 hexadecimal minúsculo"),
            ("X-AgroTracer-Timestamp", "Unix timestamp; tolerância de 300s"),
            ("X-AgroTracer-Nonce", "32 caracteres hexadecimais; uso único"),
            ("X-AgroTracer-User-Id", "Identidade WordPress assinada"),
            ("X-Correlation-ID", "UUID v4 propagado na resposta e auditoria"),
        ]
    ],
}
