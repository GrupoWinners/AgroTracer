# language: pt
Funcionalidade: Padronização de Design System, Feedback e Tolerância a Erros na Interface

  Cenário: Exibição de Alerta de Conflito de Associação (Erro/Validação)
    Dado que o usuário está na tela de "Lotes e Animais"
    Quando tentar associar um animal que já está associado ativamente a outro lote
    Então o sistema deve exibir um Modal/Toast de Erro com cor de fundo "#FEE2E2" e borda/ícone "#EF4444"
    E a mensagem deve informar "Erro de Validação: Animal já possui associação ativa em outro lote"
    E a ação principal deve bloquear o avanço até que o conflito seja resolvido

  Cenário: Notificação de Sucesso ao Atualizar Cadastro
    Dado que o usuário alterou as informações de uma fazenda
    Quando clicar em "Salvar Alterações" e a API responder com status 200/201
    Então o sistema deve exibir um Toast de Sucesso no canto inferior esquerdo com fundo "#D1FAE5" e texto "#065F46"
    E a mensagem deve exibir "Fazenda atualizada com sucesso!" juntamente com o ID da requisição (Correlation ID)

  Cenário: Prevenção de Sobreposição de Manejo Nutricional (Aviso/Atenção)
    Dado que o lote "LT-2026-001" possui manejo registrado de 01/06/2026 a 30/06/2026
    Quando o usuário tentar cadastrar um novo manejo para o período de 15/06/2026 a 15/07/2026
    Então o campo de data deve apresentar contorno vermelho com mensagem de erro inline "Existe sobreposição com um manejo já registrado"
    E o botão de envio deve permanecer desabilitado enquanto houver conflito temporal

  Cenário: Idempotência e Prevenção de Clique Duplo na Certificação
    Dado que o usuário preencheu os dados de fechamento do lote
    Quando clicar no botão "Emitir Certificado"
    Então o botão deve entrar em estado "loading" e ficar desabilitado para prevenir cliques duplos
    E deve enviar a chave "Idempotency-Key" garantindo a geração de apenas um certificado único por transação

  Cenário: Visualização Pública de Certificado via QR Code (DTO Minimizado)
    Dado que um visitante acesse o token público do certificado
    Quando a tela de consulta pública for carregada
    Então os badges de status de pegada de carbono devem seguir as cores semânticas (Verde para Válido, Vermelho para Invalidados)
    E NENHUM dado pessoal do produtor (como CPF/CNPJ, e-mail ou telefone) deve ser exibido na interface