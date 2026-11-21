# Relatório de UAT e Hardening — S6-T05

## 1. Resumo da Execução
* **Objetivo:** Validar a resiliência da aplicação contra falhas operacionais, entradas extremas e uso real sem assistência técnica.
* **Automação de API (`pytest`):** 6/6 casos aprovados (`docs/evidencias/sprint-6/S6-T05-testes.txt`).
* **Validação Manual (UAT):** Executada nos fluxos principais de Fazendas, Lotes e Certificados.
* **Bugs Bloqueantes (P1/P2):** 0 em aberto.

## 2. Matriz dos 5 Vetores de Resiliência
| Vetor | Camada | Critério de Aceite | Evidência | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1. Clique Duplo** | API + UI | Bloqueio de replay HMAC (`401`) no backend e desabilitação do botão de envio durante requisição | `test_uat_clique_duplo_idempotencia_nonce_hmac` + UI (`agrotracer-screens.js`) | ✅ |
| **2. Refresh (`F5`)** | UI / Estado | Recarregamento durante preenchimento e pós-envio sem tela branca, erro `500` ou duplicidade | Validação no navegador | ✅ |
| **3. Sessão Expirada** | API + UI | Rejeição com `401` e contrato de erro limpo na API; mensagem segura e bloqueio de sessão expirada na UI WordPress | `test_uat_sessao_expirada_ou_sem_assinatura_retorna_401` + `class-agrotracer-http-client.php` | ✅ |
| **4. Dados Extremos** | API + UI | Datas invertidas, strings >2.500 chars, IDs negativos e payloads XSS/SQLi sem erro `500` (rejeição controlada `400/422` ou persistência literal segura) | `test_uat_dados_extremos_nao_geram_erro_500` (4 casos parametrizados) | ✅ |
| **5. Acessibilidade** | UI / Teclado | Fluxo completo navegável via teclado (`Tab`, `Shift+Tab`, `Enter`, `Esc`) com atributos `aria-*` e foco visível | Validação manual sem mouse | ✅ |

## 3. Cenários de Aceitação (BDD)
**Cenário 1: Integridade de operação sob requisições concorrentes ou duplicadas**
* **Dado** que um produtor autenticado inicia o registro de uma movimentação no sistema
* **Quando** ocorre uma tentativa de submissão duplicada em curto intervalo
* **Então** o sistema impede o processamento redundante e mantém a consistência dos dados

**Cenário 2: Tratamento seguro de entradas fora do padrão**
* **Dado** que uma requisição contém dados acima do limite, datas invertidas ou caracteres potencialmente maliciosos
* **Quando** a camada de validação processa a entrada
* **Então** a operação não gera erro interno (`500`) e rejeita entradas inválidas de forma controlada (`400`/`422`)

## 4. Parecer da Revisão e UAT
* **Autora da entrega:** Nadiny Martins (`feature/S6-T05-uat-hardening`)
* **Revisão técnica e ajustes de CI:** João Vitor Santos de Souza (`LoselSpt`) no PR #50
* **Roteiro executado:** Cadastro/consulta de fazenda, lançamento de manejo em lote e emissão/consulta de certificado.
* **Observações de UX / Melhorias (P3/P4):** Registrar no Jira caso um avaliador externo fora da equipe emita observações adicionais de UAT.
