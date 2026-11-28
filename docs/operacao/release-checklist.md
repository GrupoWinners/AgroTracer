# Gate de release — S7-T05

Revisar este checklist no commit candidato, com Samela, Joao e QA.
Automacao auxilia; nao aprova release nem cria tag v1.0.0.

## Verificacao reproduzivel

```sh
python tools/demo.py up
python tools/demo.py verify
python tools/release_check.py
```

Evidencias seguras: .demo/verificacao.json e .demo/release-check.json.
Nunca publicar .demo/acesso.json, .demo/.env, dumps ou compose config.
O job wordpress_release executa todas as suites PHP; verificacoes cobre
migrations/seguranca/proxy/CORS; recuperacao cobre restore.

## Homologacao do destino real

- Debug/desenvolvimento desligados: WP_DEBUG, WP_DEBUG_LOG e DISPLAY false;
  PHP display_errors off; API via python -m app.run, sem --reload.
- Nunca habilitar AGROTRACER_OFFLINE_PREVIEW fora de local/development.
  Mesmo local exige administrador e opt-in booleano true. Nao habilitar esse
  flag para contornar erro de API em homologacao/producao.
- Cliente TLS sempre verifica certificado; usar CA valida. API interna HTTP
  somente em rede privada controlada; frontend publico HTTPS no proxy.
- API/DB/Redis fora da Internet; firewall/rede restringem trafego ao WP/proxy.
  O compose de demo vincula apenas WP/API em loopback; DB/Redis sem porta host.
- Proxy deve sobrescrever headers recebidos ou anexar cadeia de forma segura;
  configurar apenas IPs/CIDRs reais em AGROTRACER_TRUSTED_PROXIES, nunca /0.
  Se nao houver proxy confiavel, manter vazio. Nao usar CORS * com credentials.
- Logs devem omitir query/token/cookies/IP/corpo. Demo registra so status e
  duracao Apache; erros brutos desativados, diagnostico por correlation/API.
  Servidor real precisa aplicar politica equivalente em todos os coletores.
- Segredos distintos por ambiente, acesso minimo, fora do Git e do browser;
  rotacao coordenada WP/API. Revisar historico/CI artifacts e permissoes dos
  arquivos locais; scanner de padroes nao substitui auditoria completa.
- Produtor usa capability agrotracer_manage_farms; publish_posts nao concede
  acesso. Administracao backend exige AGROTRACER_ADMIN_WP_IDS explicito.
- Validar listagens/telas reais: endpoints que eram exclusivamente mock agora
  falham de forma explicita fora do preview. Revisar impacto com Joao e QA.
- Confirmar backup/restauracao e riscos conhecidos com owner/data.

Registrar responsavel, data, commit, evidencia e decisao para cada item no
Jira. Tag somente apos review independente e QA Gate sem P1/P2. Esta entrega
nao executa S7-T04, S7-T06, deploy, merge ou tag.
