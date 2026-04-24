---
subtipo: proposta-honorarios
classe: civel-dano-pessoal
descricao: Proposta de honorários periciais em ação cível (dano pessoal/incapacidade)
fonte_original: (montado do estilo-guia + Resolução CNJ 233/2016)
duracao_bloco: 20min
variaveis_requeridas:
  - juizo.numero_vara
  - juizo.materias
  - juizo.comarca
  - juizo.uf
  - processo.cnj
  - atos_anteriores.ids
  - honorarios.valor_numerico
  - honorarios.valor_extenso
variaveis_opcionais:
  - honorarios.justificativa_complexidade     # {{#se:}}: bloco extra se complexidade alta
  - partes.autor.beneficio_justica_gratuita   # {{#se-nao:}}: se NÃO for gratuidade, cita depósito
timbrado:
  topo_pagina: ../../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

MANIFESTAÇÃO – PROPOSTA DE HONORÁRIOS PERICIAIS

Meritíssimo Juiz,

Em atenção {{#lista:atos_anteriores.ids:prefixo="à intimação de ID ":separador=" e ID "}}, após análise preliminar dos autos e considerando a natureza do exame pericial requerido, venho apresentar PROPOSTA DE HONORÁRIOS PERICIAIS.

**Valor proposto:** R$ {{honorarios.valor_numerico}} ({{honorarios.valor_extenso}}).

**Fundamentação:** a proposta observa os critérios do art. 465, §3º, do CPC e da Resolução CNJ nº 233/2016, levando em conta a complexidade do exame, o tempo necessário para análise dos autos e elaboração do laudo, o deslocamento, a responsabilidade técnica e a praxe da região.

{{#se:honorarios.justificativa_complexidade}}**Justificativa de complexidade:** {{honorarios.justificativa_complexidade}}

{{/se}}{{#se-nao:partes.autor.beneficio_justica_gratuita}}Requer-se que a parte interessada seja intimada para depositar o valor em juízo, nos termos do art. 95 do CPC, com expedição de alvará em favor do subscritor após a realização do encargo.

{{/se-nao}}{{#se:partes.autor.beneficio_justica_gratuita}}Tratando-se de beneficiário da justiça gratuita, requer-se a fixação dos honorários observando-se os limites da Resolução CSJT/CNJ aplicável, com pagamento pelo erário ou nos moldes do art. 95, §3º, II do CPC.

{{/se}}Caso a presente proposta seja aceita, comprometo-me a realizar o exame pericial e entregar o laudo no prazo determinado por Vossa Excelência. Havendo discordância, coloco-me à disposição para adequação.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares - MG.
