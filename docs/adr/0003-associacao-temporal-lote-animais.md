# ADR-003 — Associação temporal entre animais e lotes

**Status:** Aceito conforme Guia AgroTracer v3.0

## Contexto

O AgroTracer precisa preservar o histórico de associação
dos animais aos lotes, permitindo rastrear entradas,
saídas e transferências sem perder os vínculos anteriores.

Manter animais.lote_id criaria uma fonte duplicada do
lote atual, sujeita a inconsistências.

## Decisão

Utilizar a tabela lote_animais como fonte única dos
vínculos entre animais e lotes.

A tabela terá:

- id: chave primária.
- animal_id: FK obrigatória para animais.id.
- lote_id: FK obrigatória para lotes.id.
- associado_em: TIMESTAMPTZ obrigatório.
- desassociado_em: TIMESTAMPTZ opcional.

Ambas as FKs terão ON DELETE RESTRICT.

## Associação ativa

Uma associação estará ativa quando:

desassociado_em IS NULL

Criar o índice parcial:

CREATE UNIQUE INDEX uq_animal_associacao_ativa
ON lote_animais(animal_id)
WHERE desassociado_em IS NULL;

A restrição deverá impedir a dupla associação ativa,
inclusive em requisições concorrentes.

## Integridade temporal

Aplicar a restrição:

CHECK (
    desassociado_em IS NULL
    OR desassociado_em >= associado_em
)

O encerramento de uma associação deverá atualizar
desassociado_em, preservando o registro histórico.

## Regras complementares

- RN-04: lotes pertencem a fazendas e têm estados.
- RN-05: identificador do animal é único.
- RN-06: um animal possui no máximo uma associação ativa.
- animais.lote_id não será criado.
- Operações privadas exigem autenticação e autorização
  por objeto.
- Eventos relevantes deverão ser auditados.

## Validação

Os testes de integração deverão demonstrar:

1. Associação ativa válida.
2. Bloqueio de segunda associação ativa para o mesmo animal.
3. Preservação das associações encerradas.
4. Bloqueio de intervalo temporal inválido.
5. ON DELETE RESTRICT nas referências históricas.
6. Ausência da coluna animais.lote_id.
7. Integridade sob concorrência.

## Referência

AgroTracer — Guia de Engenharia, Produto,
Segurança, QA e Entrega Comercial.
Versão 3.0 — Revisão Tech Lead.

Seções 8, 10, 15, 16 e 20.
