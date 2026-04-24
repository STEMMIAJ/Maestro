# MEMÓRIAS — como funcionam

## O que é (1 frase)
Memória = arquivo `.md` em `~/.claude/projects/-Users-jesus/memory/` que sobrevive entre sessões — quando abro o Claude amanhã, ainda lembro.

## Diferença do `jsonl`
- `jsonl` (em `~/.claude/projects/-Users-jesus/[uuid].jsonl`) = a CONVERSA inteira. Some quando a sessão fecha (no contexto, não no disco).
- `memory/*.md` = FATOS que valem para todas as sessões futuras.

---

## Onde ficam (caminho exato)

```
~/.claude/projects/-Users-jesus/
├── MEMORY.md                    ← índice (sempre carregado)
├── memory/
│   ├── user_perfil.md            ← quem você é
│   ├── feedback_*.md             ← regras de comportamento
│   ├── project_*.md              ← projetos em andamento
│   └── reference_*.md            ← informações fixas
├── errors.jsonl                  ← log do anti-mentira
└── [uuid].jsonl                  ← cada conversa = 1 jsonl
```

---

## O que é o `MEMORY.md`

Índice de todas as memórias. **Sempre carregado** no início da sessão.

Estrutura: lista markdown com link para cada memória + 1 linha de descrição.

```markdown
- [feedback_acentos.md](feedback_acentos.md) — SEMPRE acentuar, NUNCA escrever sem acento
- [project_dexter.md](project_dexter.md) — Hub central de perícias, reorganizado em abr/2026
```

**Limite:** linhas após a 200 são cortadas. Por isso descrições devem ser curtas.

---

## 4 tipos de memória

### 1. `user`
**Sobre você.** Quem é, o que faz, preferências.

Exemplo: `user_perfil.md`
```markdown
---
name: Perfil de Jésus
description: Médico perito CRM-MG 92148, autista TEA + TDAH
type: user
---

Médico perito judicial. Pai falecido fev/2026. Sobrecarga severa.
Linguagem: tom seco, direto, sem disclaimers.
```

### 2. `feedback`
**Como me comportar.** Regras que eu devo seguir.

Exemplo: `feedback_acentos.md`
```markdown
---
name: Sempre acentos
description: NUNCA escrever português sem acento
type: feedback
---

REGRA: SEMPRE acentos corretos.
Why: usuário detesta "voce" sem acento.
How to apply: revisar antes de mandar.
```

### 3. `project`
**Estado de projeto em andamento.**

Exemplo: `project_pje_download.md`
```markdown
---
name: Download PJe funcionando
description: Selenium + Chrome 9223 + perfil isolado, fluxo completo
type: project
---

Status: FUNCIONANDO desde 13/abr/2026.
Última execução: 13/abr.
Próximo passo: rodar amanhã pra processos novos.
```

### 4. `reference`
**Informação que vou consultar de novo.**

Exemplo: `reference_ftp_deploy.md`
```markdown
---
name: FTP do site
description: Credenciais e config para deploy stemmia.com.br
type: reference
---

HOST: alvorada.nuvemidc.com (IPv4: 177.73.233.49)
USER: deploy@stemmia.com.br
PASS: (no arquivo)
DIR_BASE: /
NOTAS: forçar IPv4 senão trava.
```

---

## Como o Claude usa memórias

### Ao abrir conversa
1. Carrega `MEMORY.md` automaticamente
2. Vê a lista de memórias disponíveis
3. NÃO carrega cada uma — só as que parecerem relevantes

### Durante a conversa
- Você fala de algo que casa com descrição de uma memória
- Eu chamo `Read` na memória específica
- Aplico o que está nela

### Ao terminar conversa
- Se aprendi algo novo importante
- Crio memória nova (ou atualizo existente)
- Adiciono linha no `MEMORY.md`

---

## Quando salvar memória

✅ **SALVAR:**
- Fato sobre você que não muda (ex: CRM)
- Regra de comportamento ("nunca faça X")
- Estado de projeto (status, próximo passo)
- Credencial/caminho que vou precisar de novo
- Decisão tomada (com motivo)

❌ **NÃO SALVAR:**
- Detalhe da conversa atual (já tá no jsonl)
- Código (tá no repositório)
- Histórico de commits (tá no git)
- Arquitetura óbvia (lê o código)
- Solução de bug específico (commit message basta)

---

## Como pedir pra eu criar

Você fala:
> "salva isso como memória feedback: nunca abrir Chrome do Mac pro PJe"

Eu confirmo com:
1. Caminho do arquivo criado
2. Linha adicionada no MEMORY.md
3. ls -lh do arquivo (prova)

---

## Como você lê manualmente

```bash
# Ver índice
cat ~/.claude/projects/-Users-jesus/memory/MEMORY.md

# Ver memória específica
cat ~/.claude/projects/-Users-jesus/memory/feedback_acentos.md

# Listar todas
ls -lh ~/.claude/projects/-Users-jesus/memory/
```

---

## Quantidade hoje
~67 memórias ativas (contagem em `MEMORY.md`).

---

## Manutenção

- A cada 30 dias, revisar memórias com `data_ultima_revisao` velha.
- Memória que ficou errada → atualizar (não deletar, mudar conteúdo).
- Memória obsoleta → mover para subpasta `memory/_arquivadas/`.

---

## Backup
Tudo em `~/.claude/projects/-Users-jesus/memory/` foi para o backup de hoje em `~/Desktop/BACKUP CLAUDE/2026-04-19_03h40/02-claude-home/projects/-Users-jesus/memory/`.

---

## Problemas conhecidos

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Claude esquece coisa importante | Memória não foi criada | Pedir explicitamente: "salva como memória" |
| Memória conflita com outra | Duas dizem oposto | Você decide qual vale, eu atualizo |
| MEMORY.md grande | Muitas memórias | Agrupar por tópico, descrições curtas |
| Memória desatualizada | Projeto mudou | Ler antes de aplicar, atualizar se mudou |

---

## Diferença das pastas (importante não confundir)

| Pasta | Para que |
|-------|----------|
| `~/.claude/projects/-Users-jesus/memory/` | Memórias permanentes (.md) |
| `~/.claude/projects/-Users-jesus/[uuid].jsonl` | Conversas individuais (1 por sessão) |
| `~/.claude/skills/` | Skills (instruções carregadas em tema) |
| `~/.claude/agents/` | Agentes (subagentes especializados) |
| `~/.claude/CLAUDE.md` | Regras universais (sempre ativas) |
| `~/.claude/settings.json` | Configurações (hooks, perms, modelo) |
