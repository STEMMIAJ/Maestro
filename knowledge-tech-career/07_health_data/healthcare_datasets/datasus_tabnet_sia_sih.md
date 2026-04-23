---
titulo: "DATASUS — TabNet, SIA, SIH, SIM, SINASC"
bloco: "07_health_data/healthcare_datasets"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "maduro"
tempo_leitura_min: 10
---

# DATASUS — sistemas de informação essenciais

Departamento de Informática do SUS mantém a principal infraestrutura de dados de saúde pública brasileira. Dados abertos, públicos, de agregação nacional.

## Mapa dos sistemas

| Sigla | O que cobre | Granularidade |
|---|---|---|
| **SIM** | Óbitos (todos) | Declaração de óbito |
| **SINASC** | Nascidos vivos | Declaração de nascido vivo |
| **SINAN** | Agravos de notificação compulsória (dengue, tuberculose, violência etc.) | Ficha de notificação |
| **SIH-SUS** | Internações hospitalares (AIH) | AIH (autorização de internação) |
| **SIA-SUS** | Procedimentos ambulatoriais | APAC, BPA |
| **CNES** | Estabelecimentos de saúde, leitos, equipamentos, profissionais | Estabelecimento |
| **SI-PNI** | Imunização | Dose aplicada |
| **SIOPS** | Orçamento público em saúde | Município/UF |
| **e-SUS APS** | Atenção primária (prontuário cidadão) | Atendimento individual |

## TabNet — o portal agregador

- URL: http://tabnet.datasus.gov.br.
- Interface web para **tabulação** de quase todos os sistemas acima.
- Permite: escolher variável linha, coluna, conteúdo, filtros por UF/município/período.
- Export: CSV, DBF, HTML, gráficos simples.
- Limitação: dados **agregados**, não individualizados. Para microdados, baixar arquivos brutos.

**Dado (2026-04-23):** tutorial oficial PDF ativo em https://datasus.saude.gov.br/wp-content/uploads/2020/02/Tutorial-TABNET-2020.pdf (data do doc: 2020, ainda vigente — DATASUS não publicou versão nova). Portal principal: https://datasus.saude.gov.br/informacoes-de-saude-tabnet/ . Acesso direto: https://tabnet.datasus.gov.br/. Tutorial alternativo acadêmico (Unisantos, 2020): https://www.unisantos.br/wp-content/uploads/2020/09/TUTORIAL.pdf

## Microdados (arquivos DBC/DBF)

- Formato legado **DBC** (compactado DBF), precisa descompactar.
- FTP histórico: `ftp.datasus.gov.br` → pastas `/dissemin/publicos/`.
- Atualmente vários datasets também distribuídos via https.
- Estrutura de arquivo (ex.: SIM): `DOyyyy.dbc` ou `DO{UF}{ano}.dbc`.

### Exemplo — baixar SIM MG 2023

```
/dissemin/publicos/SIM/CID10/DORES/DOMG2023.dbc
```

## Ferramentas de leitura

### Python (pysus / pyreaddbc)

```python
from pysus.online_data.SIM import download
df = download(state="MG", year=2023)  # retorna DataFrame
```

- `pysus` (pacote oficial-facto): baixa e descompacta.
- Alternativa manual: `pyreaddbc` + `dbfread`.

### R (read.dbc, microdatasus)

```r
library(read.dbc)
sim <- read.dbc("DOMG2023.dbc")

library(microdatasus)  # wrapper facilita
dados <- fetch_datasus(year_start = 2023, year_end = 2023, uf = "MG", information_system = "SIM")
```

## Dicionários de variáveis

- Cada sistema tem **dicionário oficial** (PDF) no site do DATASUS.
- Variáveis codificadas: sexo (1=M, 2=F, 9=ign), raça/cor, escolaridade, CID-10 causa básica.
- SIH: diagnóstico principal (DIAG_PRINC), procedimento realizado (PROC_REA em SIGTAP), valor pago (VAL_TOT).
- SIA: APAC (alta complexidade) separado de BPA (baixa/média).

## SIM — particularidades

- **Causa básica** ≠ causa imediata. Selecionada pela regra internacional da OMS (CID-10).
- Campo LINHA A/B/C/D na DO = encadeamento causal.
- Usar **causa básica** para estatísticas de mortalidade específica.

## SIH — particularidades

- AIH tem múltiplos registros quando internação passa de 45 dias (AIH de continuidade).
- Faturamento ≠ realidade clínica perfeita (glosas, erros).
- Variáveis críticas: DIAG_PRINC, DIAG_SECUN, PROC_REA, CID_MORTE (se óbito), DT_INTER, DT_SAIDA.

## Limitações gerais

1. **Subnotificação**: varia por sistema e região. SINAN sub-registra em áreas mais pobres; SIM melhor no Sul/Sudeste.
2. **Qualidade da causa básica** (SIM): "causas mal definidas" ainda são frequentes em municípios pequenos.
3. **Defasagem**: SIM consolidado ~18 meses após o ano de referência; SIH mais ágil.
4. **Mudança de versão** (CID-9 → CID-10 em 1996; CID-11 em transição) quebra séries históricas.
5. **Identificação do paciente**: microdados do DATASUS são **anonimizados**; linkage exige outras técnicas (record linkage probabilístico).

## Aplicações periciais

- Estabelecer **incidência/mortalidade** de condição em município/UF para contextualizar caso.
- Medir **taxa de infecção hospitalar** via SIH + CNES (leitos).
- Verificar **perfil de atendimento** do estabelecimento no CNES.
- **Linkage SIM ↔ SINASC** identifica mortalidade infantil por fatores pré-natais.

## Checklist antes de usar

- [ ] Sistema correto para a pergunta?
- [ ] Período e UF/município definidos?
- [ ] Dicionário de variáveis da versão certa?
- [ ] Denominador populacional (IBGE) compatível?
- [ ] Avisar sobre limitações (qualidade, subnotificação) no laudo?
