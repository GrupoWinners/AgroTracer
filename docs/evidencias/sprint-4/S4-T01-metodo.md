# S4-T01 — CarbonEngine

Implementacao separa motor de calculo puro (Decimal) da leitura SQLAlchemy
dos fatores por parametro_set_id e versao. Cada periodo de manejo contabiliza
inicio/fim inclusivos. Nao existe arredondamento por etapa.

## Contrato de chaves

- FE_BASE_DIETA:<TIPO_DIETA>: kg CO2e/cabeca/dia
- K_IDADE: unidade 1 ou adimensional
- K_PASTAGEM: unidade 1 ou adimensional
- K_SUPLEMENTACAO: unidade 1 ou adimensional

Nenhum multiplicador ausente recebe 1 automaticamente. Cada fonte e unidade
segue o conjunto versionado. A quantidade de animais e fornecida ao motor
explicitamente e sera validada pelo dominio de fechamento (S4-T02).

## Referencia exclusivamente matematica

50 cabecas x 90 dias x 2.10 = 9450 kg CO2e;
50 cabecas x 60 dias x 1.40 = 4200 kg CO2e.
Total 13650 kg CO2e.
Carcaca 50 x 540 kg x 0.53 = 14310 kg.
Intensidade 13650 / 14310 = ~0.954 kg CO2e/kg carcaca.

Valores sinteticos/didaticos, nao representam fatores oficiais IPCC/Embrapa.

## QA pendente

Executar pytest e flake8 no ambiente do projeto e confirmar CI.
