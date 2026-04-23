---
titulo: "Segredo de Justiça no PJe — Fluxo Pericial"
bloco: "05_security_and_governance"
tipo: "compliance"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Segredo de Justiça no PJe

Processos sob segredo de justiça exigem marcação, controle de acesso e armazenamento segregado. Para o perito, a falha nesse controle é risco ético (CFM), administrativo (LGPD) e processual (nulidade + responsabilização).

## Base legal

- CPC art. 189: processos em segredo — casamento/divórcio, guarda, interdição, interesse social ou de intimidade, arbitragem. Em perícia psiquiátrica e de vítima de crime sexual, padrão.
- CPC art. 11 e 189, §1º: visualização restrita às partes e seus procuradores.
- ECA, Lei Maria da Penha, Estatuto do Idoso: hipóteses específicas.

## Identificação no PJe

Processo em segredo mostra:

- Cadeado fechado ou ícone específico na interface.
- Número parcialmente ocultado em listas públicas.
- Aba "Dados Básicos" com marcação "Segredo de Justiça: SIM".
- Acesso limitado a usuários cadastrados no processo (partes, advogados, perito nomeado).

**Verificar sempre antes de baixar ou discutir peça.** Em dúvida, tratar como segredo.

## Obrigações do perito

1. **Nomeação visível**: perito vinculado no processo acessa o conteúdo; terceiros não.
2. **Não compartilhar PDFs com assistentes** sem vínculo formal e sigilo contratual.
3. **Não imprimir** sem necessidade; se imprimir, destruir com triturador após uso.
4. **Não usar IA em nuvem** sobre o conteúdo sem anonimização.
5. **Armazenar em pasta cifrada dedicada**, separada de processos públicos.

## Fluxo recomendado de armazenamento

```
~/Desktop/_MESA/10-PERICIA/processos/
├── publicos/
│   └── <numero>/
└── segredo_justica/
    ├── _README.md (regras de acesso)
    └── <numero>/
        ├── FICHA.json  (minimiza dados no nome)
        ├── autos/
        ├── anexos/
        └── laudo/
```

Pasta `segredo_justica/` com:

- Permissão 700 (só o usuário).
- Em volume APFS cifrado adicional ou imagem DMG cifrada.
- Nunca sincronizada para iCloud Drive genérico.

## Marcação no sistema local

Convenção sugerida no nome da pasta: prefixo `SJ_` ou atributo estendido xattr com tag. No Finder, usar tag colorida "Segredo".

```bash
xattr -w user.segredo "true" ~/caminho/<numero>
```

## Download via script

Ao baixar autos com `download_pje.py`, o script deve:

- Ler campo "segredo" do PJe (API ou scraping).
- Salvar em `segredo_justica/` automaticamente quando verdadeiro.
- Logar acesso em `~/Desktop/STEMMIA Dexter/00-CONTROLE/logs/segredo-acessos.log`.

## Discussão do caso

Com colegas, pupilos, em apresentações:

- Anonimizar: trocar nome, alterar idade ligeiramente, remover município específico.
- Nunca screenshot do PJe com dados identificáveis.
- Consentimento do juízo ou fim do processo não liberam discussão pública automática — se houver segredo absoluto, preservar.

## Integrantes do escritório

Secretária, assistente, estagiário que venham a acessar processo em segredo:

- Termo de confidencialidade assinado.
- Conta de usuário própria no Mac (sem compartilhamento).
- Treinamento documentado.
- Revogação imediata de acesso ao desligamento.

## Descarte

Ao fim do prazo de retenção (ver `../compliance_privacy/lgpd_para_medico_perito.md`):

- Apagar com sobrescrita (`srm` ou equivalente em APFS).
- Registrar no log de descarte: data, processo (código interno, não número público), método.

## Sinais de alerta

- Arquivo de processo em segredo encontrado fora de `segredo_justica/`.
- Screenshot com dados identificáveis em pasta pública.
- Conversa com IA em nuvem com número real do processo.
- Pen drive com dados em segredo saindo do escritório sem cifra.

Qualquer um exige avaliação de incidente — ver `../incident_response/playbook_incidente_minimo.md`.

## Referência cruzada

- `lgpd_para_medico_perito.md`
- `sigilo_medico_cfm.md`
- `../../10_career_map/professions_taxonomy/papeis_em_saude_dados_e_pericia.md`
