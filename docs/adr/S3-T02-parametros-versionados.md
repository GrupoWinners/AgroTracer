# ADR — S3-T02: Parâmetros versionados

## Contexto

O AgroTracer necessita de fatores rastreáveis, versionados e
classificados quanto à origem, conforme RN-16 e RN-22.

## Decisões

1. Cada parametro_set possui uma versão única.
2. O MVP permite apenas um parametro_set ATIVO globalmente.
3. Novos conjuntos começam em RASCUNHO.
4. A ativação exige administrador e justificativa.
5. A ativação anterior passa para INATIVO.
6. Conjuntos publicados e seus fatores são imutáveis.
7. Fatores usam NUMERIC/Decimal, chave, unidade e source_type.
8. Fatores não sintéticos exigem source_uri.
9. A ativação utiliza lock transacional e índice parcial UNIQUE.
10. A aplicação registra alterações e ativações em auditoria,
    na mesma transação dos dados.

## Transparência científica

Fatores SYNTHETIC são exclusivamente didáticos.

Nenhum valor sintético poderá ser apresentado como fator
oficial do IPCC ou da Embrapa.

## Limitações e riscos

A regra de um único conjunto ativo é uma política inicial
do MVP e deverá ser revista caso surjam famílias de métodos
independentes.

A imutabilidade das versões publicadas é protegida por
triggers PostgreSQL. A auditoria das edições em rascunho
é garantida pelos serviços da aplicação, não por trigger.

Portanto, gravações diretas no banco devem ser restritas
a operadores autorizados. Qualquer rotina de importação ou
seed deve utilizar serviços auditados ou auditoria equivalente.

A autorização administrativa inicial utiliza IDs WordPress
configurados no servidor, após autenticação HMAC.

## Consequências

A Sprint 4 poderá identificar a versão dos parâmetros
utilizados no cálculo e preservar resultados históricos.

## Validação pendente

Revisão por outro integrante e aprovação do QA Gate.
