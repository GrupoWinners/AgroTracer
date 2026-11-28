# AG-107 / S6-T06

Fonte: https://losel.atlassian.net/browse/AG-107, lida em 2026-11-19.
Samela no Jira; trabalho em equipe com Joao Vitor (comentario da issue).
5 pontos; entrega 27/11. Depende S6-T02/S6-T03; bloqueia S7-T01/S7-T03.
Aceite: backup E restore PostgreSQL, WordPress e PDFs, login/certificado
consultaveis apos restore e RTO academico registrado.

Implementacao e reproducao: docs/operacao/backup-restore.md.
Ensaio opt-in: backend/tests/test_s6_t06_restore.py; CI job recuperacao.
Nao e suficiente ter dump: teste somente passa depois de restaurar em destino
vazio, desligar a origem e validar login HTTP, certificado publico e PDF/hash.
Sem nova migration: restaura o schema migrado existente integralmente.
Sem modificacao de dados, servidores, credenciais ou backups do usuario.

A evidencia real de execucao deve vir do job/relatorio, nao deste plano.
Review de outro integrante, QA Gate e validacao do ambiente homologado
permanecem sob responsabilidade da equipe; nenhum merge automatico.

## Execucao comprovada

CI 132, commit d772239f3414e7a9db36a0de176ad323425c4275: job recuperacao
aprovado. RTO academico 4,389 s. Relatorio S6-T06-restore-ci.json: origem
desligada, login WordPress, arquivo/plugin, certificado publico e PDF
autenticado HMAC/Redis com hash identico. Job verificacoes tambem aprovado.
https://github.com/GrupoWinners/AgroTracer/actions/runs/44582596016

Falhas iniciais do laboratorio foram corrigidas antes desta evidencia:
invocacao explicita do WP-CLI e HOME gravavel para usuario 33:33.
Dumps e credenciais nao foram publicados. Nenhuma homologacao humana foi
substituida pela execucao automatizada.
