# S4-T05 — Tabela de Expected Results, Casos Limite e Validação do CarbonEngine

**Épico:** `[EP-S4] Sprint 4 — Fechamento e CarbonEngine`  
**Task:** `S4-T05 — Tabela de expected results versionada com cálculo manual e casos limite`  
**Versão do Método Auditado:** `CARBONENGINE-MVP-1.0`  
**Data:** 14/11/2026  

---

## 1. Memória de Cálculo Manual e Fórmulas Oficiais do CarbonEngine

O cálculo determinístico do CarbonEngine opera exclusivamente com a biblioteca nativa `decimal.Decimal` em contexto de alta precisão (`ctx.prec = 80`), garantindo que **não ocorra nenhum arredondamento intermediário** entre as etapas de cálculo.

### 1.1. Contabilização Temporal de Período de Manejo
Cada período de manejo possui datas com extremos inclusivos:
$$\text{dias} = (\text{data\_fim} - \text{data\_inicio}) + 1$$

*Regra de Borda:* Se $\text{data\_inicio} == \text{data\_fim}$, o período contabiliza exatamente **$1$ dia inclusivo**.

### 1.2. Fator de Emissão Ajustado ($FE_{\text{ajustado}}$)
Para cada período $i$, a taxa de emissão por cabeça por dia é multiplicada sem defaults mágicos:
$$FE_{\text{ajustado}, i} = FE_{\text{base\_dieta}, i} \times K_{\text{idade}, i} \times K_{\text{pastagem}, i} \times K_{\text{suplementacao}, i}$$

- Unidade de $FE_{\text{base\_dieta}}$: $\text{kg CO}_2\text{e} / \text{cabeça} / \text{dia}$.
- Unidade dos multiplicadores ($K$): adimensional ($1$).
- Unidade de $FE_{\text{ajustado}}$: $\text{kg CO}_2\text{e} / \text{cabeça} / \text{dia}$.

### 1.3. Emissão do Período ($E_i$) e Emissão Total ($E_{\text{total}}$)
$$E_i = \text{dias}_i \times \text{numero\_animais}_i \times FE_{\text{ajustado}, i} \quad [\text{kg CO}_2\text{e}]$$
$$E_{\text{total}} = \sum_{i=1}^{n} E_i \quad [\text{kg CO}_2\text{e}]$$

### 1.4. Massa Total de Carcaça ($M_{\text{carcaça}}$) e Intensidade de Emissões ($I$)
$$M_{\text{carcaça}} = N_{\text{abate}} \times P_{\text{médio\_kg}} \times R_{\text{carcaça}} \quad [\text{kg carcaça}]$$

$$I = \begin{cases} 
\dfrac{E_{\text{total}}}{M_{\text{carcaça}}} & \text{se } N_{\text{abate}} > 0 \land P_{\text{médio\_kg}} > 0 \land R_{\text{carcaça}} > 0 \\ 
\text{None} & \text{se qualquer termo do denominador for } \le 0 \text{ ou inválido (sem divisão por zero)}
\end{cases}$$

---

## 2. Tabela de Expected Results Versionada

