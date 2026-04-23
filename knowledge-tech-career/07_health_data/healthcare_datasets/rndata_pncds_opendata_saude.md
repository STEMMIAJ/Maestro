---
titulo: "Dados abertos em saúde — OpenDataSUS, RNDS, PNCDs"
bloco: "07_health_data/healthcare_datasets"
tipo: "referencia"
nivel: "iniciante"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "moderado"
tempo_leitura_min: 7
---

# Dados abertos em saúde no Brasil

Além do DATASUS tradicional, o Ministério da Saúde mantém portais modernos de dados abertos e a Rede Nacional de Dados em Saúde (RNDS).

## OpenDataSUS

- URL: https://opendatasus.saude.gov.br.
- Portal baseado em **CKAN** (padrão de dados abertos).
- Distribui datasets em CSV, JSON, Parquet.
- Atualização e curadoria melhor que o FTP legado.
- Datasets notáveis (amostra — `[TODO/RESEARCH: inventário completo atualizado 2026]`):
  - SRAG (Síndrome Respiratória Aguda Grave).
  - COVID-19 (vacinação, casos, óbitos por município).
  - e-SUS Notifica.
  - Farmácia Popular.
  - SINAN-dengue / arboviroses.

### API CKAN

```
https://opendatasus.saude.gov.br/api/3/action/package_list
https://opendatasus.saude.gov.br/api/3/action/package_show?id=srag-2023
```

Permite automação: listar pacotes, baixar recursos por URL.

## RNDS — Rede Nacional de Dados em Saúde

- Instituída pela **Portaria GM/MS 1.434/2020**.
- Plataforma FHIR R4 com perfis brasileiros.
- Objetivo: interoperar dados de saúde de toda a rede pública e privada.
- **Não é** portal de dados abertos — exige autenticação (certificado ICP-Brasil + OAuth2) e base legal LGPD.
- Módulos operacionais (conforme adesão):
  - Vacinação.
  - Laboratório (RELATÓRIO DE EXAMES).
  - Atenção primária (e-SUS APS).
  - Prescrição eletrônica.
  - Encaminhamento.
- `[TODO/RESEARCH: módulos ativos + cobertura municipal 2026]`.

## PNCDs — Políticas Nacionais de Controle

Sigla genérica para Programas/Políticas Nacionais (ex.: PNCD-Dengue, PNCD-Hanseníase). Cada um publica dados gerenciais e indicadores. Frequentemente ancorados em SINAN + inquéritos específicos.

## Dados do IBGE para denominador

Sem denominador populacional, taxa não se calcula.

- **Censo 2022**: base populacional oficial.
- **Projeções intercensitárias**: `ftp.ibge.gov.br`.
- **Pesquisa Nacional de Saúde (PNS)**: inquéritos 2013, 2019 + edições subsequentes — variáveis de morbidade, estilo de vida.
- **PNAD Contínua**: trabalho, renda (confundidores socioeconômicos).

## Dados ANS (saúde suplementar)

- Portal ANS — Dados Abertos: https://dados.ans.gov.br.
- **Beneficiários** por operadora, faixa etária, plano.
- **Produtos** registrados.
- **TISS** — indicadores de uso.
- **Reclamações** por operadora.
- Utilidade pericial: dimensionar carteira, checar regularidade da operadora ré.

## ANVISA (medicamentos/produtos)

- VIGIMED: farmacovigilância (eventos adversos).
- Notivisa: notificações de eventos adversos e queixas técnicas.
- Dados abertos ANVISA: registros de produtos, bulas, rotulagem.

## Portais regionais

- **DataTerra/BI municipal**: alguns municípios publicam BI de saúde (SMS-SP, SMS-BH).
- **Secretarias estaduais**: SES-MG, SES-SP publicam painéis próprios.

## Como localizar dataset certo

1. Formular pergunta com denominador claro (prevalência? incidência? tempo de internação?).
2. Consultar **OpenDataSUS** e TabNet.
3. Se atenção primária → e-SUS APS.
4. Se suplementar → ANS.
5. Se farmacovigilância → ANVISA.
6. Para validade → cruzar com dois sistemas quando possível.

## Cuidados LGPD

- Dados abertos agregados são **livres de uso**.
- Microdados do DATASUS são anonimizados, mas **risco de reidentificação** em subgrupos raros existe.
- Publicação pericial deve sempre anonimizar (sem CPF, endereço; idade em faixa se n pequeno).
- RNDS: acesso sob base legal específica (artigo 11, II, "f" LGPD — proteção da vida / tutela da saúde).

## Exemplos de perguntas periciais

- "Qual a mortalidade hospitalar por sepse em hospital X no ano Y?" → SIH + CNES.
- "Qual a taxa de cesárea do município?" → SINASC.
- "Eventos adversos de fármaco Z em 2024?" → VIGIMED.
- "Cobertura vacinal DTP no município?" → SI-PNI.
- "Quantas internações por reação transfusional?" → SIH com CID-10 específico.
