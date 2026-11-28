# Publicação da v1.0.0 — custódia da equipe

Fonte: [AG-113](https://losel.atlassian.net/browse/AG-113).
A automação gera **candidato**, não tag nem aceite. Não existe aprovação
implícita por CI verde. Os dois ensaios ainda não foram realizados.

## Revisão e ordem dos PRs

1. Revisar S7-T04 com João Vitor e Nadiny; executar e registrar dois ensaios
   de 8–12 minutos conforme [banca.md](banca.md).
2. Integrar S7-T04 somente após review/QA. Retargetar o PR S7-T06 para
   `develop`, conferir diff e CI novamente, então revisar/integrar S7-T06.
3. Fixar o SHA completo integrado e registrar no [aceite](../evidencias/sprint-7/aceite-interno.json).
   Validar CI desse SHA, riscos conhecidos, QA e review independente.
   Não usar SHA temporário de merge de PR como tag de release.

## Gerar e conferir o candidato

Na raiz do repositório, executar com SHA de 40 caracteres e diretório novo:

```text
python tools/release_bundle.py --commit SHA_COMPLETO --output .release/candidato
```

O script lê exclusivamente o snapshot Git desse commit, não arquivos locais
alterados ou não versionados. Produz código-fonte ZIP, documentação ZIP,
manifesto com hashes de cada arquivo, commit/tree e imagens declaradas, mais
SHA256SUMS.txt. Recusa caminhos privados selecionados e padrões conhecidos
de credenciais; isso não substitui revisão de segredos. Nunca anexar .demo,
senhas, tokens, dumps ou exports de configurações com valores reais.

No Linux: `sha256sum -c SHA256SUMS.txt` dentro da pasta gerada.
No PowerShell: `Get-FileHash .release/candidato/* -Algorithm SHA256` e
comparar os ZIPs e manifesto com SHA256SUMS.txt. Preservar exatamente os
bytes publicados; não recompactar depois de registrar os hashes.

O job `pacote_candidato` publica os arquivos como artifact do run. Em PR,
o manifesto identifica o merge de teste usado pela CI; depois do merge,
usar o pacote do run de `develop` correspondente ao SHA final.
As versões no manifesto são referências declaradas nos Dockerfiles/Compose,
não medições de runtime nem digests imutáveis das imagens externas.
`requirements*.txt`, migrations e demais fontes têm SHA-256 no manifesto.

## Aceite, tag e fechamento — etapa posterior aos gates

- Registrar dois ensaios completos, revisão de outro integrante, QA sem
  P1/P2 relacionado e decisão explícita da equipe com data, nome e links.
- Preencher aceite com SHA exato e links de CI/artefatos/hashes; qualquer
  alteração funcional posterior exige revalidar o candidato.
- Verificar no remoto que `v1.0.0` ainda não existe; nunca mover tag existente.
- Após aceite, criar tag anotada **no SHA aprovado** e publicar somente ela:
  `git tag -a v1.0.0 SHA_APROVADO -m "AgroTracer v1.0.0 — aceite interno"`
  e `git push origin refs/tags/v1.0.0`.
- Conferir no GitHub o commit apontado; publicar release com
  [notas](../releases/v1.0.0.md) e os quatro arquivos verificados do pacote.
- Registrar links finais da tag/release e seus hashes no aceite/Jira.
  Atualizações apenas do recibo documental após a tag devem identificar
  claramente o SHA da versão que documentam, sem mover a tag.
- Conferir dependências no Jira, concluir tarefas efetivamente aceitas e
  fechar a sprint/board pela interface. Registrar link e data da operação.
  O board é fonte única; não manter contagem manual de cards no guia.

Se faltar ensaio/review/aceite, parar antes de tag e fechamento. Não apagar
volumes, publicar produção ou fazer merge como efeito da geração do pacote.
