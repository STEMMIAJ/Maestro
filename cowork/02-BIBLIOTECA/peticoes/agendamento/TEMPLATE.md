---
subtipo: agendamento
variante: consultorio-padrao
descricao: Comunica ao juízo data/horário e local da perícia (consultório padrão)
fonte_original: _fonte-originais-perito/Agendamento de Perícia - MODELO - cópia.docx
duracao_bloco: 15min
variaveis_requeridas:
  - juizo.numero_vara
  - juizo.materias
  - juizo.comarca
  - juizo.uf
  - processo.cnj
  - atos_anteriores.ids           # intimação que agendou/determinou perícia
  - pericia.data                  # ex: "15/05/2026"
  - pericia.dia_semana            # ex: "QUINTA-FEIRA"
  - pericia.hora                  # ex: "15h30min"
  - ano_assinatura                # ex: "2026"
timbrado:
  topo_pagina: ../../03-IDENTIDADE/timbrado/timbrado-topo-pagina.png
  rodape_texto: "Empresarial Maria Costa, Rua João Pinheiro, 531, Sala 207 – Centro – Governador Valadares/MG | (33) 99900-1122 | perito@drjesus.com.br"
---

AO JUÍZO DA {{juizo.numero_vara}}ª VARA {{juizo.materias}} DA COMARCA DE {{juizo.comarca}} – {{juizo.uf}}

Processo nº: {{processo.cnj}}

MANIFESTAÇÃO – AGENDAMENTO DE PERÍCIA MÉDICA

Em atenção {{#lista:atos_anteriores.ids:prefixo="à intimação de ID ":separador=" e ID "}}, indico que a perícia médica será realizada em meu consultório, conforme segue:

**DATA E HORÁRIO:** {{pericia.data}} ({{pericia.dia_semana}}), às {{pericia.hora}}.

**LOCAL:** Rua João Pinheiro, número 531, Centro, Edifício Empresarial Maria Costa – Sala 207, 2º andar (última sala do corredor à esquerda) – Governador Valadares – MG

**Referências:** prédio de esquina entre a Rua Artur Bernardes (onde se encontra o ponto de ônibus) e a Rua João Pinheiro (sendo o prédio em frente ao muro lateral do Colégio Imaculada).

Permaneço à disposição do Juízo para quaisquer reagendamentos de data e/ou horário se necessário.

Termos em que,
Pede deferimento.

Dr. Jésus Eduardo Nolêto da Penha
Médico - Perito Judicial – CRM-MG 92.148
Membro da ABMLPM - Associação Brasileira de Medicina Legal e Perícia Médica

{{data.por_extenso}}, Governador Valadares - MG.
