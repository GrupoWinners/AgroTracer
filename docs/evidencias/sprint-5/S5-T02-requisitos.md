# AG-97 / S5-T02 — PDF

Fonte: https://losel.atlassian.net/browse/AG-97 (2026-11-18).
Responsavel: Samela; status consultado: Fazendo.
Depende de S5-T01; bloqueia S5-T06.

Escopo: PDF com metodo, source_type, versao e snapshot_sha256;
pdf_sha256 salvo no banco apos geracao. Aceite: sem PII desnecessaria;
hash do PDF armazenado depois da geracao, nunca incluido no proprio PDF.

GET /api/v1/certificados/{id}/pdf exige HMAC e proprietario. Primeiro
download gera o documento e persiste bytes + SHA-256 numa transacao;
downloads seguintes devolvem os mesmos bytes, apos conferir integridade.
O lock do certificado evita geracoes concorrentes divergentes.
X-PDF-SHA256 informa o hash dos bytes; Cache-Control: no-store.
Erro 503 PDF_INDISPONIVEL permite repetir sem perder o certificado.
Erro 409 sinaliza divergencia de integridade de snapshot/arquivo.

PDF usa somente campos permitidos do snapshot: identificadores do
certificado/lote, metodo e versoes, tipos de origem, resultados/unidades,
data e quantidade de abate, hash do snapshot. Exclui nomes, documento,
contato, localizacao, identificadores de animais, token e source_uri.
Valores do snapshot sao preservados sem arredondamento. SYNTHETIC recebe
rotulo didatico explicito. Markup em valores e escapado antes de renderizar.

QR e pagina publica/DTO nao constam do escopo desta issue; a integracao
publica pertence a S5-T05. Nao foi inventado dominio ou URL publica.
O token original nao e incorporado ao arquivo persistido, em conformidade
com S5-T03. A equipe precisa definir a entrega/retencao do link e eventual
QR na integracao publica sem violar a regra de armazenar somente hash.

Testes cobrem conteudo, hash exato, minimizacao, autorizacao, corrupcao,
rollback/retry de geracao e versoes longas. Tambem ha teste integrado de
emissoes concorrentes em sessoes PostgreSQL independentes e schema isolado.
PDF sintetico e preview sao evidencias visuais; nao sao certificados reais.

DoD do Jira: implementacao versionada sem segredo, teste/evidencia,
erros definidos, documentacao/OpenAPI/ADR conforme necessario, review de
outro integrante e QA Gate conforme risco, nenhum P1/P2 aberto relacionado.
Review e QA humanos permanecem pendentes. Nao fazer merge automaticamente.
