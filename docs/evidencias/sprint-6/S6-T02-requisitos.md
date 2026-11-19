# AG-103 / S6-T02 — hardening

Fonte: https://losel.atlassian.net/browse/AG-103, lida em 2026-11-19.
Responsavel Samela; Fazendo; 8 pontos; entrega 25/11.
Escopo: HMAC final, autorizacao por objeto em todas as rotas com ID,
rate limits e redaction de PII/segredos em logs.
Aceite: SEC-01..SEC-08 passam; sem segredo ou PII em log.
Depende de S5-T06; bloqueia S6-T03, S6-T05 e S6-T06.
DoD: codigo sem segredo, testes/evidencias, erros e docs/OpenAPI/ADR,
review de outro integrante, QA Gate conforme risco, nenhum P1/P2 aberto.

Base verificada: develop ca4a86d, incluindo S5-T06 e S6-T01.
Implementacao: headers HMAC duplicados rejeitados; ID limitado a BIGINT;
limite privado de 120/min por usuario autenticado em Redis atomico,
sem afetar o limite publico de 30/min. Os valores sao decisoes operacionais,
nao numeros prescritos no Jira. Redis falha fechado com 503; excesso 429.
Nonce continua registrado antes da operacao; retry requer novo nonce HMAC.

Logs por allowlist preservam evento, nivel, template de rota, status,
duracao e correlation_id UUID. Mensagens/argumentos/tracebacks arbitrarios,
headers, corpo, IP, query e IDs concretos nao sao serializados. SQLAlchemy
oculta parametros. Entrada suportada: `python -m app.run` (startup incluso,
access log bruto desativado, proxy headers automaticos desativados).
O lifespan tambem instala formatadores seguros nos handlers existentes.
Nao adicionar handlers/formatadores externos que reintroduzam dados brutos.

## Matriz e limites da evidencia

| Cenario | Fonte e prova |
| --- | --- |
| SEC-01 assinatura adulterada | test_s1_t05_crud_seguranca |
| SEC-02 timestamp fora da janela | test_s1_t05_crud_seguranca |
| SEC-03 replay de nonce | test_s1_t05_crud_seguranca |
| SEC-04 usuario adulterado sem reassinar | test_s3_t03_api::test_hmac_real_nas_rotas |
| SEC-05 lote de outro produtor | test_s6_t02_hardening::test_bola_todas_rotas_id e test_s5_t06_qa_gate |
| SEC-06 tokens inexistentes repetidos | test_s6_t02_hardening::test_sec06_tokens_inexistentes_genericos_ate_bloqueio; test_s5_t05_publico; contador Redis real em test_s6_t02_redis |
| SEC-07 leak do DTO | test_s5_t06_qa_gate |
| SEC-08 clique duplo | test_s5_t06_qa_gate e test_s5_concorrencia |
| Cobertura adicional | test_s6_t02_hardening: BOLA em rotas com ID, admin, limite e logs; test_s6_t02_redis: contador/expiracao em Redis real |

As verificacoes por ID incluem fazenda/talhoes, lote, associacao,
manejo, fechamento, certificacao, PDF e parametro administrativo.
As referencias por ID no corpo (animal, origem/destino de movimentacao,
fazenda do lote) mantem a cobertura das suites S2/S3.
Matriz conferida no AgroTracer_Guia_Comercial_Detalhado_v3_Revisado_TechLead.pdf,
pagina 19, secao 13.2 (documento fornecido por Samela). A marcacao historica
SEC-04 no teste de usuario zero e imprecisa; o cenario oficial e adulteracao
do ID sem reassinar, coberto pela suite S3. Usuario zero e cobertura adicional.
Review/QA humanos nao sao declarados concluidos. Logs de infraestrutura WordPress/proxy devem usar a politica
em docs/operacao/logs-seguros.md; nao houve alteracao do servidor do usuario.
