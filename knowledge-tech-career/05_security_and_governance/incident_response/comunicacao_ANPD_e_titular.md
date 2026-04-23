---
titulo: "Comunicação de Incidente à ANPD e aos Titulares"
bloco: "05_security_and_governance"
tipo: "compliance"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "parcial"
tempo_leitura_min: 6
---

# Comunicação de Incidente à ANPD e aos Titulares

Art. 48 da LGPD impõe ao controlador comunicar à ANPD e aos titulares afetados quando o incidente puder acarretar risco ou dano relevante.

## Critério de notificação

Nem todo incidente exige notificação. A avaliação pondera:

- Natureza e categoria do dado (sensível vs comum).
- Quantidade de titulares.
- Facilidade de identificação.
- Probabilidade concreta de dano (financeiro, moral, discriminação).
- Medidas de mitigação já adotadas (dado estava criptografado?).

Dado pericial sensível vazado em claro = notificação padrão.

## Prazo

Lei fala em "prazo razoável" (art. 48, §1º). ANPD regulou via Resolução CD/ANPD nº 15/2024 (ou posterior — verificar vigente):

- Comunicação inicial: em até **3 dias úteis** do conhecimento.
- Comunicação complementar: após investigação, com detalhes finais.

[TODO/RESEARCH: confirmar resolução vigente em 2026 e prazo atualizado — consultar portal ANPD]

## Conteúdo mínimo da comunicação à ANPD

Art. 48, §1º, I a V:

1. Descrição da natureza dos dados pessoais afetados.
2. Informações sobre os titulares envolvidos (quantidade, categoria).
3. Medidas técnicas e de segurança usadas para proteger os dados.
4. Riscos relacionados ao incidente.
5. Motivos da demora, se foi o caso.
6. Medidas adotadas para reverter ou mitigar os efeitos.

Formato: formulário eletrônico no portal da ANPD.

## Conteúdo mínimo ao titular

Comunicação clara, individualizada quando possível:

- Que o incidente ocorreu.
- Que dados foram afetados (especificamente).
- Quando ocorreu.
- Riscos prováveis.
- Medidas já tomadas pelo controlador.
- Recomendações ao titular (trocar senha, monitorar cartão, etc.).
- Canal de contato para dúvidas.

Canal preferencial: e-mail formal com confirmação de recebimento. Evitar SMS ou WhatsApp como único canal.

## Casos especiais no fluxo pericial

### Segredo de justiça

Se o incidente envolve processo sob segredo, comunicar também:

- Juízo do processo, com a brevidade possível.
- Partes via advogados, respeitando o rito.

### Segredo médico

Possíveis desdobramentos éticos:

- Autoavaliação ética: houve violação do sigilo? Se sim, CRM pode ser comunicado.
- Avaliação de responsabilidade civil.

### Quando a vítima é vulnerável

Menor, pessoa com transtorno psíquico, idoso. Comunicação via representante legal, sob apoio e cuidado redobrado.

## Modelo de comunicação inicial interna

```
Incidente ID: INC-2026-001
Data do evento: 2026-04-22 16:30
Data do conhecimento: 2026-04-23 09:00
Descrição: [fato objetivo]
Dados afetados: [categorias e quantidade]
Titulares: [nº aproximado, categorias]
Origem: [causa raiz conhecida ou em investigação]
Medidas imediatas: [contenção feita]
Notificações pendentes: ANPD, titulares, juízo?
Responsável pela resposta: [nome]
```

Salvar em `~/Desktop/STEMMIA Dexter/00-CONTROLE/incidentes/INC-2026-001.md`.

## Modelo ao titular (esqueleto)

```
Prezado(a) [nome],

Em [data], identificamos um incidente de segurança que envolveu dados
pessoais seus sob tratamento deste perito em razão de processo judicial
em que V.Sa. figura como periciando.

Dados afetados: [descrição].
Medidas adotadas: [contenção, análise, notificação à ANPD].
Recomendações: [ações práticas].

Canal de atendimento: [e-mail, telefone].

Atenciosamente,
Dr. Jesus — Perito Judicial
CRM-MG XXXXX
```

## Registro interno obrigatório

Mesmo quando o incidente não exige notificação externa, registrar:

- Data, descrição, avaliação, decisão de não notificar, justificativa.
- ANPD pode questionar depois — o registro é defesa.

## Anti-padrões

- Esconder o incidente.
- Notificar informalmente e sem registro.
- Demorar além do prazo regulamentar.
- Comunicar sem plano claro de mitigação em curso.

## Referência cruzada

- `playbook_incidente_minimo.md`
- `../compliance_privacy/lgpd_para_medico_perito.md`
- `../compliance_privacy/segredo_de_justica_pje.md`

[TODO/RESEARCH: verificar resoluções ANPD 2026 e formulário online vigente]
