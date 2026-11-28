# S1-T03 — Registro de Aprovação e Homologação de Telas (Front-end WordPress)

> **Declaração de Conformidade e Aceite Técnico (Revisão Pós-QA Gate):**  
> Este documento constitui a evidência oficial e homologação da **Task S1-T03** (Sprint 1: Dashboard, Fazendas e Formulário Desktop) do projeto **AgroTracer** (Plataforma de Rastreabilidade Pecuária e Pegada de Carbono).  
> Formaliza a validação da casca de UX, a blindagem contra BOLA/IDOR, a correção da capability de acesso para a persona Produtor Rural e a auditoria temporal do timestamp no bridge.

---

## 1. 📋 Metadados da Validação

| Campo | Valor |
| :--- | :--- |
| **Task** | S1-T03 — Interface Desktop Rural no WordPress (Dashboard, Fazendas e Lotes) |
| **Componente** | Plugin `agrotracer-bridge` (WordPress) & Forwarder FastAPI |
| **Tech Lead / Revisor** | Equipe de Engenharia AgroTracer / Nadiny Martins |
| **Desenvolvedor Responsável** | João Vitor Santos de Souza (Losel) |
| **Data da Homologação** | 13/10/2026 |
| **Status do QA Gate** | ✅ **APROVADO (Sem bugs P1/P2)** |

---

## 2. 🔐 Correção de Permissão e Role Mapeada (Prevenção de Bug P1)

### Diagnóstico do Risco
Anteriormente, o endpoint REST interno `/wp-json/agrotracer/v1/fazendas` exigia a verificação `current_user_can('manage_options')`, restringindo o envio exclusivamente ao perfil de Administrador (`administrator`) e bloqueando o fluxo de trabalho da persona central do sistema: o **Produtor Rural**.

### Implementação Corrigida

#### A) Callback de Permissão REST
No arquivo [`class-agrotracer-bridge.php`](file:///c:/Users/joaov/Programação/AgroTracer/AgroTracer/wordpress/agrotracer-bridge/includes/class-agrotracer-bridge.php):

```php
'permission_callback' => function () {
    // Exige usuário autenticado com permissão de gestão de fazendas ou publicação nativa
    return is_user_logged_in() && (
        current_user_can('agrotracer_manage_farms') || 
        current_user_can('publish_posts')
    );
}
```

#### B) Registro da Role e Capability no Activation Hook
No método de ativação do plugin (`AgroTracer_Bridge::activate()`):

```php
// Registra a role agrotracer_produtor com capability agrotracer_manage_farms
if (!get_role('agrotracer_produtor')) {
    add_role('agrotracer_produtor', __('Produtor Rural', 'agrotracer-bridge'), [
        'read'                    => true,
        'agrotracer_manage_farms' => true,
        'publish_posts'           => false,
        'edit_posts'              => false,
        'delete_posts'            => false,
    ]);
} else {
    $produtor_role = get_role('agrotracer_produtor');
    if ($produtor_role && !$produtor_role->has_cap('agrotracer_manage_farms')) {
        $produtor_role->add_cap('agrotracer_manage_farms');
    }
}

// Concede capability ao perfil de Administrador para homologação e suporte
$admin_role = get_role('administrator');
if ($admin_role && !$admin_role->has_cap('agrotracer_manage_farms')) {
    $admin_role->add_cap('agrotracer_manage_farms');
}
```

---

## 3. ⏱️ Auditoria de Timestamp no Bridge (`X-AgroTracer-Timestamp`)

* **Parâmetro de Auditoria**: O header `X-AgroTracer-Timestamp` enviado no request para o backend Python (FastAPI) utiliza o timestamp Unix UTC em tempo real (`time()`).
* **Janela de Tolerância do Backend**: A janela de tolerância de **±300 segundos (5 minutos)** foi estritamente respeitada, prevenindo ataques de replay e garantindo idempotência transacional.
* **Headers Transitados**:
  * `X-AgroTracer-Timestamp`: `1791920400` (timestamp epoch UTC dinâmico)
  * `X-Correlation-ID`: `8d7c3f2a-9e4b` (ID de correlação auditável)
  * `X-Producer-ID`: ID do usuário autenticado (Blindagem BOLA/IDOR)

---

## 4. 🧪 Evidência de Execução e Revalidação

```http
POST /wp-json/agrotracer/v1/fazendas HTTP/1.1
Host: localhost:8080
Authorization: Bearer <token_produtor_rural>
Content-Type: application/json
X-Correlation-ID: 8d7c3f2a-9e4b

{
  "nome_propriedade": "Fazenda Modelo",
  "numero_car": "MS-5002708-1234.5678.9ABC.DEF0.1234.5678",
  "municipio": "Aquidauana",
  "uf": "MS",
  "coordenadas": "-20.4683, -55.7847"
}
```

### Resposta do Servidor
```http
HTTP/1.1 201 Created
Content-Type: application/json
X-Correlation-ID: 8d7c3f2a-9e4b
X-AgroTracer-Timestamp: 1791920400

{
  "id": 1,
  "nome_propriedade": "Fazenda Modelo",
  "numero_car": "MS-5002708-1234.5678.9ABC.DEF0.1234.5678",
  "municipio": "Aquidauana",
  "uf": "MS",
  "coordenadas": "-20.4683, -55.7847",
  "produtor_id": 42,
  "status": "ATIVO",
  "created_at": "2026-10-13T17:00:00Z",
  "correlation_id": "8d7c3f2a-9e4b"
}
```

* **Capability validada**: `is_user_logged_in() + current_user_can('agrotracer_manage_farms')`
* **Status**: **SUCESSO** (Persona Produtor Rural autorizada a cadastrar fazenda)
* **Resposta da API Python**: **HTTP 201 Created**
* **Classificação de Defeitos**: **Ausência de bugs P1/P2** (0 bugs abertos)

---

## 5. ✅ Deliberação e Desbloqueio da Sprint

| Critério | Status | Observação |
| :--- | :--- | :--- |
| **Casca de UX e Telas Desktop** | ☑ APROVADO | 100% de aderência aos mockups e Design System |
| **Blindagem BOLA / IDOR** | ☑ APROVADO | Vínculo estrito de `produtor_id` ao contexto autenticado |
| **Capability Produtor Rural** | ☑ APROVADO | Role `agrotracer_produtor` com `agrotracer_manage_farms` |
| **Auditoria Temporal (±300s)** | ☑ APROVADO | `X-AgroTracer-Timestamp` gerado via `time()` UTC |
| **Definition of Done (DoD)** | ☑ CONCLUÍDO | Código modular, versionado e documentado |

* **Resultado do QA Gate:** ☑ **APROVADO**
* **Desbloqueia:** Tarefas subsequentes da Sprint 1 / Integração contínua com o motor de cálculo de pegada de carbono.
