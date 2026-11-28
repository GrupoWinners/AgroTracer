# ADR — S2-T03: Cronologia das movimentações (RN-07)

## Status

Proposta implementada, pendente de revisão técnica.

## Contexto

A RN-07 exige que movimentações tenham exatamente
um alvo (animal XOR lote), respeitem a cronologia
e não tenham origem igual ao destino.

## Decisões

1. A movimentação pertence a exatamente um animal
   ou um lote, nunca a ambos.

2. Uma nova movimentação precisa ter data/hora
   estritamente posterior à última movimentação
   registrada para o mesmo alvo.

3. Eventos com data/hora igual ou anterior ao
   último evento são rejeitados com HTTP 409 e
   código MOVIMENTACAO_FORA_DE_ORDEM.

4. A entrada exige data/hora com timezone.

5. A gravação utiliza bloqueio de linha
   SELECT FOR UPDATE no animal ou lote para
   serializar operações concorrentes.

6. O PostgreSQL aplica CHECK XOR, CHECK de
   origem/destino e FKs com ON DELETE RESTRICT.

7. A movimentação e sua auditoria são gravadas
   na mesma transação.

8. As rotas privadas verificam a propriedade
   do alvo e dos talhões informados.

## Limites

O bloqueio de concorrência pressupõe que as
movimentações sejam registradas pelo serviço
responsável pela validação cronológica.

Inserções SQL diretas não passam por essa validação;
as CHECKs garantem XOR e origem/destino, mas não
a ordem temporal entre registros.

Esta política cronológica deve ser revisada pela
equipe antes do merge definitivo.

## Validação

- Testes de integração PostgreSQL.
- Testes de constraints e FKs.
- Testes de API e auditoria.
- Testes de autorização.
- Teste de concorrência com duas transações.
