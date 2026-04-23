---
titulo: Template de Evidência de Habilidade
bloco: 11_personal_skill_mapping
arquivo: evidence_of_skill/evidence_catalog_template.md
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# Template — Catálogo de Evidências

## Propósito
Cada afirmação "sei X" na matriz de habilidades precisa apontar para uma evidência objetiva. Este template padroniza o registro. Uma evidência por arquivo. Nome do arquivo: `YYYY-MM-DD_slug-curto.md`.

## Frontmatter padrão (copiar no topo do arquivo)

```yaml
---
titulo: <frase-objetiva do que foi feito>
bloco: 11_personal_skill_mapping
arquivo: evidence_of_skill/<YYYY-MM-DD>_<slug>.md
versao: 0.1
status: ativo
ultima_atualizacao: <YYYY-MM-DD>
tipo_evidencia: [projeto|script|laudo|PR|certificacao|issue|publicacao|apresentacao]
habilidade_principal: <domínio.subtopico da matriz>
nivel_demonstrado: <0|1|2|3|4>
---
```

## Seções obrigatórias

### 1. Descrição
Frase direta do que foi feito. Máximo 3 linhas. Sem adjetivos inflados.

### 2. Arquivo ou URL
- Caminho absoluto se local: `/Users/jesus/.../arquivo.py`
- URL se remoto: commit SHA, PR link, repo público
- Anonimização: se for caso real pericial, referência + flag `[ANONIMIZADO]`

### 3. Habilidade demonstrada
Lista (1–3 itens) apontando para linhas específicas da matriz:
- `Python.async/await` — nível demonstrado 2
- `APIs.consumir REST` — nível demonstrado 2

### 4. Data
Data da execução (não do cadastro).

### 5. Validação externa
Tipo e peso:
- **Forte**: code review por terceiro, PR aceito em repo público, certificação emitida por instituição reconhecida, laudo homologado em sentença
- **Média**: funciona em produção interna há >30 dias, usado por colega
- **Fraca**: só rodou uma vez, só autoverificação

Se ausente, marcar `validacao_externa: nenhuma` e justificar.

### 6. Limitações conhecidas
Honesto. "Só funciona se input tiver campo X", "Não testei com N>1000", "Depende de hard-code que uma IA gerou".

### 7. Próximo passo sugerido
Curto. Ex: "cobrir com pytest", "refatorar para async", "submeter a code review".

## Exemplo mínimo preenchido

```yaml
---
titulo: Script DJEN que consulta intimações e filtra homônimo irmão
bloco: 11_personal_skill_mapping
arquivo: evidence_of_skill/2026-04-22_djen_filtro_homonimo.md
versao: 0.1
status: ativo
ultima_atualizacao: 2026-04-22
tipo_evidencia: script
habilidade_principal: Python.async/await
nivel_demonstrado: 2
---
```

### Descrição
Script assíncrono consulta DJEN, filtra publicações por nome do perito removendo homônimo (irmão), grava em SQLite.

### Arquivo
`/Users/jesus/Desktop/STEMMIA Dexter/src/automacoes/monitor_processos/djen_filtro.py`

### Habilidade demonstrada
- Python.async/await — 2
- APIs.consumir REST — 2
- Databases.SQLite — 2

### Data
2026-04-22

### Validação externa
Média — rodando via launchd 3x/dia há 5 dias, zero falso-positivo nas últimas 20 execuções.

### Limitações conhecidas
- Filtro homônimo depende de regex simples sobre OAB; se DJEN mudar formato, quebra.
- Sem retry exponencial — já registrado como falha PW-012.

### Próximo passo
Adicionar backoff e cobrir filtro com pytest (3 casos: homônimo, não-homônimo, empate).
