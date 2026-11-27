# Manual do Usuário — AgroTracer (Fluxo Completo)

Este manual guia qualquer operador do início ao fim no fluxo completo do **AgroTracer** (do login à emissão e verificação pública de certificado), sem necessidade de apoio técnico adicional.

> **Aviso de proveniência:** os parâmetros e fatores utilizados na demonstração são **SYNTHETIC** (didáticos) e não representam inventário oficial de emissões ou certificação ambiental independente.

---

## 1. Acesso ao Sistema

1. Se estiver usando a demo local (`python tools/demo.py up`), abra `.demo/acesso.json` e anote o usuário e a senha gerados.
2. Acesse `http://127.0.0.1:18080/agrotracer/` (ou a URL do ambiente WordPress configurado).
3. Faça login com a conta de produtor (`agrotracer_manage_farms`).
4. Após autenticado, o sistema abre a tela **Dashboard** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-dashboard.png`).

---

## 2. Cadastro de Fazendas

1. No menu superior, clique em **Fazendas** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-fazendas.png`).
2. Clique em **Nova Fazenda** e preencha **Nome**, **Município** e **UF** (2 letras).
3. Confirme o salvamento. A fazenda passa a aparecer na listagem e fica disponível para vincular lotes.

*(Na demo limpa, a fazenda `Fazenda SYNTHETIC S7` com o talhão `DEMO-PASTO` já vem pré-cadastrada.)*

---

## 3. Lotes e Animais

1. No menu superior, clique em **Lotes e Animais** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-lotes.png`).
2. Na aba **Lotes de Manejo**:
   - Clique em **Novo Lote**, selecione a **Fazenda**, informe o **Código do Lote** e salve.
3. Na aba **Animais** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-animais.png`):
   - Cadastre os animais com identificador único e associe-os ao lote desejado.
   - Um lote só pode ser fechado se possuir animais associados e ao menos um manejo registrado.

---

## 4. Manejo Nutricional (Timeline)

1. No menu superior, clique em **Manejo** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-manejo.png`).
2. Selecione o **Lote** no seletor superior.
3. Clique em **Registrar Manejo** e informe:
   - **Data de início** e **Data de fim** (sem sobreposição com outro período já registrado para o mesmo lote);
   - **Tipo de dieta** (ex.: `PASTAGEM`);
   - **Conjunto de parâmetros** ativo (ex.: `S7-DEMO-SYNTHETIC-1`).
4. Salve o registro. A timeline exibirá o período em ordem cronológica.

---

## 5. Fechamento do Lote e Emissão de Certificado

1. No menu superior, clique em **Fechamento** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-fechamento.png`).
2. Selecione o lote em manejo (na demo local, utilize o lote **`S7-DEMO-PARA-EMITIR`**).
3. Preencha os dados de abate:
   - **Data do abate** (ex.: `2026-02-02`)
   - **Número de animais abatidos** (ex.: `1`, não superior ao total do lote)
   - **Peso médio de abate (kg)** (ex.: `540`)
   - **Rendimento de carcaça** (ex.: `0.53`)
4. Clique em **Fechar Lote e Emitir Certificado** e confirme os dados no modal.
5. **Atenção:** o **token público de verificação** é exibido **uma única vez** no resultado da emissão. Copie e guarde esse token com segurança (ele não pode ser recuperado depois em texto claro).

---

## 6. Certificados e Download de PDF

1. No menu superior, clique em **Certificados** (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-certificados.png`).
2. Localize o certificado emitido (na demo local, também há o certificado pré-emitido do lote `S7-DEMO-CERTIFICADO`).
3. Clique em **Baixar PDF** para obter o documento oficial do certificado. A integridade do arquivo é garantida pelo cabeçalho/campo `pdf_sha256`.

---

## 7. Consulta Pública (Sem Login)

1. Acesse a página pública `/certificado/` (ex.: `http://127.0.0.1:18080/certificado/`), acessível sem autenticação (`docs/evidencias/sprint-6/screenshots/chrome-1920x1080-publico.png`).
2. Informe o **Token do Certificado** (ou leia o **QR Code** do PDF emitido) e clique em **Verificar**.
3. A tela exibirá os dados públicos minimizados: status (`VALIDO`), método e parâmetros (`SYNTHETIC`), dados do abate, emissões calculadas, `snapshot_sha256` e `pdf_sha256`, sem expor dados privados do produtor.

---

## Referências Visuais Atuais

Screenshots capturados em 1366x768 e 1920x1080 (Chrome e Edge) disponíveis em:
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-dashboard.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-fazendas.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-lotes.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-animais.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-manejo.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-fechamento.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-certificados.png`
- `docs/evidencias/sprint-6/screenshots/chrome-1920x1080-publico.png`
