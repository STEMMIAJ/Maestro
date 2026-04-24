# 03-IDENTIDADE — Índice

Pasta de identidade profissional do Dr. Jesus (perito judicial). Fonte única de verdade para dados que aparecem em petições, laudos, atestados e comunicados.

## Estrutura

```
03-IDENTIDADE/
├── _INDICE.md                  # este arquivo
├── dados-profissionais.md      # campos pessoais/profissionais (CRM, CPF, endereço, PIX)
├── estilo-redacao.md           # padrão de escrita (tratamento, pessoa verbal, fecho)
├── guia-extracao-estilo.md     # como extrair perfil de estilo do corpus real
├── assinatura/                 # imagens de assinatura digitalizada
├── logos/                      # logos STEMMIA / marca pessoal
└── timbrado/                   # papel timbrado (DOCX / PDF base)
```

## Função de cada arquivo

| Arquivo | Função | Quem preenche |
|---|---|---|
| `dados-profissionais.md` | Template de dados. Placeholders `{{CAMPO}}` alimentam templates de laudo/petição automaticamente. | Usuário (uma vez; revisar 2x/ano). |
| `estilo-redacao.md` | Escolhas de estilo (tratamento, pessoa verbal, fecho). Checkboxes para o usuário marcar. | Usuário valida; Claude obedece. |
| `guia-extracao-estilo.md` | Método para extrair o estilo real a partir de peças antigas em `02-BIBLIOTECA/peticoes/_corpus-estilo/`. Gera `perfil-estilo.json`. | Sistema automatiza; usuário confere. |
| `assinatura/` | PNG transparente da assinatura para colar em PDF. | Usuário escaneia. |
| `logos/` | Logo da marca (cabeçalho, rodapé, e-mail). | Usuário fornece. |
| `timbrado/` | Papel timbrado base (DOCX/PDF) usado como moldura. | Usuário localiza arquivo existente. |

## Fluxo de uso

1. Usuário preenche `dados-profissionais.md` (substitui placeholders).
2. Usuário marca opções em `estilo-redacao.md`.
3. Sistema processa corpus em `02-BIBLIOTECA/peticoes/_corpus-estilo/` conforme `guia-extracao-estilo.md` e gera `perfil-estilo.json`.
4. Agente de redação lê os três artefatos (dados + estilo manual + perfil automático) antes de produzir qualquer peça.

## Regras

- NUNCA duplicar dados desta pasta em outros arquivos. Referenciar por placeholder.
- Alteração de CRM, endereço ou PIX → editar apenas `dados-profissionais.md`. Todos os templates recebem a mudança automaticamente.
- Perfil de estilo é regerado sempre que o corpus crescer 20% ou o usuário solicitar.
