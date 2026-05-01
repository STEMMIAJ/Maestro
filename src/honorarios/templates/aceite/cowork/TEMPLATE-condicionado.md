---
subtipo: aceite
variante: condicionado
descricao: Aceite que ratifica honorários JÁ FIXADOS pelo juiz em decisão anterior
fonte_original: _fonte-originais-perito/Petição de Aceite - 0038122-07.2012.8.13.0396 - Mantena.docx
duracao_bloco: 15min
variaveis_requeridas:
  - juizo.numero_vara
  - juizo.materias
  - juizo.comarca
  - juizo.uf
  - processo.cnj
  - atos_anteriores.ids
  - honorarios.valor_numerico     # ex: 1500.00
  - honorarios.valor_extenso      # ex: "um mil e quinhentos reais"
  - data.por_extenso
timbrado:
  topo_pagina: ../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

MANIFESTAÇÃO – ACEITE DE ENCARGO E HONORÁRIOS

Meritíssimo Juiz,

Em atenção {{#lista:atos_anteriores.ids:prefixo="à(s) decisão/intimação de ID ":separador=" e ID "}}, venho ratificar meu aceite dos encargos e honorários periciais, já fixados em R$ {{honorarios.valor_numerico}} ({{honorarios.valor_extenso}}). Aguardo os trâmites necessários para prosseguir com o agendamento da perícia médica, caso não haja suspeição ou impedimento sobre minha atuação.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares - MG.
