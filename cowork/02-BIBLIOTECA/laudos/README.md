---
nome: laudos-por-classe
proposito: Laudos periciais por classe processual, com estrutura compartilhada e seções específicas
---

# Laudos — por classe

Estrutura canônica (comum a todos):

1. **Preâmbulo** — endereçamento, processo, nomeação
2. **Histórico** — fatos relevantes extraídos da petição inicial + contestação
3. **Documentos analisados** — lista numerada de peças e exames
4. **Exame físico** (se presencial) — achados por sistema
5. **Discussão** — raciocínio técnico (núcleo intelectual)
6. **Conclusão** — síntese objetiva
7. **Respostas aos quesitos** — item a item, numerados conforme autos

Variações por classe ficam na seção **Discussão** e nos **Respostas aos quesitos**.

## Particularidades por classe

### `erro-medico/`
- Seção extra: **Conduta esperada** (padrão técnico aplicável à especialidade do réu)
- Seção extra: **Análise do nexo causal** (adequada/direta/concausa)
- Referenciar diretrizes da especialidade (CFM, sociedades médicas)
- Cuidado redobrado: laudo em erro-médico é peça de grande escrutínio; versão inicial + revisão obrigatória antes de entregar

### `securitario/`
- Seção extra: **Análise documental da apólice** (cláusulas aplicáveis)
- Tabela SUSEP de invalidez — percentuais por membro/função
- Distinção clara: **lesão** (anatômica) × **incapacidade** (funcional) × **invalidez** (jurídica)

### `previdenciario/`
- Campos obrigatórios: **CID**, **DID** (data início doença), **DII** (data início incapacidade)
- Classificação: **temporária/permanente** × **parcial/total** × **uniprofissional/omniprofissional**
- Data provável de recuperação (se temporária)
- Linguagem do INSS (mas sem jargão previdenciário fora do técnico)

### `trabalhista/`
- CAT (Comunicação de Acidente de Trabalho): existe? data?
- PPP (Perfil Profissiográfico Previdenciário): análise
- LTCAT: análise
- **Nexo ocupacional** × **concausa** (NTEP / Decreto 6.957/2009)
- Agente insalubre quantificado (NR-15) se aplicável

### `civel-dano-pessoal/`
- Linha do tempo: fato → atendimento → evolução → sequela
- Distinção: **incapacidade temporária** × **incapacidade permanente** × **dano estético**
- Tabelas aplicáveis (SUSEP, Decreto 3048/99)

### `psiquiatrico/`
- Fontes heterogêneas: relato do periciando, relato de terceiros, evolução psiquiátrica, medicação
- CID-10 F + escalas aplicáveis (HAM-D, BDI, PANSS conforme caso)
- Cuidado com simulação e exagero (sem acusação; registrar achados)

## Template por classe

Cada `laudos/<classe>/` vai conter:
- `TEMPLATE.md` — esqueleto com marcadores de seção
- `placeholders.json` — campos extraídos de `FICHA.json`
- `checklist-pre-entrega.md` — o que VERIFICAR antes de fechar (específico da classe)
- `armadilhas.md` — erros comuns que o sistema alerta
- `diretrizes-aplicaveis.md` — CFM, sociedades, normas

## Templates-fonte já existentes (a importar)

- `~/Desktop/_MESA/10-PERICIA/templates-reaproveitaveis/` (symlink já existe em `_fonte-templates-mesa`)
- `LAUDOS-REFERENCIA/` do Dexter (symlink `_fonte-referencia`)

**Próximo passo:** catalogar cada template existente → classificar por classe → mover referência para subpasta correta.
