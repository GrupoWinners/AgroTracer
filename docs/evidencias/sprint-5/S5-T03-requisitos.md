# AG-98 / S5-T03 — tokens publicos

Fonte: https://losel.atlassian.net/browse/AG-98 (consultada em 2026-11-18).
Responsavel: Samela. Status consultado: Fazendo.

Escopo: token opaco >=128 bits (256 recomendado); persistir somente
token_hash para lookup; limitar consultas publicas. Aceite: unico, nao
sequencial, rate limit, resposta generica para inexistente (RN-13).
Depende de S4-T06; bloqueia S5-T01 e S5-T05.

Implementacao: secrets.token_urlsafe(32), SHA-256 e unicidade no banco.
Servico consultar_token para integracao pela S5-T05, que implementara
a pagina publica e DTO. Nao expor o objeto ORM retornado pelo servico.
Limite operacional escolhido: 30 consultas/minuto por IP de conexao,
compartilhado no Redis com incremento/expiracao atomicos. Inclui entradas
malformadas. Redis indisponivel retorna 503, nunca desativa o limite.
Usar IP real somente com configuracao explicita de proxies confiaveis.

O token original e retornado uma unica vez; nao registrar em logs,
auditoria, banco, URLs de telemetria nem cache de idempotencia.
A S5-T01 usara 409 controlado para repeticoes para nao armazenar o token.
CI ampliado para bases feature/S5-* dos PRs encadeados.

DoD do Jira: testes/evidencias, erros definidos, docs/OpenAPI/ADR conforme
necessario, review de outro integrante, QA Gate conforme risco e nenhum
P1/P2 relacionado aberto. Review e QA humanos permanecem pendentes.
