# S3-T06 — Proveniência dos dados de demonstração

Revisão do repositório local em 2026-11-07, incluindo backend, migrations,
testes, documentação textual e as duas distribuições WordPress/preview.

## Resultado da revisão

- Os fatores 2.10 usados pelos testes S3-T02 já eram SYNTHETIC.
- Ocorrências IPCC/EMBRAPA no backend são opções do esquema de proveniência
  e testes negativos de fonte sem URI; não atribuem esses valores às entidades.
- O ADR S3-T02 já proíbe atribuição institucional de valores sintéticos.
- O dashboard contém o número fixo 13.650, sem cálculo ligado ao backend.
  Ele é ilustração visual, não resultado do fator 2.10 nem inventário real.
- Não havia arquivo canônico de fatores demo. Foi adicionado
  `backend/examples/parametros_demo.json`: versão DEMO-SYNTHETIC-2026-01,
  RASCUNHO, valor Decimal textual, source_type SYNTHETIC, source_uri null.
  Não há aprovador, aprovação científica ou referência institucional fictícia.
- Os avisos dos dois templates PHP e do preview agora identificam explicitamente
  os dados sintéticos e a ausência de inventário real. A classificação também
  aparece em `data-source-type="SYNTHETIC"`.

## Uso e limites

O JSON é um exemplo testado, não uma migration ou seed automático. Nenhum
conjunto foi ativado ou reclassificado no banco por esta tarefa. Uma futura
importação deve usar os serviços auditados da S3-T02, com ator e justificativa,
e preservar a imutabilidade de versões publicadas. Aprovação administrativa
de demonstração não equivale a validação científica.

O fator 2.10 foi escolhido exclusivamente como valor didático já usado nos
testes. Não é recomendado para estimativas reais, inventários ou certificados.
Uma fonte não sintética exige referência verificável e revisão humana;
preencher source_uri sozinho não comprova a origem científica do número.

## Evidências reproduzíveis

- `test_s3_t06_demo.py` verifica classificação, ausência de atribuição,
  estado de rascunho e validade do exemplo perante o validador de fatores.
- `test_s3_t03_api.py` carrega o JSON real e verifica que a consulta retorna
  SYNTHETIC, source_uri null e Decimal textual.
- Busca textual usada: `git grep -n -i -E 'ipcc|embrapa|fator.*oficial'`.
- Suíte local final: `python -m pytest -q -k "not test_s1_t01_postgresql"`:
  **172 passed, 1 deselected, 1 warning**, em PostgreSQL de testes + SQLite.
  A exclusão S1-T01 e o warning Starlette/httpx são herdados da base.
- `python -m flake8 app tests`: sem erros.
- `php -l` nos dois templates dashboard.php: sem erros de sintaxe.

Escopo não validado: dados de produção, documentos externos ao repositório,
imagens de evidências históricas e homologação visual em WordPress instalado.
Revisão por integrante da equipe e QA Gate seguem pendentes.
