# Decisões Arquiteturais — STEMMIA Dexter

---

## 2026-04-07 — Repositório único vs pastas no Desktop

**Contexto:** Dezenas de pastas espalhadas no Desktop (ANALISADOR FINAL, Projetos Plan Mode, STEMMIA SISTEMA COMPLETO, etc.) tornavam navegação e manutenção impossíveis.
**Decisão:** Centralizar tudo em um repositório único ~/Desktop/STEMMIA Dexter/ com estrutura modular.
**Motivo:** Reduz carga cognitiva, permite git, facilita backup e continuidade entre sessões.
**Alternativas descartadas:** Manter pastas separadas (caos); monorepo com submódulos (complexidade desnecessária).

---

## 2026-04-07 — gerar_peticao.py com XML em vez de reportlab/fpdf2

**Contexto:** Geração de petições em PDF precisava de formatação precisa (margens, fontes, cabeçalhos judiciais).
**Decisão:** Usar geração via XML como intermediário, não reportlab nem fpdf2 diretamente.
**Motivo:** reportlab tem API verbosa e fpdf2 falha em encoding de caracteres especiais (acentos, cedilha). XML permite template reutilizável.
**Alternativas descartadas:** reportlab (verboso demais); fpdf2 (encoding quebrado); LaTeX (dependência pesada).

---

## 2026-04-10 — pdftotext com fallback para Tesseract OCR

**Contexto:** PDFs do TRT frequentemente são escaneados (imagens), não texto nativo. pdftotext retorna string vazia nesses casos.
**Decisão:** Tentar pdftotext primeiro; se retornar vazio ou < 50 caracteres, rodar tesseract com --oem 1 --psm 6.
**Motivo:** Manter velocidade para PDFs nativos e garantir extração para escaneados.
**Alternativas descartadas:** Usar só tesseract (lento para PDFs nativos); ignorar escaneados (perda de dados críticos).

---

## 2026-04-11 — FATO+PROVA+IMPACTO substituiu score numérico 0-100

**Contexto:** Score numérico (0-100) para gravidade de argumentos era subjetivo e inconsistente entre sessões. IA alucinava scores.
**Decisão:** Substituir por tripla qualitativa: FATO (o que aconteceu), PROVA (documento que comprova), IMPACTO (consequência jurídica/médica).
**Motivo:** Elimina subjetividade numérica, força vinculação a evidência concreta, impede alucinação.
**Alternativas descartadas:** Score 0-100 (alucinação); classificação A/B/C (ainda subjetiva sem ancoragem).

---

## 2026-04-13 — Selenium + Chrome debug porta 9223 para download PJe

**Contexto:** Download automatizado de processos do PJe exigia autenticação com certificado digital A1. Certificado só funciona no Windows/Parallels.
**Decisão:** Chrome aberto em modo debug na porta 9223 com perfil isolado (.chrome-pje), Selenium conecta via debuggerAddress.
**Motivo:** Permite manter sessão autenticada persistente sem relogin. Perfil isolado evita conflito com Chrome pessoal.
**Alternativas descartadas:** Puppeteer (menos controle sobre certificado); requests + cookies (PJe usa JS pesado); extensão Chrome (frágil).

---

## 2026-04-14 — Sistema de memória persistente em Markdown/Obsidian

**Contexto:** Memória comprometida (TEA + TDAH) + perda de contexto entre sessões Claude.
**Decisão:** Criar sistema de memória em ~/Desktop/STEMMIA Dexter/memoria/ com Markdown compatível com Obsidian (wikilinks, vault local).
**Motivo:** Markdown é durável, versionável (git), legível sem ferramenta, e Obsidian adiciona grafo de conhecimento + busca.
**Alternativas descartadas:** Notion (vendor lock-in); banco SQL (overhead); apenas CLAUDE.md (sem estrutura).
