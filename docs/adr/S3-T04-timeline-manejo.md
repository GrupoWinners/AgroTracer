# ADR — S3-T04: Timeline de manejo nutricional e identificação de conflitos (RN-08)

## Status

Implementado, pendente de revisão de outro integrante e QA Gate.

## Contexto

A regra de negócio RN-08 determina que os períodos de manejo nutricional de um lote não podem possuir sobreposição temporal (datas inclusivas). O produtor rural necessita de uma interface clara para cadastrar períodos alimentares, visualizar a timeline contínua de manejo e ser alertado de forma precisa quando houver colisão de datas, identificando explicitamente o período conflitante. Adicionalmente, conforme as decisões tomadas na S3-T02 e S3-T06, os fatores zootécnicos devem apresentar unidades claras e ser devidamente rotulados quanto à proveniência, evitando alegações científicas indevidas no MVP.

## Decisões

1. **Interface de Timeline Contínua (`templates/manejo.php`)**:
   - Apresenta a sequência cronológica de períodos alimentares para o lote selecionado.
   - Exibe datas formatadas em padrão explícito (DD/MM/AAAA) acompanhadas da duração total em dias inclusivos.
   - Exibe fatores zootécnicos com unidades claras: `kg MS/cab/dia` (Consumo de Matéria Seca), `% EB` (Conversão de Metano Entérico) e `kg CH4/cab/ano` (Emissão Entérica).
   - Apresenta aviso de transparência metodológica destacando que os fatores ativos pertencem à versão `v1.0-2026 (SYNTHETIC / Didático)`, sem alegação científica indevida junto a órgãos oficiais.

2. **Detecção e Identificação do Período Conflitante**:
   - A validação de sobreposição opera tanto no front-end em tempo real (inline) quanto na resposta segura do backend / Bridge (HTTP 409).
   - Quando detectada sobreposição (`inicio_a <= fim_b && inicio_b <= fim_a`), o sistema não emite apenas um erro genérico: identifica nominalmente as datas do período conflitante já existente (ex: `01/11/2026 a 10/11/2026`).
   - O botão de envio do formulário permanece desabilitado enquanto persistir sobreposição temporal, prevenindo submissões inválidas (conforme BDD `design-ux.feature`).

3. **Estados de UX Completos**:
   - Estado de Carregamento (Loading State com spinner oficial).
   - Estado Vazio (Empty State com CTA direcionado para o primeiro cadastro quando o lote não possuir períodos).
   - Estado de Conflito (Banner de alerta semântico `danger` + caixa de alerta no modal).
   - Estado com Dados (Timeline gráfica com itens ordenados, badges de status e contadores de integridade).

4. **Integração Bridge REST & HMAC**:
   - Endpoint WordPress REST `POST /agrotracer/v1/manejos`: despacha a criação para `POST /api/v1/lotes/{lote_id}/manejos` com assinatura HMAC-SHA256 e Correlation ID.
   - Endpoint WordPress REST `GET /agrotracer/v1/manejos`: consulta os manejos ordenados do lote via `GET /api/v1/lotes/{lote_id}/manejos`.
   - Endpoint WordPress REST `GET /agrotracer/v1/parametros`: disponibiliza conjuntos de parâmetros versionados com proveniência explícita.
   - Em caso de 409 `MANEJO_SOBREPOSTO`, propaga o período conflitante (`detalhes.inicio` e `detalhes.fim`) no envelope JSON.

## Consequências

- O produtor obtém feedback imediato e compreensível sobre por que uma data não pode ser utilizada e qual manejo anterior está ocupando aquele período.
- A Sprint 4 (Cálculo e Certificação) poderá consumir a timeline ordenada de manejos e a versão associada dos parâmetros sem risco de períodos duplicados ou lacunas confusas.