| ID | Cenário | Entradas do Manejo | Entradas do Abate | Emissão Total Esperada ($\text{kg CO}_2\text{e}$) | Carcaça Total Esperada ($\text{kg}$) | Intensidade Esperada ($\text{kg CO}_2\text{e} / \text{kg carcaça}$) | Status / Comportamento |
|---|---|---|---|---|---|---|---|
| **EXP-01** | **Caso Base Sintético (P1 + P2)** | **P1:** 2026-01-01 a 2026-03-31 (90 dias), 50 cab, $FE_{\text{base}}=2.10$, $K=(1, 1, 1)$<br>**P2:** 2026-04-01 a 2026-05-30 (60 dias), 50 cab, $FE_{\text{base}}=1.40$, $K=(1, 1, 1)$ | $N=50$<br>$P=540\text{ kg}$<br>$R=0.53$ | **13.650**<br>*(P1: 9.450 + P2: 4.200)* | **14.310** | **$0.953878...$**<br>*(arredondamento visual: $0.954$)* | Aprovado (Referência MVP) |
| **EXP-02** | **Multiplicadores Compostos** | 2026-06-01 a 2026-06-10 (10 dias), 20 cab, $FE_{\text{base}}=2.50$, $K_{\text{id}}=1.20$, $K_{\text{pas}}=0.85$, $K_{\text{sup}}=1.10$ | $N=20$<br>$P=500\text{ kg}$<br>$R=0.50$ | **561**<br>*(FE aj.: 2.805)* | **5.000** | **0.1122** | Aprovado |
| **EXP-03** | **Manejo de Mesmo Dia** | 2026-07-15 a 2026-07-15 (1 dia), 30 cab, $FE_{\text{base}}=2.00$, $K=(1, 1, 1)$ | $N=30$<br>$P=600\text{ kg}$<br>$R=0.50$ | **60** | **9.000** | **$0.006666...$** | Aprovado ($1$ dia inclusivo) |
| **EXP-04** | **Ano Bissexto** | 2024-02-01 a 2024-02-29 (29 dias), 10 cab, $FE_{\text{base}}=1.00$, $K=(1, 1, 1)$ | $N=10$<br>$P=500\text{ kg}$<br>$R=0.50$ | **290** | **2.500** | **0.116** | Aprovado ($29$ dias fev/24) |
| **EXP-05** | **Zero Animais no Manejo** | 2026-01-01 a 2026-01-31 (31 dias), 0 cab, $FE_{\text{base}}=2.10$, $K=(1, 1, 1)$ | $N=50$<br>$P=540\text{ kg}$<br>$R=0.53$ | **0** | **14.310** | **0** | Aprovado (Emissão nula) |
| **EXP-06** | **Fator Base Zero** | 2026-01-01 a 2026-01-10 (10 dias), 100 cab, $FE_{\text{base}}=0$, $K=(1, 1, 1)$ | $N=100$<br>$P=500\text{ kg}$<br>$R=0.50$ | **0** | **25.000** | **0** | Aprovado |
| **EXP-07** | **Multiplicador Zero** | 2026-01-01 a 2026-01-15 (15 dias), 50 cab, $FE_{\text{base}}=2.10$, $K_{\text{sup}}=0$ | $N=50$<br>$P=500\text{ kg}$<br>$R=0.50$ | **0** | **12.500** | **0** | Aprovado |
| **EXP-08** | **Zero Animais no Abate** | 2026-01-01 a 2026-01-31 (31 dias), 50 cab, $FE_{\text{base}}=2.10$, $K=(1, 1, 1)$ | **$N=0$**<br>$P=540\text{ kg}$<br>$R=0.53$ | **3.255** | **0** | **None** | Denominador $0 \to$ sem divisão |
| **EXP-09** | **Peso Médio Zero** | 2026-01-01 a 2026-01-31 (31 dias), 50 cab, $FE_{\text{base}}=2.10$, $K=(1, 1, 1)$ | $N=50$<br>**$P=0\text{ kg}$**<br>$R=0.53$ | **3.255** | **0** | **None** | Denominador $0 \to$ sem divisão |
| **EXP-10** | **Rendimento Zero** | 2026-01-01 a 2026-01-31 (31 dias), 50 cab, $FE_{\text{base}}=2.10$, $K=(1, 1, 1)$ | $N=50$<br>$P=540\text{ kg}$<br>**$R=0$** | **3.255** | **0** | **None** | Denominador $0 \to$ sem divisão |
| **EXP-11** | **Animais Negativos no Manejo** | 2026-01-01 a 2026-01-10 (10 dias), **-5 cab**, $FE_{\text{base}}=2.10$ | N/A | N/A | N/A | N/A | `ErroCarbono`: Quantidade inválida |
| **EXP-12** | **Fator Negativo** | 2026-01-01 a 2026-01-10 (10 dias), 10 cab, **$FE_{\text{base}}=-0.01$** | N/A | N/A | N/A | N/A | `ErroCarbono`: Não pode ser negativo |
| **EXP-13** | **Multiplicador Negativo** | 2026-01-01 a 2026-01-10 (10 dias), 10 cab, **$K_{\text{idade}}=-1.0$** | N/A | N/A | N/A | N/A | `ErroCarbono`: Não pode ser negativo |
| **EXP-14** | **Data Invertida (Fim < Início)** | **2026-08-10 a 2026-08-09**, 10 cab, $FE_{\text{base}}=2.10$ | N/A | N/A | N/A | N/A | `ErroCarbono`: Datas inválidas |
| **EXP-15** | **Contaminação por Float** | 2026-01-01 a 2026-01-05 (5 dias), 10 cab, **$FE=2.10$ (float)** | N/A | N/A | N/A | N/A | `ErroCarbono`: Deve ser Decimal |
| **EXP-16** | **Decimal Não Finito (NaN/Inf)** | 2026-01-01 a 2026-01-05 (5 dias), 10 cab, **$FE=\text{Decimal('NaN')}$** | N/A | N/A | N/A | N/A | `ErroCarbono`: Deve ser Decimal finito |
| **EXP-17** | **Abate Negativo** | $E_{\text{total}}=13.650$ | **$N=-1$** ou **$P=-540$** ou **$R=-0.53$** | 13.650 | Negativo | **None** | Denominador $\le 0 \to$ None |
| **EXP-18** | **Emissão Negativa no Abate** | **$E_{\text{total}}=-100$** | $N=50$, $P=540$, $R=0.53$ | N/A | 14.310 | N/A | `ErroCarbono`: Não pode ser negativo |
| **EXP-19** | **Lista de Períodos Vazia** | `periodos = []` | N/A | N/A | N/A | N/A | `ErroCarbono`: Ao menos um período |
| **EXP-20** | **Alta Precisão (80 dígitos)** | 2026-01-01 a 2026-01-07 (7 dias), 13 cab, fatores com 20 casas decimais | $N=13$, $P=540$, $R=0.53$ | Idêntico à expansão analítica manual | $3.720,6$ | Exata sem arredondamento | Aprovado |

