# Banca — roteiro de 10 minutos e plano B

Custódia: Samela (Product Owner); FastAPI/DB/secrets: Samela;
WordPress/Bridge/proxy: João Vitor. QA: Nadiny.
Fonte: [AG-111](https://losel.atlassian.net/browse/AG-111).
Este roteiro prepara o ensaio; não comprova sua execução pela equipe.

## Preparação antes de iniciar o cronômetro

1. Registrar commit com `git rev-parse HEAD` e confirmar CI do candidato.
2. Executar `python tools/demo.py up`, `python tools/demo.py verify` e
   `python tools/release_check.py`. Docker deve estar disponível.
3. Abrir o [manual](manual-usuario.md) e entrar no WordPress local. Acesso e
   token ficam somente em `.demo/acesso.json`; não projetar esse arquivo.
4. Conferir os dois estados do plano B: `S7-DEMO-PARA-EMITIR` ainda em
   manejo, pronto para emissão, e `S7-DEMO-CERTIFICADO` com certificado
   emitido. Não consumir o lote de reserva durante a preparação.
5. Baixar previamente o PDF do certificado emitido, conferir seu SHA-256
   com `pdf_sha256` do acesso privado e abrir a consulta pública. Guardar o
   PDF sintético localmente, sem incluir credenciais ou tokens nos registros.
6. Manter preview desligado. Listagens de animais, parâmetros e histórico
   de fechamentos têm limitação 503 descrita na [LIM-01](../evidencias/sprint-7/S7-T03.md).
   Se a UI impedir o percurso, registrar a ocorrência; não chamar mock de integração.

## Sequência cronometrada (meta 10 min; aceite 8–12 min)

| Tempo | Apresentação / ação | Evidência e responsável sugerido |
| --- | --- | --- |
| 0:00–1:00 | Problema, rastreabilidade por lote e limites do MVP | Samela: fatores SYNTHETIC, sem alegação de laudo ambiental |
| 1:00–2:00 | Arquitetura WP → Bridge HMAC → FastAPI → PostgreSQL; Redis | João: fronteira pública/privada e segredo só no servidor |
| 2:00–3:30 | Login, fazenda e lote; vínculo de animais e histórico | Manual; diferenciar dados persistidos e limitações de listagem |
| 3:30–5:00 | Manejo, parâmetros versionados e continuidade temporal | Samela: RN-08; fatores e proveniência do seed |
| 5:00–7:00 | Emissão atômica, snapshot e PDF | Usar lote de demonstração; dados de abate abaixo |
| 7:00–8:30 | Consulta pública/QR, hashes e privacidade | DTO público, sem login; PDF privado com autorização |
| 8:30–10:00 | CI, restore, limitações e conclusão | QA consolidado; registrar perguntas e respostas |

Dados do seed para emissão: data `2026-02-02`, quantidade `1`, peso médio
`540 kg`, rendimento `0.53`. Confirmar o ID do lote no ambiente, nunca fixá-lo
a partir de outro computador. Token é devolvido uma única vez; guardar em
local privado. Repetir emissão não é operação de desfazer.

## Plano B por tipo de falha

- Falha no cadastro/manejo: usar o lote previamente pronto, sem alterar
  fatores/datas para contornar validações. Explicar o ponto de retomada.
- Falha na emissão: abrir o certificado previamente emitido e o PDF já
  verificado; não repetir cliques, não habilitar preview e não gerar sucesso fictício.
- API/WordPress indisponível: apresentar o PDF local e as evidências de CI
  com commit/data; declarar que se trata de registro prévio, sem afirmar
  consulta online. Screenshots de Sprint 6 são históricos, não prova do candidato.
- Falha de rede no QR: abrir a consulta já verificada se disponível; caso
  contrário, mostrar o resultado registrado e anotar a indisponibilidade.
- Lote de reserva já consumido: preparar outro lote pelo fluxo normal antes
  do ensaio seguinte. `demo.py up` é idempotente e não repõe lotes consumidos.
  Não apagar volumes nem banco para reiniciar uma apresentação.

## Perguntas técnicas para ensaiar

| Pergunta | Resposta e referência verificável |
| --- | --- |
| Por que HMAC? | Bridge assina método/caminho/tempo/nonce/ator/hash do corpo; API valida integridade e janela, Redis evita replay. Ver `backend/app/core/bridge_auth.py`. Não substitui TLS. |
| Como impedir acesso a lote de outro produtor? | Autorização por posse no backend, além da assinatura; testes BOLA em `test_s6_t02_hardening.py`. |
| O que acontece no clique duplo? | UI bloqueia reenvio; backend valida idempotência/transação. Conflitos são explícitos, não novo certificado silencioso. |
| Os números são científicos? | Cálculo determinístico com Decimal, fatores versionados SYNTHETIC. Não é laudo ou certificação ambiental independente. |
| Hash garante veracidade? | Hash detecta alteração dos bytes/snapshot; não comprova a verdade dos dados de entrada. |
| Por que guardar hash do token? | Token opaco é mostrado na emissão; banco guarda hash. Consulta pública minimiza dados e aplica rate limit. |
| Como recuperar o sistema? | Procedimento e ensaio de restore em `docs/evidencias/sprint-6/S6-T06-requisitos.md`; tempo medido é de laboratório, não SLA de produção. |
| O que ainda não funciona? | Declarar LIM-01 a LIM-05 do QA; não esconder 503 nem apresentar preview como persistência real. |

## Registro obrigatório dos dois ensaios

Preencher [ensaios.json](../evidencias/sprint-7/ensaios.json) com fatos reais:
commit completo, data, participantes, duração em segundos, etapas concluídas,
plano B exercitado, perguntas/respostas e referências aos registros sem segredos.
Cada ensaio deve cobrir apresentação e perguntas técnicas; registrar separadamente
o tempo de perguntas. Resultado incompleto ou fora de 480–720 segundos exige
novo ensaio. QA/review de outro integrante continua necessário.
