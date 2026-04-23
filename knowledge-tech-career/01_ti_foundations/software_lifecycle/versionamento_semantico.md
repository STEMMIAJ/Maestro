---
titulo: "Versionamento semântico"
bloco: "01_ti_foundations/software_lifecycle"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 4
---

# Versionamento semântico

## SemVer (Semantic Versioning)

Convenção para numerar versões de software de forma que o número carregue significado. Formato: `MAJOR.MINOR.PATCH`.

Exemplo: `2.7.3`.

Regras para incrementar:

- **PATCH** (`2.7.3` → `2.7.4`) — correção de bug que **não muda comportamento externo** e é totalmente compatível. Exemplo: corrigir cálculo errado em função `calcular_prazo()`.
- **MINOR** (`2.7.3` → `2.8.0`) — nova funcionalidade compatível com versões anteriores. Quem usa `2.7` continua funcionando ao atualizar para `2.8`. PATCH volta a zero. Exemplo: adicionar função `exportar_docx()`.
- **MAJOR** (`2.7.3` → `3.0.0`) — mudança **quebra compatibilidade**. Código que depende da versão antiga pode deixar de funcionar. MINOR e PATCH voltam a zero. Exemplo: renomear `gerar_laudo()` para `gerar_documento_pericial()` ou alterar formato do JSON retornado.

## Extensões opcionais

- **Pré-release** — `2.8.0-beta.1`, `3.0.0-rc.2`. Indica versão instável; precede a versão final.
- **Build metadata** — `2.8.0+20260423`. Identifica build específico, ignorado para ordenação.

Ordem: `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0 < 1.0.1`.

## Versão 0.x.y

Enquanto `MAJOR = 0`, a API é considerada instável. Qualquer incremento pode quebrar tudo. Por isso os artefatos deste projeto começam em `0.1` — sinalizam rascunho.

## Quando subir cada

| Mudança | Subir |
|---|---|
| Corrigir typo em log | PATCH |
| Corrigir bug de cálculo | PATCH |
| Adicionar parâmetro opcional com default | MINOR |
| Adicionar nova função | MINOR |
| Remover função pública | MAJOR |
| Renomear parâmetro | MAJOR |
| Mudar formato de arquivo de saída | MAJOR |
| Mudar default de parâmetro existente | MAJOR (muda comportamento) |
| Alterar dependência interna sem afetar usuário | PATCH ou nada |

## Onde aparece

- `package.json` (npm), `pyproject.toml` (Python), `Cargo.toml` (Rust).
- Tags do Git: `git tag v2.7.3`.
- Releases no GitHub.
- Cabeçalho de API: `API-Version: 2.7.3`.
- Frontmatter de documento vivo (como estes artefatos).

## Constraints (intervalos) em gerenciadores

- `^2.7.3` — aceita qualquer `2.x.x >= 2.7.3` (compatível MINOR).
- `~2.7.3` — aceita qualquer `2.7.x >= 2.7.3` (só PATCH).
- `>=2.7.3 <3.0.0` — explícito.

Regra prática: bibliotecas usam `^` (aceita features novas); aplicação em produção prefere lockfile (`package-lock.json`, `poetry.lock`) para reprodutibilidade exata.

## Por que importa para o perito

- **Laudo pericial sobre software** que alegou "falha após atualização" exige comparar versões por SemVer: pulo MAJOR = quebra esperada; bug em PATCH = responsabilidade do fornecedor.
- **Documentos vivos** (laudo modelo v0.1 → v1.0 após peer review) se beneficiam de SemVer para rastrear evolução.
- **Monitor de processos** e scripts versionados: ao ver `v1.3.2 → v2.0.0` no changelog, você sabe que reconfiguração é necessária.

## Referências

- semver.org — spec 2.0.0 oficial.
