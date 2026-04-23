---
titulo: "Playbook Mínimo de Resposta a Incidente"
bloco: "05_security_and_governance"
tipo: "runbook"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Playbook Mínimo de Resposta a Incidente

Incidente é evento que comprometeu (ou pode ter comprometido) confidencialidade, integridade ou disponibilidade. Para o perito autônomo, sem equipe de SOC, o objetivo é: contenção rápida + preservação de evidência + notificação quando obrigatório.

## Fases (NIST SP 800-61)

1. Preparação
2. Detecção e análise
3. Contenção
4. Erradicação
5. Recuperação
6. Lições aprendidas

## 1. Preparação (pré-incidente)

Ter pronto antes que aconteça:

- Contato da ANPD (canal de comunicação de incidentes).
- Contato de advogado especializado em LGPD.
- Contato do TI/consultor de segurança.
- Backup testado e restaurável.
- Inventário de ativos: o que existe, onde, quão sensível.
- Este próprio documento em local imprimível.

## 2. Detecção e análise

Sinais típicos:

- Laudo sumiu da pasta.
- Mac apresentou tela de ransomware.
- E-mail recebido com ameaça de vazamento.
- Login estranho reportado pelo provedor (Google, Apple).
- Comportamento anormal de processo no Activity Monitor.
- Pendrive perdido com dados sensíveis.
- Compartilhamento indevido por terceiro (secretária/estagiária).

Avaliar:

- O que foi afetado?
- Quem tem acesso agora?
- Há dado sensível envolvido?
- Há titulares identificáveis?
- Há risco de dano material ou moral ao titular?

Documentar desde o primeiro minuto: data/hora, descrição, evidência preservada.

## 3. Contenção

Objetivo: parar o sangramento sem destruir evidência.

### Ação imediata comum

- Desconectar Mac da internet (Wi-Fi off, cabo removido).
- Trocar senha da conta comprometida (de outro dispositivo limpo).
- Revogar tokens/chaves comprometidos (API, OAuth, 1Password).
- Bloquear cartão se envolvido.
- Tirar YubiKey/chave física do dispositivo.
- Não desligar o computador (perde memória volátil com pistas).

### Isolamento

- Mover Mac para rede isolada ou deixar offline.
- Se suspeita de ransomware: **não pagar**, **não reiniciar**, fotografar tela.

## 4. Erradicação

Remover a causa raiz:

- Malware: reinstalação limpa do SO é padrão-ouro. Scanner (Malwarebytes) é paliativo.
- Acesso indevido: revogar credencial, rotacionar tudo relacionado.
- Dispositivo perdido: ativar Find My + remote wipe.
- Compromisso de e-mail: revogar app passwords, revisar regras de filtro maliciosas criadas, verificar desvios.

Preservar cópia forense antes (clonagem de disco com `dd` ou disk imager) se houver chance de ação penal ou cível.

## 5. Recuperação

Voltar ao estado operacional seguro:

- Restaurar dados de backup testado (ver `../backups_disaster_recovery/restauracao_e_teste.md`).
- Validar integridade por hash.
- Monitorar por 30 dias: logins, e-mail, contas financeiras, alertas ANPD.
- Reemitir laudos se integridade comprometida.

## 6. Lições aprendidas

Registrar em `~/Desktop/STEMMIA Dexter/00-CONTROLE/incidentes/<data>.md`:

- Linha do tempo.
- Causa raiz.
- O que funcionou.
- O que falhou.
- Ação corretiva permanente (mudar política, adicionar controle, treinamento).

Sem essa etapa, o mesmo incidente volta.

## Triagem de severidade

| Nível | Exemplo | Ação |
|-------|---------|------|
| Baixa | senha fraca descoberta, não usada | trocar, seguir |
| Média | e-mail suspeito clicado, sem credencial digitada | antivírus, trocar por precaução |
| Alta | credencial vazada, acesso confirmado | contenção imediata, análise, notificação |
| Crítica | laudo em segredo de justiça vazado | ANPD, titulares, juízo, OAB, advogado |

## Comunicações obrigatórias

Ver `comunicacao_ANPD_e_titular.md`. Resumo:

- Incidente com risco a dado sensível: ANPD + titular em prazo razoável.
- Envolve segredo de justiça: comunicar juízo imediatamente.
- Envolve segredo médico: pode implicar autorreporte ao CRM.

## Anti-padrões

- Esperar para ver se "passa".
- Desligar e ligar o Mac esperando resolver.
- Não documentar achando que piora responsabilização (piora é não documentar).
- Comunicar titulares por WhatsApp sem formalização.

## Referência cruzada

- `comunicacao_ANPD_e_titular.md`
- `../backups_disaster_recovery/restauracao_e_teste.md`
- `../compliance_privacy/lgpd_para_medico_perito.md`
