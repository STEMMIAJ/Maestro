## 2026-04-14 — Reorganização completa STEMMIA Dexter

**O que fez:**
- Criou estrutura de 39 diretórios organizados (src/, memoria/, agents/, templates/, referencias/, docs/, painel/, hooks/, n8n/, data/)
- 28 arquivos de conteúdo criados (~3.900 linhas) via 5 agentes Opus paralelos
- Migrou 58 scripts Python para src/ (6 categorias: pipeline, petições, honorários, jurisprudência, pje, utils)
- Migrou 85 agentes Claude para agents/clusters/ (7 categorias)
- Migrou 5 hooks e 5 workflows N8N
- Instalou/abriu Obsidian com vault em memoria/
- Criou dashboard HTML com sidebar escura (painel/index.html)
- Criou .gitignore robusto bloqueando dados sensíveis

**Decisões tomadas:**
- Copiar scripts, não mover (originais preservados em SCRIPTS/)
- Pasta memoria/ = vault Obsidian (sem duplicação)
- Agentes classificados em 7 clusters por função
- data/ completamente excluído do Git
- 5 agentes paralelos para criação de conteúdo

**Pendências:**
- Testar cada script copiado: `python3 script.py --help`
- Ajustar imports relativos nos scripts de src/
- Popular referencias/protocolos/ e referencias/tabelas/
- Reclassificar 49 agentes "gerais" em clusters específicos
- Subir painel no site via FTP
- Criar script de conversão sessões TXT → notas Obsidian
- Configurar Daily Notes no Obsidian

**Aprendizados:**
- 558 skills espalhadas por plugins diversos (não centralizadas)
- Apenas 1 dos 6 orquestradores foi encontrado em ~/.claude/agents/
- Brew já tinha Obsidian instalado
- Migração de 153 componentes sem erro
