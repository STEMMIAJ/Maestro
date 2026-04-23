---
titulo: "Sigilo Médico e CFM — Aplicação Pericial"
bloco: "05_security_and_governance"
tipo: "compliance"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Sigilo Médico e CFM na Prática Pericial

O segredo médico é dever ético previsto no Código de Ética Médica (CEM) e reforçado por resoluções do Conselho Federal de Medicina. Em perícia judicial há peculiaridades: o perito atua em função legal, mas o segredo não desaparece — é redimensionado.

## Fontes normativas principais

### Resolução CFM 1.605/2000

Regula o fornecimento de prontuários e documentos médicos a autoridades. Princípios:

- Prontuário pertence ao paciente; custódia é do médico/instituição.
- Autoridade judicial pode requisitar, mas a forma deve preservar sigilo (autos sob segredo, lacre, perito como intermediário).
- Médico assistente não entrega prontuário a parte da ação por ofício direto — exige ordem judicial.

Consequência pericial: ao receber prontuário nos autos, o perito é guardião de dado sensível sob regime especial.

### Resolução CFM 1.931/2009 — Código de Ética Médica

Capítulo IX — Sigilo Profissional. Artigos 73-79. Pontos centrais:

- **Art. 73**: vedado revelar fato sigiloso, salvo por justa causa, dever legal, consentimento expresso do paciente.
- **Art. 76**: vedado revelar em perícia administrativa/judicial fato que o paciente/periciando tenha exposto espontaneamente, quando não relacionado à causa.
- **Art. 77**: vedado prestar informações a empresa seguradora fora do contexto do laudo específico.

Para o perito: **revelar apenas o necessário e suficiente à resposta dos quesitos**. Comentário íntimo do periciando sobre relação familiar, não vinculado à patologia em discussão, não entra no laudo.

### Resolução CFM 2.217/2018

Altera o CEM. Reforça dever de sigilo em meios eletrônicos: prontuário eletrônico, troca por e-mail, armazenamento em nuvem. Exige medidas técnicas adequadas. Base ética para os controles LGPD.

### Resoluções sobre perícia

- **CFM 2.056/2013 e atualizações**: normas sobre perícias médicas, ratificando o dever de sigilo sobre o material pericial. [TODO/RESEARCH: verificar resolução vigente em 2026]
- **CFM 2.057/2013**: perícia psiquiátrica.

## Segredo médico vs perícia judicial — como convivem

Base ética: o perito tem **dever legal** de responder aos quesitos. Isso afasta o sigilo em relação ao conteúdo necessário para responder. Porém:

1. O laudo vai para autos, que podem ter segredo de justiça.
2. O material bruto (exames, vídeos, gravações de anamnese) nunca deve circular fora do fluxo processual.
3. Terceiros (secretária, IA externa, ferramenta de transcrição) são "operadores" sob LGPD e precisam estar autorizados e vinculados a sigilo contratual.

## Prontuário médico recebido em autos

Quando o perito recebe prontuário de terceiro hospital ou colega:

- Uso exclusivo para fins da perícia.
- Citação pontual no laudo quando essencial; evitar transcrição extensa.
- Guardado pelo prazo legal junto aos demais documentos periciais.
- Descarte seguro ao fim do prazo.

## Comunicação com periciando

- Não fornecer diagnóstico ou orientação terapêutica — não é consulta. A perícia não substitui o médico assistente.
- Documentar no laudo recomendação genérica de seguimento com equipe assistencial.
- Guardar identidade do periciando com o mesmo rigor de prontuário.

## Relato e anamnese

- O que o periciando relatou em anamnese pericial **é** parte do material pericial, não prontuário clínico.
- Revelar ao juízo o que o periciando narrou sobre os fatos é permitido se relevante ao quesito.
- Revelar dado íntimo irrelevante à causa viola art. 76 CEM.

## IA e transcrição

Usar IA para transcrever anamnese ou sumarizar laudos:

- Modelo local (Whisper local, LLM on-device) é preferível.
- Serviço em nuvem exige contrato de operador sob LGPD + sem retenção para treino + servidor BR quando possível.
- Anonimização mínima antes de envio.

## Violação de sigilo — sanções

- Ética: advertência a cassação pelo CRM/CFM (art. 22 do Código de Processo Ético-Profissional).
- Penal: art. 154 CP — revelação de segredo profissional.
- Civil: reparação por dano moral.
- Administrativa LGPD: sanções ANPD.

## Fluxo mínimo pericial compatível

1. Receber autos / prontuário → armazenar em pasta cifrada.
2. Anamnese gravada (com anuência) → transcrição em ferramenta com contrato adequado ou local.
3. Laudo responde quesitos com o mínimo suficiente.
4. Material bruto retido sob chave pelo prazo legal.
5. Descarte seguro no fim do prazo.

## Referência cruzada

- `lgpd_para_medico_perito.md`
- `segredo_de_justica_pje.md`
- `../incident_response/playbook_incidente_minimo.md`

[TODO/RESEARCH: CFM 2.056/2013 foi substituída? Conferir Portal CFM em 2026]
