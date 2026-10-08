
# ADR 0001 - Estrutura do Repositorio e CI

Data: 08/10/2026
Projeto: AgroTracer
Equipe: Grupo Winners
Sprint: 0
Tarefa: S0-T02 - Repositorio, estrutura, .gitignore, branches e CI minimo

## Status

Proposto - aguardando aprovacao da equipe.

## Contexto

O projeto AgroTracer necessita de uma estrutura de desenvolvimento organizada para facilitar o trabalho em equipe e permitir que os integrantes desenvolvam suas atividades de forma independente.

Para isso, e necessario definir a organizacao das pastas, padronizar as ferramentas utilizadas e configurar um ambiente que possa ser reproduzido por todos os desenvolvedores.

Tambem e importante implementar verificacoes automaticas para identificar possiveis erros antes que novas alteracoes sejam incorporadas a branch principal do projeto.

## Decisao

Foram propostas as seguintes decisoes tecnicas para o desenvolvimento do AgroTracer:

- Python 3.14.7: versao definida pela equipe para o desenvolvimento do backend.
- Flake8 7.4.1: ferramenta escolhida para verificar problemas de qualidade e formatacao do codigo Python.
- Pytest 9.1.1: ferramenta utilizada para executar testes automatizados.
- GitHub Actions: ferramenta de integracao continua responsavel por executar automaticamente o lint e os testes.
- Estrutura do backend: organizacao em pacotes separados, incluindo core, api/v1, domain, services, repositories, models, schemas e db.
- WordPress: criacao de um diretorio reservado para o futuro desenvolvimento do plugin.
- Git: utilizacao de branches separadas para o desenvolvimento das funcionalidades, seguindo os padroes feature/PY-xx, feature/WP-xx e qa/QA-xx.
- Pull Requests: adocao de revisao por outro integrante antes da incorporacao de alteracoes a branch main.
- Seguranca: utilizacao do .gitignore para evitar o versionamento de arquivos locais e do .env.example para documentar configuracoes sem expor credenciais reais.

A escolha do Flake8 ocorreu apos um bloqueio de execucao do Ruff por uma politica de seguranca do Windows no ambiente de desenvolvimento. O Flake8 foi instalado e executado com sucesso, atendendo a necessidade de analise estatica do projeto.

## Consequencias

A estrutura proposta facilita a organizacao do codigo e permite que diferentes integrantes trabalhem em partes especificas do AgroTracer.

A utilizacao do Flake8 e do Pytest contribui para identificar problemas de codigo e verificar comportamentos esperados durante o desenvolvimento.

O GitHub Actions permitira automatizar essas verificacoes, reduzindo o risco de incorporar alteracoes com falhas a branch principal.

Como consequencia, todos os integrantes precisarao manter seus ambientes atualizados, respeitar as convencoes de branches e commits e executar as verificacoes necessarias antes de solicitar a revisao de suas alteracoes.

As dependencias tambem deverao ser mantidas compativeis com a versao Python 3.14.7 adotada pelo projeto.

## Decisoes pendentes

A estrategia de autenticacao e seguranca da comunicacao entre o plugin WordPress e o backend Python ainda precisa ser definida e documentada em um ADR especifico, antes da implementacao da integracao real.

A aprovacao deste ADR e a configuracao definitiva das regras de protecao da branch main tambem deverao ser confirmadas pela equipe.

## Validacao

No ambiente local de desenvolvimento, foram realizadas as seguintes verificacoes:

- Execucao do Flake8 sem apresentar erros.
- Execucao do Pytest com um teste aprovado.
- Criacao da estrutura inicial do backend.
- Criacao das pastas de documentacao e do plugin WordPress.
- Criacao dos arquivos .gitignore e .env.example.
- Documentacao dos comandos de instalacao, lint e testes no README.

A execucao do CI no GitHub Actions, a aprovacao do Pull Request e a revisao por outro integrante ainda serao verificadas antes da conclusao da tarefa S0-T02.
