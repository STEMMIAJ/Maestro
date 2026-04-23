---
titulo: "Estratégia 3-2-1 de Backup"
bloco: "05_security_and_governance"
tipo: "pratica"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Estratégia 3-2-1

Regra clássica de backup:

- **3** cópias totais dos dados (1 original + 2 backups).
- **2** mídias diferentes (tipos distintos de armazenamento).
- **1** cópia offsite (em local físico distinto).

Evolução moderna: 3-2-1-1-0 — adiciona 1 cópia offline/imutável e 0 erros na restauração testada.

## Por que 3-2-1 funciona

Cada número mitiga uma classe de falha:

- 3 cópias: resistem a corrupção silenciosa, exclusão acidental, ransomware parcial.
- 2 mídias: resistem a falha de tecnologia (HD magnético + SSD, disco + nuvem).
- 1 offsite: resiste a incêndio, roubo, enchente, apreensão física do escritório.

Falhar qualquer critério abre vetor concreto. Perito sem offsite que sofre incêndio perde laudos em andamento e responde por atraso processual.

## Aplicação pericial

### Ativos críticos

1. Laudos concluídos assinados (pasta `10-PERICIA/laudos/assinados/`).
2. Laudos em andamento (drafts, anexos, fotos de exame).
3. Base de processos (FICHA.json, banco SQLite Dexter).
4. Scripts e automações (`~/Desktop/STEMMIA Dexter/src/`).
5. Configurações Claude Code (`~/.claude/`).
6. Chaves ICP e certificados.

### Mapeamento 3-2-1

| Cópia | Mídia | Onde | Frequência |
|-------|-------|------|-----------|
| Original | SSD interno Mac | Desktop/STEMMIA Dexter | contínua |
| Backup 1 | HD externo USB | Time Machine local | horária |
| Backup 2 | Nuvem cifrada | Backblaze B2 / iCloud / Arq | diária |
| Offline | SSD USB em cofre | Desconectado | semanal |

3 cópias (SSD + HD + nuvem) em 2 mídias (local + remoto) com 1 offsite (nuvem). O SSD offline é o "1" do 3-2-1-1 — imune a ransomware porque desconectado.

## Criptografia obrigatória

Dado pericial é sensível (art. 11 LGPD). Todo backup **cifrado antes de sair do disco**.

- Time Machine: ativar "Encrypt backups" na configuração inicial.
- Nuvem: Arq, Restic, Borg. Nunca confiar só na criptografia do provedor.
- SSD offline: APFS Encrypted, senha forte em gestor.

## Cadência

| Ativo | RPO aceitável | RTO aceitável |
|-------|--------------|---------------|
| Laudo em andamento | 1 hora | 4 horas |
| Laudo assinado final | 24 horas | 24 horas |
| Scripts | 24 horas | imediato (Git) |
| Config Claude | 24 horas | 1 hora |

RPO = quanto dado aceita perder. RTO = quanto tempo aceita ficar sem.

## Retenção

- Laudos: 20 anos mínimo (prazo prescricional estendido).
- Drafts: 5 anos.
- Scripts: versionamento Git indefinido.
- Backups diários: 30 dias; semanais: 12 semanas; mensais: 24 meses.

## Integridade

Backup que nunca foi testado não é backup. Ver `restauracao_e_teste.md`.

## Referência cruzada

- `time_machine_macos.md`
- `restauracao_e_teste.md`
- `../compliance_privacy/lgpd_para_medico_perito.md`
