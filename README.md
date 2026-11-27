# AgroTracer

Rastreabilidade pecuaria e demonstracao didatica de calculo de emissoes.
Sprint 7: instalacao reproduzivel, revisao e preparacao para QA da release.
Os fatores e dados de demo sao **SYNTHETIC**: nao constituem inventario real,
validacao cientifica ou certificacao ambiental independente.

## Do clone a demo local

Requisitos: Git, Python 3.12+ (CI 3.14.7), Docker com containers Linux e
Docker Compose v2 com `up --wait`. No Windows, abrir Docker Desktop antes.
O primeiro build baixa imagens e dependencias; reserve alguns minutos.
Os mesmos comandos funcionam em PowerShell, Git Bash e Linux:

```sh
git clone --branch develop https://github.com/GrupoWinners/AgroTracer.git
cd AgroTracer
python tools/demo.py up
python tools/demo.py verify
```

Enquanto o PR S7-T01 estiver em review, apos clonar use
`git switch feature/S7-T01` (ou a branch encadeada S7-T05 para sua revisao).
A demo e um projeto Compose independente, sem reutilizar banco/volumes do
`docker-compose.yaml` anterior. Nao exige editar wp-config, executar SQL manual,
instalar plugin pela interface ou copiar chave HMAC entre servicos.

Abra http://127.0.0.1:18080/agrotracer/ e faca login com o usuario e senha de
`.demo/acesso.json`. O bootstrap gera credenciais aleatorias e as guarda
somente em `.demo/` (ignorado no Git). Nao compartilhe esses arquivos ou
publique sua saida; no Windows, mantenha a pasta restrita a sua conta.
A API local fica em http://127.0.0.1:18000/health.

O bootstrap aplica `alembic upgrade head`, instala WordPress e Bridge,
provisiona as paginas, vincula o produtor ao ID real do usuario WP e cria:

- Fazenda SYNTHETIC S7, talhao, dois animais e dois lotes com manejo.
- Conjunto ativo S7-DEMO-SYNTHETIC-1, publicado apos inserir os fatores.
- Lote S7-DEMO-CERTIFICADO: snapshot, certificado, token e PDF persistidos.
- Lote S7-DEMO-PARA-EMITIR: pronto para demonstrar fechamento/emissao.

Para emitir o segundo lote: abate 2026-02-02, 1 animal, peso medio 540 kg,
rendimento 0.53. O arquivo de acesso tambem informa os IDs e o token do
primeiro certificado para consultar na pagina publica `/certificado/`.
`verify` valida login WP real, Bridge PHP -> HMAC -> API -> banco,
consulta publica e hash do PDF. Publica somente um resumo sem credenciais.

Reexecutar `up` preserva senhas e dados, nao duplica o seed nem recupera token
do banco. Se perder `.demo/acesso.json`, o token original nao pode ser
reconstituido; preserve o arquivo privado junto ao ambiente de demonstracao.
O seed exige opt-in e banco chamado `agrotracer_demo`; recusa banco com dados
preexistentes e nao apaga registros. A transacao inteira reverte em falha.
Nenhuma migration nova foi necessaria: as migrations existentes sao testadas
em instalacao limpa, inclusive triggers, constraints e PDFs.

Para encerrar preservando os dados:

```sh
python tools/demo.py stop
```

Para iniciar novamente, executar `up`. Nao executar `down -v` em ambientes
com dados a preservar. O job CI utiliza volumes novos e descartaveis.

### Diagnostico local

- Docker indisponivel: iniciar Docker Desktop em modo Linux e verificar
  `docker info`. Se o build falhar, verificar acesso aos registries e PyPI.
- Portas 18000/18080 ocupadas: liberar essas portas antes da primeira execucao.
- `DEMO_COMPOSE_FALHOU`: verificar `docker compose --env-file .demo/.env
  -p agrotracer-s7-demo -f ops/demo/compose.yaml ps` (comando em uma linha).
  Nao publicar `docker compose config`, dumps ou .demo, pois contem segredos.
- Falha no seed: nao limpar banco automaticamente. Conferir opt-in, migrations
  e uso exclusivo do projeto demo; dados de outro ambiente devem ser preservados.

## Desenvolvimento e testes

```sh
cd backend
python -m venv .venv
```

Ativar no PowerShell: `.venv\Scripts\Activate.ps1`; no Git Bash:
`source .venv/Scripts/activate`; no Linux: `source .venv/bin/activate`.

```sh
python -m pip install -r requirements-dev.txt
python -m flake8 app tests
python -m pytest -v -k "not test_s1_t01_postgresql"
```

Alguns testes exigem PostgreSQL/Redis exclusivos de teste; a CI fornece essas
bases e valida todas as migrations. O teste legado S1-T01 depende de configuracao
local e permanece fora do filtro historico da CI; nao usar base real para testes.
Para API manual, carregar variaveis conforme `.env.example`, migrar o banco e
usar `python -m app.run` (logs seguros, sem reload). O compose antigo segue
disponivel para desenvolvimento; nao e o caminho de instalacao da demo.

## Evidencias e operacao

- [Sprint 6: seguranca, performance e recuperacao](docs/evidencias/sprint-6/README.md)
- [Sprint 7: requisitos e reproducao](docs/evidencias/sprint-7/S7-T01.md)
- [Politica de logs](docs/operacao/logs-seguros.md)
- [Backup e restore](docs/operacao/backup-restore.md)

A demo e local e usa HTTP em loopback/rede Docker. Nao e configuracao de
producao: TLS, proxy, segredos, backups e homologacao exigem o checklist de
release e revisao conjunta. Nao publicar tag ou integrar PR antes de QA/review.
