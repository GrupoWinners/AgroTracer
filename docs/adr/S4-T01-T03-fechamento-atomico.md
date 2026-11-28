# ADR — S4-T01 a S4-T03: Fechamento deterministico e snapshot

## Contexto e escopo

O CarbonEngine realiza calculo didatico deterministico por periodos de
manejo, sem equivalencia a inventario cientifico oficial.

## Politicas para o MVP

1. Decimal em todo calculo, datas de manejo inclusivas; sem arredondamento
   em cada etapa. Nao ha fator magico: multiplicadores ausentes falham.
2. Um unico parametro_set_id por fechamento, mas diferentes chaves de
   FE_BASE_DIETA por tipo_dieta dentro do mesmo conjunto.
3. O conjunto deve estar publicado (ATIVO ou INATIVO) e cobrir o periodo
   de vigencia. SNAPSHOT registra versao de parametros e versao do metodo.
4. Contagem usa lote_animais no tempo. Associacao parcial dentro de um
   manejo e rejeitada; deve-se dividir o manejo em periodos sem ambiguidades.
   DATETIME e interpretado em UTC no MVP.
5. O numero de abate nao pode exceder o numero comprovado no ultimo
   manejo. Denominador nao positivo retorna 422; nao se emite certificado.
6. Fechamento, status do lote, snapshot e auditoria sao confirmados na mesma
   transacao. Falha em qualquer passo faz rollback integral.
7. PostgreSQL impede UPDATE/DELETE do snapshot e exige snapshot no COMMIT
   de fechamento por trigger DEFERRABLE. Isso protege RN-11/RN-21.
8. O MVP trata fecho repetido como conflito 409, sem criar outro registro.

## Pendencias de revisao

- Concordancia do orientador/PO sobre contagem temporal e timezone UTC.
- Politica de quantidade abatida menor que a ultima contagem.
- Definicao de evolucao para mais de um conjunto versionado por lote.
- Confirmar com Joao Vitor o payload/resposta do POST de fechamento.
- Conferir migrações no PostgreSQL de testes e QA Gate com Nadiny.

## Transparencia cientifica

Exemplo 13650 kg CO2e e 0.954 de intensidade e exclusivamente sintetico.
Nenhuma cifra foi atribuida ao IPCC/Embrapa sem referencia completa.
