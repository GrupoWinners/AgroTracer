# ADR-002 — Autenticação e Segurança da Bridge

- **Projeto:** AgroTracer
- **Sprint:** 0
- **Task:** S0-T06 — Protocolo HMAC, envelope de erro e correlation_id
- **Status:** Proposto — aguardando revisão e aprovação da equipe

## 1. Contexto

O AgroTracer utiliza WordPress como interface e FastAPI como backend.

A comunicação entre WordPress e FastAPI precisa garantir a autenticidade das requisições, a integridade dos dados transmitidos e a proteção contra ataques de repetição.

Foi definido o protocolo HMAC-SHA256 com chave secreta compartilhada exclusivamente entre os servidores.

## 2. Decisão arquitetural

A camada PHP do WordPress será responsável por gerar a assinatura HMAC-SHA256. O backend FastAPI será responsável por verificar a assinatura, validar o timestamp e impedir a reutilização dos nonces.

O protocolo utilizará os seguintes headers:

| Header | Finalidade |
|---|---|
| X-AgroTracer-Signature | Assinatura HMAC-SHA256 em hexadecimal minúsculo |
| X-AgroTracer-Timestamp | Unix timestamp UTC, em segundos |
| X-AgroTracer-Nonce | Token aleatório de 16 bytes, representado por 32 caracteres hexadecimais |
| X-AgroTracer-User-Id | ID do usuário autenticado no WordPress, ou 0 para requisições de sistema autorizadas |
| X-Correlation-ID | Identificador UUID v4 para rastreamento |

O ID do usuário deverá ser obtido no servidor WordPress, nunca confiando diretamente em um valor fornecido pelo navegador.

A identidade será protegida pela assinatura HMAC. A autorização para executar cada operação continuará sendo responsabilidade do sistema.

## 3. Canonical string

A assinatura será calculada sobre os campos na seguinte ordem:

```text
METHOD
PATH_WITH_QUERY
TIMESTAMP
NONCE
WP_USER_ID
SHA256_BODY
```

Os campos serão separados por `\n`, sem quebra de linha adicional ao final. A canonical string será convertida em bytes UTF-8.

O método HTTP deverá ser escrito em maiúsculas.

O corpo será utilizado em seus bytes originais. Seu hash SHA-256 será representado em hexadecimal minúsculo.

Para requisições sem corpo, será utilizado o SHA-256 da sequência vazia:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

Os parâmetros da query string serão ordenados alfabeticamente pela chave e codificados segundo a RFC 3986.

**Pendente de confirmação entre PHP e Python:** representação dos caminhos codificados, parâmetros repetidos, espaços, caracteres especiais e entradas inválidas. Esses casos deverão possuir vetores de teste compartilhados antes da aprovação definitiva.

## 4. Assinatura e chave secreta

O algoritmo adotado será HMAC-SHA256.

A variável de ambiente `AGROTRACER_BRIDGE_SECRET` armazenará a chave secreta compartilhada.

A chave deverá ser gerada por um mecanismo criptograficamente seguro e disponibilizada apenas aos servidores autorizados.

O contrato utilizará os bytes ASCII da chave configurada. O segredo não poderá aparecer no navegador, nos logs ou no repositório.

A comparação das assinaturas utilizará `hmac.compare_digest()` no Python.

A comunicação em produção deverá utilizar HTTPS com verificação válida do certificado TLS.

## 5. Timestamp e proteção anti-replay

O FastAPI aceitará timestamps dentro de uma tolerância de ±300 segundos em relação ao horário UTC do servidor.

O nonce deverá conter pelo menos 128 bits aleatórios, gerados com fonte criptograficamente segura e independente do nonce nativo do WordPress.

Após verificar a assinatura HMAC, o backend registrará o nonce no Redis por **660 segundos**.

A operação deverá ser atômica, utilizando `SET NX EX 660`.

Uma segunda tentativa de utilizar o mesmo nonce durante a janela de retenção será rejeitada.

Se o Redis estiver indisponível, a autenticação falhará de forma segura e a operação protegida não será executada.

### Justificativa do ajuste

Durante a revisão de segurança, foi identificado que o TTL original de 600 segundos poderia expirar enquanto uma requisição ainda estivesse dentro da janela temporal permitida de ±300 segundos.

Para evitar essa possibilidade de reutilização, foi proposta a ampliação do TTL para 660 segundos, acrescentando uma margem de segurança de 60 segundos.

A correção foi implementada no backend Python e validada por testes automatizados.

**Status do ajuste:** proposta aguardando aprovação da equipe e atualização definitiva do protocolo.

## 6. Envelope de erro

As falhas de autenticação utilizarão um envelope JSON padronizado:

```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_REQUEST",
    "message": "Não foi possível autenticar a requisição.",
    "correlation_id": "123e4567-e89b-42d3-a456-426614174000",
    "timestamp": "2026-10-16T21:42:00Z"
  }
}
```

O código HTTP 401 será utilizado para falhas de autenticação.

O código HTTP 503 será utilizado quando um serviço indispensável à autenticação estiver indisponível.

Os códigos atualmente implementados incluem `AUTH_INVALID_REQUEST` e `AUTH_SERVICE_UNAVAILABLE`.

O catálogo definitivo de erros, inclusive a utilização de `AUTH_INVALID_SIGNATURE`, deverá ser confirmado entre os desenvolvedores.

## 7. Correlation ID

O sistema utilizará UUID v4 no header `X-Correlation-ID`.

O FastAPI preservará um identificador válido recebido e gerará um novo quando estiver ausente ou inválido.

O identificador será retornado no header de resposta e no envelope de erro.

O correlation ID será utilizado exclusivamente para rastreamento e não como credencial de autenticação.

## 8. Testes e validação

A implementação Python possui testes automatizados para construção da canonical string, assinatura HMAC, timestamp, headers, proteção anti-replay, indisponibilidade do Redis e tratamento de erros.

Antes da aprovação deste ADR deverão ser verificados os casos especiais de canonicalização, a compatibilidade entre PHP e Python e a proteção efetiva das rotas de negócio.

As evidências serão registradas em `docs/evidencias/sprint-0/`.

## 9. Critérios para aprovação

A decisão será considerada concluída após a validação conjunta entre WordPress e FastAPI, execução dos testes e CI, revisão por outro integrante, validação de QA e ausência de problemas críticos ou altos pendentes relacionados ao protocolo.

O Pull Request deverá permanecer em Draft até que esses critérios sejam atendidos.
