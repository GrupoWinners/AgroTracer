# S1-T01 — Modelagem inicial de dados e auditoria (Refinamento Guia v3.0)

## Objetivo
Implementar a estrutura inicial de persistência para produtores, fazendas, talhões e eventos de auditoria no PostgreSQL, em conformidade com as regras de negócio e contratos da Sprint 1 do Guia v3.0.

## Entidades e Tabelas

### 1. `produtores`
- Identificador interno `BigInteger` com `Identity()`.
- `wordpress_user_id` obrigatório, único (`uq_produtores_wordpress_user_id`) e positivo (`ck_produtores_wordpress_user_id_positivo`).
- Aplicação do princípio de identidade única delegada ao WordPress (sem armazenamento de senhas no Python).

### 2. `fazendas`
- Identificador interno `BigInteger` com `Identity()`.
- `produtor_id` obrigatório, com `ForeignKey("produtores.id", ondelete="RESTRICT")`.
- `nome` (String 120, obrigatório, `ck_fazendas_nome_obrigatorio`).
- `municipio` (String 80, obrigatório, `ck_fazendas_municipio_obrigatorio`).
- `uf` (String 2, obrigatório, `ck_fazendas_uf_tamanho`).
- `numero_car_informado` (Text, opcional, tratado como dado declarado).
- **RN-02**: `UniqueConstraint("numero_car_informado", name="uq_fazendas_numero_car_informado")` para deduplicação local declarada.

### 3. `talhoes`
- Identificador interno `BigInteger` com `Identity()`.
- `fazenda_id` obrigatório, com `ForeignKey("fazendas.id", ondelete="RESTRICT")`.
- `identificador` (String 50, obrigatório, `ck_talhoes_identificador_obrigatorio`, ex: "Piquete 01").
- `area_hectares` (`Numeric(12, 4)`, obrigatória, `ck_talhoes_area_hectares_positiva` > 0).
- `UniqueConstraint("fazenda_id", "identificador")` para evitar nomes duplicados na mesma fazenda.

### 4. `auditoria_eventos`
- Identificador do evento `BigInteger` com `Identity()`.
- `entidade` (String 50) e `acao` (String 30) obrigatórias e não-vazias (`btrim <> ''`).
- `entidade_id` (`BigInteger`, opcional).
- `wordpress_user_id` (`BigInteger`, opcional) e `correlation_id` (String 128, opcional).
- `detalhes` em formato `JSONB`.
- `criado_em` (`TIMESTAMPTZ`, default `now()`).
- Sem persistência de segredos ou senhas (RF-16 / RNF-07).

## Integridade e Tratamento de Erros
- `23505`: violação de unicidade (CAR duplicado, usuário WP duplicado, talhão duplicado).
- `23514`: violação de CHECK constraint (área negativa/zero, UF inválida, strings vazias).
- `23503`: violação de chave estrangeira ou bloqueio por `ON DELETE RESTRICT`.

## Migration Alembic
- Revision: `s1t01_modelos`
- Down Revision: `4b5cbbc1616c` (extensão `btree_gist`)
- Upgrade: DDL completo das 4 tabelas e constraints.
- Downgrade: remoção ordenada das 4 tabelas com rollback íntegro.
