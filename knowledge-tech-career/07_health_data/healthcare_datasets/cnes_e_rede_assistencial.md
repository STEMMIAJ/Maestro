---
titulo: "CNES — Cadastro Nacional de Estabelecimentos de Saúde"
bloco: "07_health_data/healthcare_datasets"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "maduro"
tempo_leitura_min: 7
---

# CNES — Cadastro Nacional de Estabelecimentos de Saúde

Registro oficial de **todos** os estabelecimentos de saúde do Brasil (públicos e privados), mantido pelo Ministério da Saúde.

## O que contém

- Identificação: código CNES (7 dígitos), razão social, fantasia, CNPJ.
- Endereço, contato, gestor.
- **Tipo de estabelecimento**: hospital, UBS, clínica, SADT, consultório isolado, laboratório, farmácia etc. (tabela de tipos oficial).
- **Leitos**: por especialidade (clínica, cirúrgica, obstétrica, pediátrica, UTI adulto/pediátrica/neonatal).
- **Equipamentos**: tomógrafo, ressonância, mamógrafo, raio-X, ultrassom.
- **Profissionais vinculados**: CPF, CBO (ocupação), carga horária, vínculo (estatutário, CLT, autônomo).
- **Serviços especializados** habilitados (ex.: alta complexidade oncológica, transplante).
- **Equipes da APS** (ESF, NASF, eSB).
- **Habilitações** ministeriais (UPA, UTI tipo II, hospital amigo da criança).

## Como consultar

### Portal web

- URL: https://cnes.datasus.gov.br.
- Busca por nome, CNPJ, município, código CNES.
- Consulta retorna ficha completa do estabelecimento.

### API / dados abertos

- **Dados abertos DataSUS-CNES**: arquivos mensais em FTP (`/dissemin/publicos/CNES/200508_/Dados/`), formato DBC.
- Módulos separados: LT (leitos), EP (equipamentos), PF (profissionais), HB (habilitações), ST (estabelecimento).
- Granularidade: mês.

### Python

```python
from pysus.online_data.CNES import download
df = download(group="ST", state="MG", year=2026, month=3)
```

### REST API não-oficial

- Projeto **OpenDataSUS** hospeda parte em CSV via https://opendatasus.saude.gov.br.
- `[TODO/RESEARCH: confirmar endpoint oficial CNES REST 2026]`.

## Código CNES

- 7 dígitos numéricos.
- Único por estabelecimento.
- Usado em TISS, AIH, APAC, prescrição eletrônica, vínculos profissionais.

## Aplicações periciais

1. **Verificar existência e habilitação** do estabelecimento réu no momento do fato — CNES tem histórico por competência.
2. **Conferir se profissional** constava no corpo clínico em data X.
3. **Checar leitos e equipamentos** disponíveis (ex.: UTI neonatal no município).
4. **Comprovar capacidade técnica** para procedimento (serviços habilitados).
5. **Auditoria de vínculos** (se médico atendia em horário incompatível).

## Combinação com outros sistemas

- **CNES + SIH**: quantos partos por hospital, taxa de cesárea, mortalidade materna.
- **CNES + SIA**: cobertura ambulatorial por UBS.
- **CNES + CNPJ/Receita**: verificar vínculo societário do prestador.
- **CNES + judicial**: localizar todos os CNES de uma rede privada ré.

## Limitações

1. **Atualização depende do gestor local** — pode haver defasagem.
2. **Profissional pode ter múltiplos vínculos** — somar horas pode exceder realidade.
3. **Leitos cadastrados ≠ leitos operacionais** (fechamento temporário não aparece).
4. **Consultórios isolados** (cnes tipo 40) podem ser subcadastrados.

## Estrutura resumida do arquivo ST (estabelecimento)

Principais campos:

- CNES, CNPJ, RAZAO_SOC, NOME_FANT.
- COD_IBGE (município), REGIAO_SAUDE.
- TPGESTAO (gestão municipal/estadual/dupla), ESFERA_A (pública, privada, filantrópica).
- CO_TIPO_UNIDADE (tabela tipos), NATUREZA.
- DT_ATUAL, COMPETEN (mês/ano da base).

## Fluxo pericial sugerido

```python
import pandas as pd
from pysus.online_data.CNES import download

est = download(group="ST", state="MG", year=2024, month=12)
alvo = est[est["CNES"] == "2123456"]  # código do hospital

prof = download(group="PF", state="MG", year=2024, month=12)
corpo_clin = prof[(prof["CNES"] == "2123456") & (prof["CPF"] == "...")]
```

## Alternativas comerciais

- **ScaleHealth**, **Abramge**, operadoras — bases próprias de prestadores credenciados, mas sem valor probatório como o CNES.
