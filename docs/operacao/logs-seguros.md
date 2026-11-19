# Logs sem PII/segredos

Iniciar o backend em `backend/` com `python -m app.run`. O JSON registra
somente evento, nivel, template da rota, status, duracao e correlation_id.
Diagnosticos arbitrarios sao substituidos por diagnostic_redacted.
Nao habilitar echo SQL, debug com locals ou captura de corpos/headers em APM.

O proxy e o WordPress tambem precisam evitar access logs completos:
o token publico fica na query string. Em Nginx usar, por exemplo,
`log_format agrotracer_safe '$status $request_time';` e associar esse
formato ao access_log do virtual host. Nao incluir request, args, URI,
Referer, Cookie, Authorization, IP ou User-Agent.

No Apache pode-se usar `LogFormat "%>s %D" agrotracer_safe` e esse formato
no CustomLog. Desabilitar WP_DEBUG/WP_DEBUG_LOG no ambiente publicado.
Erros de proxy/PHP precisam de coletor que descarte mensagens brutas e
preserve somente codigo/nivel; nao basta mascarar a palavra password.
Aplicar essa configuracao ao servidor real e validar com uma requisicao
sintetica antes de declarar a homologacao de infraestrutura concluida.

O launcher nao confia automaticamente em X-Forwarded-For. Para consulta
publica atras de proxy, configurar somente CIDRs efetivamente confiaveis
em AGROTRACER_TRUSTED_PROXIES; o resolvedor existente percorre a cadeia
da direita para a esquerda. Nunca usar 0.0.0.0/0 como atalho.

Auditoria de negocio no banco e diferente do log operacional. Continua
restrita ao banco autorizado; suas retencao/permissoes devem ser tratadas
pela equipe. Nenhum dump ou segredo deve ser anexado ao PR/CI.
