---
titulo: "LGPD para Médico Perito"
bloco: "05_security_and_governance"
tipo: "compliance"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 10
---

# LGPD para Médico Perito

Lei 13.709/2018 aplica-se ao perito judicial no tratamento de dados pessoais e sensíveis dos periciandos. Não há isenção por atuação judicial — há base legal específica.

## Definições essenciais

- **Titular**: pessoa natural a quem se referem os dados (o periciando).
- **Controlador**: quem decide sobre o tratamento (o perito judicial, em relação ao laudo).
- **Operador**: quem trata por conta do controlador (secretária, nuvem, software).
- **Dado pessoal**: qualquer informação que identifica pessoa natural.
- **Dado sensível**: saúde, biometria, genético, orientação sexual, origem racial, convicção (art. 5º, II). **Dado pericial médico é sensível.**

## Bases legais aplicáveis ao perito

Art. 7º (dados pessoais) e art. 11 (dados sensíveis) listam bases. Para o perito:

### Para dados sensíveis (art. 11)

- **II, "a"**: cumprimento de obrigação legal ou regulatória. Perícia judicial nomeada pelo juiz = cumprimento de dever legal.
- **II, "d"**: exercício regular de direitos em processo judicial.
- **II, "f"**: tutela da saúde, em procedimento realizado por profissional de saúde.

Consentimento **não é** base padrão: o periciando não tem opção de recusar em perícia judicial.

### Para dados pessoais comuns (endereço, profissão do periciando)

- Art. 7º, II: cumprimento de obrigação legal.
- Art. 7º, VI: exercício regular de direito em processo judicial.

## Ciclo de vida do dado pericial

1. **Coleta**: autos do processo, exame físico, exames complementares anexados.
2. **Retenção**: durante elaboração do laudo e período de possível complementação.
3. **Tratamento**: análise, correlação clínica, redação.
4. **Compartilhamento**: protocolo do laudo no juízo (destinatário legítimo).
5. **Armazenamento pós-entrega**: retenção mínima para atender complementações, impugnações, recursos, ações de responsabilidade. Usualmente 20 anos (prazo prescricional).
6. **Descarte**: secure delete quando prazo expirar.

## Direitos do titular (art. 18)

O periciando pode pedir:

- Confirmação da existência de tratamento.
- Acesso aos dados.
- Correção de dados incompletos, inexatos ou desatualizados.
- Portabilidade.
- Eliminação de dados tratados com consentimento.
- Informação sobre compartilhamento.
- Revogação de consentimento.

**Limite**: direitos cedem quando a base legal é cumprimento de obrigação legal ou exercício de direito em processo. Não se apaga laudo pericial porque periciando pediu — há obrigação de retenção.

Pedido deve ser respondido em até 15 dias.

## Obrigações operacionais do perito

### Medidas de segurança (art. 46)

- Criptografia em repouso (FileVault) e trânsito (TLS).
- Controle de acesso (senha forte, MFA).
- Log de acesso ao laudo e exames.
- Backup cifrado.
- Descarte seguro.

### Registro de operações de tratamento (art. 37)

Documento interno listando:

- Finalidades do tratamento.
- Bases legais.
- Categorias de titulares e dados.
- Medidas de segurança.
- Prazos de retenção.

Modelo em `~/Desktop/STEMMIA Dexter/00-CONTROLE/LGPD-registro-tratamento.md` [TODO/RESEARCH: confirmar existência].

### Relatório de Impacto à Proteção de Dados (RIPD/DPIA)

Obrigatório quando tratamento apresenta alto risco. Perícia psiquiátrica com periciandos vulneráveis, perícias envolvendo menores, bases biométricas — justificam RIPD.

### Encarregado (DPO)

Art. 41. Exigido para controladores. ANPD pode dispensar pequeno porte. Perito pessoa física pode indicar a si mesmo ou terceirizar. Dado do DPO público no site profissional.

### Notificação de incidente (art. 48)

Vazamento com risco a direitos do titular → comunicar ANPD e titulares em prazo razoável. Ver `../incident_response/comunicacao_ANPD_e_titular.md`.

## Interação com CFM

LGPD **não revoga** segredo médico. Os dois regimes se somam: segredo médico é barreira adicional ao compartilhamento, mesmo quando LGPD permitiria. Ver `sigilo_medico_cfm.md`.

## Interação com segredo de justiça

Processo com segredo exige marcação e controle extra de acesso. Ver `segredo_de_justica_pje.md`.

## Transferência internacional

Cloud com servidor nos EUA (Google, OpenAI, Anthropic) = transferência internacional. Art. 33 exige base legal. Para dado sensível pericial, evitar. Usar instâncias BR quando disponíveis, anonimizar antes de processar em IA estrangeira.

## Sanções

Multa até 2% do faturamento, limitada a R$ 50 milhões por infração. Advertência, publicização da infração, bloqueio dos dados. Responsabilidade civil reparatória independente da ANPD.

## Anti-padrões documentados

- Laudo em Google Drive pessoal sem cifra extra.
- Envio de exame por WhatsApp.
- Chamada em IA sem anonimização mínima.
- Pendrive com laudos perdido no fórum.
- Secretária com acesso à pasta inteira sem log.

## Referência cruzada

- `sigilo_medico_cfm.md`
- `segredo_de_justica_pje.md`
- `../incident_response/comunicacao_ANPD_e_titular.md`
- `../secrets_access/gerenciamento_de_segredos.md`

[TODO/RESEARCH: verificar resoluções ANPD de 2026 sobre dado sensível em saúde]