---

## 3. Cuidado de Engenharia: Diferenciação entre Validade Matemática e Validade Científica

> [!IMPORTANT]
> **DIRETRIZ DE GOVERNANÇA E TRANSPARÊNCIA:**
> A equipe do projeto AgroTracer estabelece a distinção explícita e obrigatória entre **Validade Matemática** e **Validade Científica** para todos os relatórios, auditorias e artefatos de código.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ARQUITETURA DE CÁLCULO AGROTRACER                     │
├─────────────────────────────────────────────┬───────────────────────────────┤
│             VALIDADE MATEMÁTICA             │      VALIDADE CIENTÍFICA      │
│          (Garantida pelo Motor)             │     (Governança de Dados)     │
├─────────────────────────────────────────────┼───────────────────────────────┤
│ • Aritmética determinística com Decimal     │ • Parâmetros e fatores de     │
│   em precisão estendida (80 dígitos).       │   emissão versionados e       │
│ • Ausência de arredondamento intermediário. │   rastreáveis.                │
│ • Reproduzibilidade exata bit a bit em      │ • Identificação clara da      │
│   qualquer plataforma de execução.          │   fonte regulatória (IPCC /   │
│ • Prevenção absoluta de divisão por zero    │   Embrapa / GHG Protocol).    │
│   (retorno explícito None).                 │ • Indicação de parâmetros     │
│ • Rejeição estrita de tipos contaminantes   │   SINTÉTICOS / DIDÁTICOS      │
│   (float IEEE-754, strings, NaN, Inf).      │   para testes de software.    │
│ • Comutatividade e associatividade exatas.  │ • Não constitui inventário    │
│                                             │   oficial de emissões.        │
└─────────────────────────────────────────────┴───────────────────────────────┘
```

### 3.1. O que é Validade Matemática (Escopo do CarbonEngine)
A **validade matemática** diz respeito à correção formal e exatidão dos algoritmos computacionais implementados:
1. **Determinismo Numérico:** O cálculo é uma função pura. Dadas as mesmas entradas (`data_inicio`, `data_fim`, `numero_animais`, `fatores`), o resultado é invariavelmente idêntico em qualquer ambiente de hardware ou sistema operacional.
2. **Imunidade a Erros de Ponto Flutuante:** Ponto flutuante binário (padrão IEEE-754 `float`) introduz ruídos como $0.1 + 0.2 = 0.30000000000000004$. O CarbonEngine rejeita terminantemente `float` e utiliza representação decimal exata via `decimal.Decimal`.
3. **Contabilização Temporal Inclusiva:** A fórmula $(Fim - Inicio) + 1$ reflete a integral de emissão biológica em que o primeiro e o último dia de pastejo/confinamento são integralmente contabilizados.
4. **Sem Divisão por Zero:** A função `calcular_intensidade` valida os três componentes do denominador ($N_{\text{abate}}$, $P_{\text{médio}}$ e $R_{\text{carcaça}}$). Caso o produto resulte em valor menor ou igual a zero, o cálculo é abortado de forma segura retornando `None`, impedindo `ZeroDivisionError`.

### 3.2. O que é Validade Científica (Escopo de Domínio e Governança)
A **validade científica** refere-se à representatividade agronômica e biológica dos fatores utilizados perante o ciclo de vida da pecuária:
1. **Fatores Sintéticos do MVP:** As cifras de referência do projeto (ex.: $FE_{\text{base}} = 2.10\text{ kg CO}_2\text{e}/\text{cab}/\text{dia}$ para confinamento, $1.40$ para pastagem e o resultado sintético de $13.650\text{ kg CO}_2\text{e}$ com intensidade $0.954\text{ kg CO}_2\text{e}/\text{kg carcaça}$) são **estritamente didáticas e sintéticas**. Elas foram calibradas exclusivamente para homologação funcional de software.
2. **Não Substituição de Metodologias Oficiais:** O sistema AgroTracer **NÃO** alega conformidade com o IPCC Guidelines for National Greenhouse Gas Inventories (Tier 2 ou Tier 3) nem com o Protocolo GHG Agropecuário até que conjuntos de parâmetros reais sejam chancelados por pesquisadores credenciados.
3. **Rastreabilidade de Fontes:** A arquitetura exige que fatores não sintéticos possuam `source_uri` e `source_type` registrados no banco de dados. Caso contrário, o carregamento do conjunto de parâmetros é rejeitado (`carregar_fatores_versionados`).

---

## 4. Matriz de Execução de Testes Automatizados

A suíte `backend/tests/test_s4_t05_casos_limite.py` executa **51 testes automatizados**, complementando os 11 testes de `test_s4_t01_carbon_engine.py`, totalizando **62 asserções de engenharia com 100% de sucesso**.

```
[TEST SUITE S4-T05]
├── 1. Tabela de Expected Results (test_expected_result_*)
│   ├── test_expected_result_caso_base_sintetico (13.650 kg CO2e / 0.954 intensidade) -> PASSED
│   └── test_expected_result_multiplicadores_combinados (561 kg CO2e) -> PASSED
├── 2. Casos Limite - Zero (test_zero_*)
│   ├── test_zero_animais_no_manejo (emissao = 0) -> PASSED
│   ├── test_zero_fator_emissao_base (emissao = 0) -> PASSED
│   ├── test_zero_multiplicador_zera_emissao (emissao = 0) -> PASSED
│   ├── test_zero_emissao_total_com_abate_valido (intensidade = 0) -> PASSED
│   └── test_zero_no_denominador_retorna_none_sem_divisao_por_zero [4 variações] -> PASSED
├── 3. Casos Limite - Negativos (test_negativo_*)
│   ├── test_negativo_animais_manejo_rejeitado (ErroCarbono) -> PASSED
│   ├── test_negativo_fatores_rejeitados [4 fatores] (ErroCarbono) -> PASSED
│   ├── test_negativo_emissao_total_em_intensidade (ErroCarbono) -> PASSED
│   └── test_negativo_parametros_abate_retornam_none [4 variações] (None) -> PASSED
├── 4. Casos Limite - Temporais (test_temporal_*)
│   ├── test_temporal_mesmo_dia_inclusivo (1 dia) -> PASSED
│   ├── test_temporal_fim_menor_que_inicio_rejeitado (ErroCarbono) -> PASSED
│   ├── test_temporal_ano_bissexto (29 dias) -> PASSED
│   ├── test_temporal_virada_de_ano (32 dias) -> PASSED
│   └── test_temporal_tipos_invalidos_rejeitados [5 variações] (ErroCarbono) -> PASSED
├── 5. Casos Limite - Tipos e Floats (test_float_* / test_decimal_* / test_tipo_*)
│   ├── test_lista_vazia_de_periodos_rejeitada (ErroCarbono) -> PASSED
│   ├── test_float_em_fator_rejeitado (ErroCarbono) -> PASSED
│   ├── test_decimal_nao_finito_rejeitado [NaN, +Inf, -Inf] -> PASSED
│   ├── test_tipo_invalido_numero_animais_manejo [4 variações] -> PASSED
│   ├── test_tipo_invalido_animais_abate_intensidade [3 variações] -> PASSED
│   ├── test_peso_ou_rendimento_nao_decimal_lanca_erro [4 variações] -> PASSED
│   └── test_identificacao_fatores_invalida [4 variações] -> PASSED
└── 6. Casos Limite - Precisão e Comutatividade
    ├── test_alta_precisao_analitica_sem_arredondamento (80 casas decimais) -> PASSED
    └── test_comutatividade_multiplicadores -> PASSED
```
