---
subtipo: escusa
variante: padrao
descricao: Recusa de nomeação por impedimento, suspeição ou motivo técnico (art. 157 CPC)
fonte_original: (sem DOCX de referência — montado do estilo-guia)
duracao_bloco: 10min
variaveis_requeridas:
  - juizo.numero_vara
  - juizo.materias
  - juizo.comarca
  - juizo.uf
  - processo.cnj
  - atos_anteriores.ids
  - escusa.motivo
  - escusa.fundamento_legal
variaveis_opcionais:
  - escusa.detalhamento      # parágrafo extra opcional
timbrado:
  topo_pagina: ../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

MANIFESTAÇÃO – ESCUSA DE NOMEAÇÃO

Meritíssimo Juiz,

Em atenção {{#lista:atos_anteriores.ids:prefixo="à intimação de ID ":separador=" e ID "}}, venho, com fundamento em {{escusa.fundamento_legal}}, apresentar ESCUSA da nomeação para atuar como perito judicial nestes autos, pelos motivos que passo a expor.

{{escusa.motivo}}

{{#se:escusa.detalhamento}}{{escusa.detalhamento}}
{{/se}}Requer-se, portanto, que este Juízo acolha a presente escusa e designe outro profissional para a realização da perícia, dispensando-me do encargo.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares - MG.
