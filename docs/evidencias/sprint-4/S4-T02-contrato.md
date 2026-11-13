# S4-T02 — Fechamento do lote

POST /api/v1/lotes/{lote_id}/fechamento, HMAC WordPress e RN-19.

Payload JSON exemplo:
```json
{
  "data_abate": "2026-12-31",
  "numero_animais_abate": 50,
  "peso_medio_abate_kg": "540",
  "rendimento_carcaca": "0.53"
}
```

- Fechamento exige lote EM_MANEJO (RN-04), manejo, conjunto publicado e
  vigencia compatível, animais com historico completo em cada periodo e
  numero abatido dentro da quantidade observada no ultimo manejo.
- Para evitar dupla contagem, mudancas de associacao durante um manejo
  exigem dividir o manejo em periodos alinhados antes de fechar.
- Fatores FE_BASE_DIETA:<TIPO_DIETA>, K_IDADE, K_PASTAGEM,
  K_SUPLEMENTACAO devem existir no mesmo parametro_set_id.
- Contrato atualmente suporta exatamente um parametro_set_id por
  fechamento; regra explicitada para revisao e futura ampliacao.
- Datas de associacao em TIMESTAMPTZ sao interpretadas em UTC.
- Dados de abate invalidos -> 422 (nao certificado); lote fechado -> 409.
- Auditoria e dados de fechamento no mesmo commit; erro desfaz tudo.
- Nenhuma rota de certificado e acionada no fechamento.

**Dependencia S4-T03:** este PR e preparatorio. O snapshot deve ser
gravado na mesma transacao antes de homologar o fluxo de fechamento.

QA: testar PostgreSQL, rollback por falha de auditoria e concorrencia,
e validar o tratamento de datas/timezones com Nadiny.
