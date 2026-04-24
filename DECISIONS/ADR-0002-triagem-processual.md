# ADR-0002 — Triagem processual replicável como pacote interno do pipeline Maestro

**Data:** 2026-04-24
**Status:** accepted
**Autor:** Dr. Jesus (+ Claude Opus 4.7 como redator)

## Contexto

Em 2026-04-23, 24 PDFs de Taiobeiras foram classificados manualmente em 4 grupos (A=21 AJG, B=1 custeado, C=1 securitário, D=1 seguro vida com JG contestada) por leitura visual. Essa classificação:

1. **Não é replicável** — cada novo lote (Governador Valadares, Mantena, Conselheiro Pena) exigiria releitura manual.
2. **Não tem trecho-evidência** gravado — impossível auditar depois.
3. **Não distingue gratuidade DEFERIDA de PEDIDA** — scripts atuais (`extrair_partes.py`) só leem flag pedida do cabeçalho PJe. CLAUDE.md global distingue mundo AJG (tabela R$ 612 TJMG) de mundo custeado (proposta livre) e exige checagem de deferimento.
4. **Bloqueia emissão de propostas** — sem saber quem custeia, não se sabe se aplica tabela ou se faz proposta.

Pressão externa:
- R1 Dexter: uma issue por sessão; sem issue não há trabalho.
- R2 Dexter: todo código novo vai DENTRO de `Maestro/`.
- R8 Dexter: decisão arquitetural exige ADR ANTES de implementar.
- ENFORCEMENT de planos: plano deve seguir template 11 blocos.

## Opções consideradas

1. **`PYTHON-BASE/08-SISTEMAS-COMPLETOS/triagem-processual/`** — fora de Maestro.
   - Prós: isolado, fácil de deletar.
   - Contras: viola R2 Dexter; não aproveita `extrair_partes` + `classificar_acao` como lib; obriga duplicação.

2. **Repo separado novo** (`STEMMIAJ/triagem-processual`).
   - Prós: autonomia total, pode virar produto.
   - Contras: mais overhead de sincronização; fragmenta ecossistema; reuso de `pipeline/` vira dependência externa.

3. **Pacote interno `Maestro/src/pipeline/triagem/`** reusando `extrair_partes.py` e `classificar_acao.py` como libs.
   - Prós: cumpre R2; reuso imediato; testes na mesma suíte; CI/CD do Maestro aplica sem modificação.
   - Contras: acopla triagem ao pipeline existente (mitigado: só importa funções puras, não estado).

## Decisão

**Opção 3** — `Maestro/src/pipeline/triagem/` como pacote interno.

Razão dominante: cumpre todas as regras Dexter (R1/R2/R3/R4/R8) sem custo de criar segundo repo e sem duplicar `extrair_partes`/`classificar_acao`. Reaproveita o que já está validado.

## Consequências

**Positivas:**
- Reuso direto de `extrair()` e `classificar()` sem copy-paste.
- Testes ficam em `tests/triagem/` junto com os outros, rodam no mesmo pytest.
- CI/CD do Maestro valida triagem como parte do repo oficial.
- FICHA.json canônica (38 campos) passa a ser populada em produção.
- Auditoria: cada classificação gera trecho-evidência + grupo no CSV.

**Negativas / custos aceitos:**
- Acoplamento ao pipeline Maestro (aceitável — é o repo central).
- Bloco `triagem` novo no schema FICHA.json requer comunicação com consumidores downstream (peticao-gerador, aceite-gerador). Mitigação: bloco é opcional, não quebra ficha legada.
- `classificar_acao.py` retorna strings com acentos (`"SECURITÁRIA"`, `"CÍVEL — CURATELA/INTERDIÇÃO"`) — código novo deve usar exatamente essas strings, sem normalização silenciosa.

**Arquivos/módulos afetados:**
- `Maestro/src/pipeline/triagem/` — NOVO pacote (8 módulos)
- `Maestro/src/pipeline/extrair_partes.py` — CONSUMIDO como lib (sem alteração)
- `Maestro/src/pipeline/classificar_acao.py` — CONSUMIDO como lib (sem alteração)
- `Maestro/tests/triagem/` — NOVO diretório de testes + 3 PDFs fixture
- `Maestro/CHANGELOG.md` — atualizado a cada fase
- `cowork/01-CASOS-ATIVOS/_TEMPLATE-CASO/FICHA.json` — schema permanece inalterado; bloco `triagem` adicionado como chave opcional de 1º nível

**Riscos conhecidos (tratados no plano 11 blocos):**
- Regex IMPUGNADA/REVOGADA calibrado contra amostra sem casos reais desses estados (ver Anexo A).
- Heurística de gênero de juiz (H1) por primeiro nome pode errar em nomes andróginos.
- Heurística de UF via dígitos 15-16 do CNJ pode falhar para justiça federal/eleitoral (restrito a justiça estadual = "8" no 13º dígito).

## Como reverter (se ADR for superseded)

1. Apagar `Maestro/src/pipeline/triagem/` e `Maestro/tests/triagem/`.
2. Reverter alterações em `CHANGELOG.md`.
3. Fechar issue correspondente com label `wontfix`.
4. Código externo que dependia do módulo: nenhum (é novo, sem consumidores legados).
5. FICHAs geradas com bloco `triagem` permanecem válidas (bloco opcional).
