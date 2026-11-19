# Backup e restore — AgroTracer

## Custodia e escopo

AG-107 / S6-T06: equipe; Samela cuida de FastAPI/PostgreSQL/segredos;
Joao Vitor de WordPress/Bridge/proxy. Depende AG-103 e AG-104; bloqueia
S7-T01/S7-T03. Aceite: login e certificado consultaveis apos restore e RTO
academico registrado. Backup sem restore nao e evidencia.

O PDF esta persistido em `certificados_pdf.conteudo` (BYTEA), com SHA-256.
Por isso o dump completo de PostgreSQL inclui PDFs, certificados, tokens
HASH, snapshots, auditoria, constraints, triggers e versao Alembic.
WordPress exige banco MariaDB/MySQL e `wp-content` (uploads/plugins/themes).
Configuracao, chaves HMAC, credenciais, certificados TLS e infraestrutura
precisam de custodia separada, acesso restrito e restauracao coordenada.
Nao registrar esses valores no Git, Jira, logs ou artifact de CI.

## Ensaio automatizado (somente dados sinteticos)

Requisitos: Docker Linux, Python e requirements-dev.txt, Redis exclusivo de
teste. No backend definir AGROTRACER_RESTORE_DRILL=1 e
AGROTRACER_TEST_REDIS_URL para esse Redis; executar:

```sh
python -m pytest tests/test_s6_t06_restore.py -v -s --tb=short
```

A CI executa o job `recuperacao` e publica somente `s6-restore/restore-ci.json`.
O teste cria rede, containers e volumes com prefixo aleatorio `agrotracer-s6-`.
Nunca usa a base indicada no .env para backup/restore; URLs sao geradas a partir
dos containers novos. Portas expostas apenas em loopback e alocadas pelo Docker.
O cleanup so remove os nomes criados nesta execucao. Nao executar docker prune.

1. Provisionar origem e destino vazios, mesma versao dos bancos/WP.
2. Aplicar migrations reais na origem; inserir dados SYNTHETIC, emitir
   certificado e PDF pelo servico e instalar WP/Bridge com usuario sintetico.
3. Validar login antes do backup; sem escritores concorrentes, capturar
   pg_dump -Fc, SQL WordPress e tar de wp-content.
4. Desligar a origem. Iniciar cronometro e executar pg_restore --exit-on-error
   no destino vazio, importar SQL WP e restaurar wp-content. Ajustar home/siteurl
   para a porta do destino e verificar Bridge ativo e arquivo de upload.
5. Fazer login HTTP real com cookie WordPress; consultar certificado publico
   usando token original mantido apenas na memoria; baixar PDF com HMAC real,
   Redis real e verificar SHA-256 identico. Encerrar cronometro.
6. Emitir JSON sem senhas/token/dumps e remover recursos temporarios.

O RTO academico comeca no pg_restore e termina apos todas as verificacoes.
Destino ja provisionado: nao inclui pull de imagens, provisionamento, DNS,
TLS, rotacao de segredos nem volume de producao. Nao e SLA ou RPO de producao.
Backups do ensaio vivem apenas na memoria do processo e sao descartados;
este teste NAO configura um agendamento nem armazenamento de backup real.

## Procedimento do ambiente homologado (custodia conjunta)

- Registrar versoes/digests, revisao Git/Alembic e responsaveis. Suspender
  escritas no backend e WP para alinhar banco/arquivos entre os componentes.
- Exportar PostgreSQL com pg_dump -Fc; WP com wp db export; arquivar wp-content.
  Guardar manifesto com SHA-256/tamanho/data dos arquivos e verificacao de
  integridade. Transferir criptografado para armazenamento restrito fora do
  servidor. Definir retencao, RPO e frequencia com os responsaveis (nao constam
  como numeros no Jira); validar permissao de leitura e recuperacao das chaves.
- Restaurar primeiro em destino vazio e isolado, usando as mesmas versoes;
  nao sobrescrever producao como parte deste ensaio. Restaurar segredos por
  canal seguro, conferir proxy, URLs e TLS. Redis de rate limit e efemero;
  nao importar cache de producao. Preservar a chave HMAC coordenadamente nos
  dois lados, sem expor nos registros.
- Repetir login, certificado valido/revogado, PDF/hash, autorizacao por objeto
  e limites; registrar tempo de ponta a ponta, volumes, resultado e revisor.
- Cutover/rollback do ambiente real exigem planejamento conjunto e QA/review;
  esta entrega nao altera servidores ou credenciais reais.

Referencias oficiais:
- https://www.postgresql.org/docs/16/app-pgdump.html
- https://www.postgresql.org/docs/16/app-pgrestore.html
- https://developer.wordpress.org/cli/commands/db/export/
- https://developer.wordpress.org/cli/commands/db/import/
