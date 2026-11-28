# S1-T01 — Modelagem inicial de dados e auditoria

## Objetivo

Implementar a estrutura inicial de produtores, fazendas,
talhões e eventos de auditoria no PostgreSQL.

## Tabelas

### produtores
- Identificador interno com Identity.
- wordpress_user_id obrigatório, único e positivo.
- Identidade vinculada ao WordPress.

### fazendas
- Identificador interno com Identity.
- produtor_id obrigatório.
- FK com ON DELETE RESTRICT.
- numero_car_informado opcional.
- CAR declarado, sem validação oficial.

### talhoes
- Identificador interno com Identity.
- fazenda_id obrigatório.
- FK com ON DELETE RESTRICT.
- area_hectares NUMERIC(12,4), obrigatória e positiva.

### auditoria_eventos
- Identificador do evento.
- Entidade, ação e registro afetado.
- Identidade WordPress e correlation_id.
- Detalhes JSONB e data de criação.
- Eventos devem preservar informações históricas.
- Não armazenar senhas, tokens ou segredos.

## Integridade e erros

- 23505: valor único já cadastrado.
- 23514: valor inválido para uma CHECK.
- 23503: relacionamento inválido ou exclusão bloqueada.
- 23502: campo obrigatório ausente.

A conversão para códigos e mensagens da API pertence
à implementação das próximas rotas CRUD.

## Migration

- Revision: s1t01_modelos
- Upgrade: cria as quatro tabelas.
- Downgrade: remove as quatro tabelas.
- Chaves estrangeiras com ON DELETE RESTRICT explícito.

## Evidências

- S1-T01-migrations.txt
- S1-T01-pytest.txt
- S1-T01-flake8.txt

## Limites e pendências

- CAR é dado declarado; não há consulta oficial.
- Confirmar a definição completa das RN-01 e RN-02.
- Validar o esquema com a equipe antes do merge.
- QA Gate e code review dependem de aprovação formal.
- CRUD protegido ponta a ponta pertence às tasks seguintes.

## Ajustes solicitados no Code Review

Foram realizados os seguintes ajustes:

- Adicionados nome, municipio e uf à tabela fazendas.
- Adicionada unicidade de numero_car_informado (RN-02).
- Adicionado identificador obrigatório à tabela talhoes.
- Criada migration incremental s1t01_campos.
- Atualizados os testes de integridade do PostgreSQL.

## Validações realizadas

Ambiente: PostgreSQL 16.

- Pytest: 54 testes aprovados.
- Flake8: aprovado sem erros.
- Migration inicial: aprovada.
- Migration incremental: aprovada em banco vazio.
- Downgrade e novo upgrade: aprovados.
- FKs com ON DELETE RESTRICT: confirmadas.
- Unicidade do CAR: validada.
- Campos obrigatórios: validados.
- Área positiva dos talhões: validada.

## Proteção de dados existentes

A migration incremental foi testada em um banco contendo:

- 1 produtor.
- 1 fazenda.
- 1 talhão.
- 1 evento de auditoria.

A execução foi interrompida intencionalmente porque existem
registros que ainda não possuem os novos campos obrigatórios.

Após a tentativa:

- Os quatro registros permaneceram preservados.
- A revisão continuou em s1t01_modelos.
- Nenhuma alteração parcial de estrutura foi identificada.

## Pendência de migração de dados legados

A migration atual não realiza preenchimento automático de
nome, municipio, uf ou identificador.

Para atualizar bancos já populados, será necessário obter
os valores reais desses campos e definir um procedimento de
migração de dados com a equipe.

Esta validação comprova a interrupção segura, mas não
comprova a conclusão da migração de um banco populado.

A estratégia de preenchimento deverá ser aprovada antes
do merge ou formalmente tratada como pré-condição de implantação.
