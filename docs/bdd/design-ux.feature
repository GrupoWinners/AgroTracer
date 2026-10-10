# language: pt
Funcionalidade: Padronização de Design System, Feedback e Tolerância a Erros na Interface

  Cenário: Exibição de Alerta de Conflito de Associação (Erro de Validação)
    Dado que o utilizador está na tela de "Lotes e Animais"
    Quando tentar associar um animal que já está associado ativamente a outro lote
    Então o sistema deve exibir um Modal de Erro com estilo semântico "danger"
    E a mensagem deve informar "Erro de Validação: Animal já possui associação ativa em outro lote"
    E a ação principal deve bloquear o avanço até que o conflito seja resolvido

  Cenário: Notificação de Sucesso ao Atualizar Cadastro
    Dado que o utilizador alterou as informações de uma fazenda
    Quando clicar em "Salvar Alterações" e a API responder com sucesso
    Então o sistema deve exibir um Toast com estilo semântico "success"
    E a mensagem deve exibir "Fazenda atualizada com sucesso!" juntamente com o id de correlação (Correlation ID)

  Cenário: Prevenção de Sobreposição de Manejo Nutricional (Aviso/Atenção)
    Dado que o lote "LT-2026-001" possui manejo registrado para o período atual
    Quando o utilizador tentar cadastrar um novo manejo com datas sobrepostas
    Então o campo de data deve apresentar contorno com estilo semântico "warning" e mensagem inline "Existe sobreposição com um manejo já registrado"
    E o botão de envio deve permanecer desabilitado enquanto houver conflito temporal

  Cenário: Idempotência e Prevenção de Clique Duplo na Certificação
    Dado que o utilizador preencheu os dados de fechamento do lote
    Quando clicar no botão "Emitir Certificado"
    Então o botão deve entrar em estado "loading" e ficar desabilitado para prevenir cliques duplos
    E deve enviar a chave "Idempotency-Key" garantindo a geração de apenas um certificado único por transação

  Cenário: Visualização Pública de Certificado via QR Code (DTO Minimizado)
    Dado que um visitante acesse o token público do certificado
    Quando a tela de consulta pública for carregada
    Então os badges de status de pegada de carbono devem seguir os estilos semânticos ("success" para Válido, "danger" para Invalidados)
    E NENHUM dado pessoal do produtor (CPF/CNPJ, e-mail ou telefone) deve ser exibido na interface