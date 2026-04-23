---
titulo: "Tríade CIA — Confidencialidade, Integridade, Disponibilidade"
bloco: "05_security_and_governance"
tipo: "conceito"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Tríade CIA

A tríade CIA é o alicerce da segurança da informação. Qualquer controle técnico, política ou decisão arquitetural deve ser justificado contra ao menos um dos três pilares.

## Confidencialidade

Garantia de que o dado só é acessível a quem tem direito. Para o perito, confidencialidade abrange:

- Dados clínicos do periciando (prontuário, exames, laudos psiquiátricos).
- Segredo médico (CFM 1.605/2000).
- Segredo de justiça marcado nos autos do PJe.
- Identidade de terceiros (filhos, cônjuges, testemunhas).

Controles típicos: criptografia em repouso (FileVault, LUKS), criptografia em trânsito (TLS 1.3), controle de acesso (IAM, Keychain), MFA.

## Integridade

Garantia de que o dado não foi alterado de forma não autorizada. Na prática pericial:

- Hash SHA-256 do laudo no momento da assinatura digital.
- Cadeia de custódia de exames físicos recebidos.
- Logs de alteração (quem editou, quando, o quê).

Controles: assinatura digital ICP-Brasil, checksums, versionamento Git, WORM storage para provas digitais.

## Disponibilidade

Garantia de que o sistema está acessível quando necessário. Prazo processual não espera.

- Backup 3-2-1 para laudos em produção.
- Redundância de internet no dia da audiência.
- Monitoramento de serviços críticos (PJe, DataJud).

Controles: backup automático, failover, SLA de provedores, redundância geográfica.

## Trade-off entre os três

Aumentar um pilar frequentemente reduz outro. Criptografar tudo com chave perdida = zero disponibilidade. Backup aberto em nuvem pública = integridade alta mas confidencialidade nula. O perito decide o balanço caso a caso, documentando a decisão.

## Aplicação pericial concreta

| Ativo | C | I | D |
|-------|---|---|---|
| Laudo assinado | Alta | Altíssima | Média |
| Fotos de exame físico | Alta | Alta | Baixa |
| Base de processos ativos | Alta | Alta | Alta |
| Scripts de automação | Baixa | Alta | Média |

## Referência cruzada

- `ameacas_e_vetores.md` — o que ataca cada pilar
- `seguranca_por_camadas.md` — como defender em profundidade
- `../compliance_privacy/lgpd_para_medico_perito.md` — obrigação legal sobre C

[TODO/RESEARCH: verificar se CFM publicou nova resolução 2026 sobre prontuário digital]
