# AG-104 / S6-T03 — medicao e N+1

Fonte: https://losel.atlassian.net/browse/AG-104, lida em 2026-11-19.
Samela; 5 pontos; entrega 26/11. Depende S6-T02, bloqueia S6-T06.
Escopo: p95 CRUD <800 ms, PDF <=3 s, investigar N+1 e indices.
Aceite: medicoes registradas e regressoes conhecidas; nao otimizar sem dado.

## Evidencia e alteracao

`S6-T03-nmais1-antes.txt` registra a falha real: 20 manejos da mesma dieta
consultavam os mesmos fatores 20 vezes. Agora o fechamento reutiliza fatores
por (parametro_set_id, dieta) apenas na mesma transacao; teste exige uma
consulta tanto para 1 quanto para 20 manejos. Nenhum cache global ou alteracao
do snapshot/historico. Calculos, arredondamento e isolamento preservados.

`S6-T03-performance-local.json` contem todas as 30 amostras por operacao,
3 aquecimentos excluidos, p95 nearest-rank e metas. SQLite local: criar
18,785 ms; listar 22,760 ms; editar 15,370 ms; gerar/persistir PDF 36,335 ms;
download 35,465 ms. Todos abaixo das metas nesse cenario.
A geracao remove apenas o PDF sintetico da fixture antes de cada amostra,
para nao medir apenas o download/cache. Nao altera dados reais.

CI executa a mesma medicao em PostgreSQL num schema unico isolado e registra
os indices do schema publico migrado. Exporta `s6-performance` como artifact.
Para reproduzir: executar `pytest tests/test_s6_t03* -q` no backend, opcionalmente
com AGROTRACER_PERF_REPORT apontando para JSON. PostgreSQL exige a base de
TESTE `agrotracer_s2_t01_teste`; esquema temporario e removido ao final.

## Indices e limites

O indice unico de fatores por conjunto/chave ja atende a busca por conjunto.
Os indices existentes de manejo por lote e de certificado por snapshot/lote
sao preservados e inventariados na evidencia da CI. Nao ha medicao que
justifique novo indice/migration nesta entrega. A listagem administrativa
ja usa selectinload de fatores. A melhoria demonstrada e reduzir consultas
repetidas, nao prometer ganho de latencia de producao.

Teste ASGI, um cliente sequencial, 34 fazendas e um lote/animal/certificado:
nao inclui rede, proxy, WordPress, HMAC/Redis nem concorrencia. As tabelas do
benchmark sao criadas do metadata; os testes de integracao existentes continuam
validando as migrations no banco principal de teste. Volumes reais e p95
ponta a ponta precisam ser medidos no ambiente homologado. Nenhuma regressao
observada neste recorte; QA/review humano e homologacao continuam pendentes.
