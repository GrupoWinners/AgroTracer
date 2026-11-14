# ADR — S4-T05: Separação entre Validade Matemática e Validade Científica no CarbonEngine

## Status
Aprovada

## Data
2026-11-14

## Contexto e Escopo

No âmbito da Sprint 4 (Fechamento e CarbonEngine), o sistema AgroTracer calcula as emissões estimadas de gases de efeito estufa (GEE) decorrentes do manejo nutricional de lotes bovinos e a respectiva intensidade carbônica por quilograma de carcaça abatida.

Cálculos ambientais e zootécnicos enfrentam frequentemente o risco de ambiguidades entre:
1. A exatidão algorítmica da computação (ausência de erros numéricos, divisões por zero ou perdas de precisão).
2. A legitimidade científica das conclusões biológicas (conformidade com metodologias IPCC Tier 2/3, GHG Protocol Agropecuário ou medições diretas de campo).

Para evitar que dados didáticos de homologação sejam equivocadamente interpretados como inventários chancelados, fez-se necessária uma decisão formal de arquitetura.

## Decisão Arquitetural

1. **Separação Rígida de Camadas:**
   - O módulo `carbon_engine.py` é um motor computacional puramente aritmético e determinístico.
   - Ele não possui "opinião" científica sobre a adequação dos coeficientes; seu compromisso restringe-se à **validade matemática**:
     - Aritmética estrita com `decimal.Decimal` em precisão de 80 dígitos (`ctx.prec = 80`).
     - Rejeição absoluta de ponto flutuante binário (`float`), `NaN` e infinitos.
     - Extremos de datas estritamente inclusivos: $(\text{fim} - \text{inicio}) + 1$.
     - Rejeição de divisões por zero na intensidade: denominadores nulos ou negativos retornam `None`.
     - Ausência de arredondamento intermediário por etapa.

2. **Governança de Validade Científica via Parâmetros Versionados:**
   - A validade científica pertence à camada de dados e proveniência (`ParametroSet`, `Fator` e `carbon_fatores_service.py`).
   - Todos os fatores consumidos pelo motor exigem vinculação a um conjunto publicado (`parametro_set_id`) e versão explícita.
   - Fatores cadastrados com tipo `SYNTHETIC` são explicitamente identificados como sintéticos/didáticos.
   - Fatores que aleguem fonte externa exigem `source_uri` obrigatório e validado.
   - A documentação e relatórios gerados devem declarar explicitamente quando os dados utilizam a calibração sintética de referência do MVP ($13.650\text{ kg CO}_2\text{e}$ / $0,954\text{ kg CO}_2\text{e}/\text{kg carcaça}$).

## Consequências

### Positivas
- **Auditabilidade e Reprodutibilidade:** Qualquer auditor pode reproduzir o cálculo manualmente e obter exatamente os mesmos decimais, sem desvios por arredondamento de hardware.
- **Transparência Regulatória:** Protege a plataforma contra acusações de *greenwashing* ou emissão indevida de certificações oficiais sem chancela científica.
- **Desacoplamento e Evolutividade:** Permite atualizar o conjunto de fatores científicos para versões reais (Embrapa/IPCC) no futuro sem alterar uma única linha do motor de cálculo puro.
- **Resiliência:** Previne falhas de sistema (`ZeroDivisionError`) e comportamentos indefinidos diante de dados de abate incompletos.

### Mitigações
- Relatórios emitidos pela aplicação contêm aviso de responsabilidade científica referente à versão dos parâmetros vigentes.
- A suíte de testes `test_s4_t05_casos_limite.py` monitora continuamente a integridade de todas as condições de contorno e premissas numéricas.
