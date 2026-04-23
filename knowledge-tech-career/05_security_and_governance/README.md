---
titulo: Seguranca e Governanca
bloco: 05_security_and_governance
versao: 0.1
status: esqueleto
ultima_atualizacao: 2026-04-23
---

# 05 — Segurança e Governança

## Definição do domínio

Segurança é a disciplina de reduzir probabilidade e impacto de acesso, alteração ou perda indevida de informação. Governança é o conjunto de regras, papéis e evidências que tornam essa disciplina auditável. Este bloco cobre fundamentos de infosec, gestão de segredos e acesso, backup e recuperação de desastre, compliance (LGPD, CFM, resolução 2.217/2018), privacidade e resposta a incidente.

Ênfase deliberada: o sistema manipula dados médicos sensíveis (laudos, exames, prontuários de periciados) e material judicial sigiloso. Não é um bloco de "boas práticas gerais" — é requisito legal (LGPD art. 11, sigilo médico, segredo de justiça).

O objetivo é dar ao operador condições de justificar, por escrito, por que o sistema é seguro o suficiente para o tipo de dado que guarda, e ter plano pronto para quando falhar.

## Subdomínios

- `infosec_basics/` — CIA (confidencialidade, integridade, disponibilidade), modelo de ameaça, superfície de ataque, criptografia simétrica/assimétrica, hash.
- `secrets_access/` — gestão de credenciais (keychain, 1Password, vault), chaves SSH, princípio do menor privilégio, rotação.
- `backups_disaster_recovery/` — 3-2-1, RPO/RTO, teste de restore, Time Machine, backup offsite criptografado.
- `compliance_privacy/` — LGPD, CFM 2.217/2018, segredo de justiça, base legal, DPIA, anonimização/pseudonimização.
- `incident_response/` — detecção, contenção, erradicação, recuperação, comunicação, lições aprendidas.

## Perguntas que este bloco responde

1. Qual a base legal para tratar dado médico de periciado?
2. Onde guardar a chave da API sem commitar no Git?
3. Um backup que nunca foi restaurado existe?
4. O que fazer nas primeiras 2 horas de um vazamento?
5. Quando anonimizar e quando pseudonimizar basta?
6. Como auditar quem acessou qual laudo?
7. Qual a diferença entre criptografia em trânsito e em repouso?
8. O que precisa estar num relatório de incidente para ANPD?

## Como coletar conteúdo para este bloco

- Lei 13.709/2018 (LGPD) e guias orientativos da ANPD.
- Resoluções CFM pertinentes (2.217/2018, 2.299/2021).
- OWASP Top 10, CIS Controls, NIST Cybersecurity Framework 2.0.
- "Security Engineering" (Anderson) como referência profunda.
- Documentação oficial de ferramentas usadas (1Password, macOS keychain, GPG).
- Casos reais: post-mortem de incidentes públicos (serasa, grandes hospitais).

## Critérios de qualidade das fontes

Seguir `00_governance/source_quality_rules.md`. Em segurança, priorizar fonte normativa (lei, resolução, NIST, OWASP) e evidência de auditoria. Registrar versão do controle (CIS v8.1, NIST CSF 2.0). Evitar FUD de vendor.

## Exemplos de artefatos que podem entrar

- Modelo de ameaça STRIDE do sistema pericial.
- Playbook de resposta a incidente com vazamento de laudo.
- Procedimento de teste de restore trimestral.
- Matriz de dados (tipo, base legal, retenção, criptografia).
- Checklist LGPD para operador pericial autônomo.
- Procedimento de rotação de chave DataJud/PJe.

## Interseções com outros blocos

- `01_ti_foundations` — redes e SO definem superfície.
- `03_web_development` — autenticação/deploy são superfícies críticas.
- `04_systems_architecture` — segurança é requisito de arquitetura.
- `07_health_data` — dados clínicos têm tratamento privilegiado em LGPD art. 11.
- `09_legal_medical_integration` — sigilo profissional + segredo de justiça se cruzam aqui.
- `14_automation` — scripts que manipulam segredo ou dado sensível precisam deste bloco.
