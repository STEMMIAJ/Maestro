---
titulo: "Time Machine no macOS"
bloco: "05_security_and_governance"
tipo: "pratica"
nivel: "junior"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Time Machine no macOS

Time Machine é o sistema de backup nativo da Apple. Snapshots horários (últimas 24h), diários (último mês), semanais (além disso, até encher o disco). Ponto forte: restauração granular por pasta e por timestamp. Ponto fraco: formato proprietário, exige disco formatado APFS.

## Configuração

1. Conectar HD externo USB (mínimo 2x o tamanho do disco de origem, recomendado 3x).
2. System Settings → General → Time Machine → Add Backup Disk.
3. **Marcar "Encrypt Backups"** e definir senha — salva no 1Password/Keychain.
4. Deixar "Back Up Automatically" ativo.

O primeiro backup demora horas (copia tudo). Depois, incremental, tipicamente 1–5 minutos.

## Exclusões

Nem tudo precisa entrar no backup. Excluir para economizar espaço e reduzir tempo:

- `~/Library/Caches/`
- Pastas de vídeo grandes que já estão em nuvem.
- `node_modules/`, `.venv/`, `__pycache__/`.
- Máquinas virtuais Parallels (arquivos enormes; fazer backup separado).
- Downloads se não tiverem trabalho em andamento.

Configurar em: System Settings → Time Machine → Options → lista de exclusão.

**Não excluir:**

- `~/Desktop/STEMMIA Dexter/` (hub pericial).
- `~/.claude/` (config, skills, memória).
- `~/.ssh/` (chaves).
- `~/Library/Application Support/` (dados de apps).
- `~/.pjeoffice-pro/` (assinador).

## Redundância de destino

Desde macOS Big Sur, Time Machine suporta múltiplos destinos. Alternância automática a cada backup.

- Destino 1: HD externo na mesa (rápido).
- Destino 2: NAS via SMB ou disco de rede (redundância).
- Destino 3: HD rotativo em local offsite (casa da família).

## Validação periódica

Comando para ver últimos backups e integridade:

```bash
tmutil latestbackup
tmutil listbackups
tmutil status
tmutil verifychecksums /Volumes/Backup/Backups.backupdb
```

Alerta vermelho: `tmutil status` sem avanço há dias, ou `verifychecksums` com erro.

## Restauração

- Pasta ou arquivo: abrir Time Machine na barra de menus → navegar timestamps → Restore.
- Sistema inteiro: boot em Recovery (Cmd+R) → Restore from Time Machine Backup.
- Item apagado: Time Machine abre no contexto da pasta atual; voltar até timestamp antes da exclusão.

## Advertências críticas

- **Time Machine não substitui o 1 offsite.** Se o HD estiver ao lado do Mac, incêndio destrói tudo junto.
- **Não é imune a ransomware.** Snapshots locais (APFS) podem ser criptografados por malware rodando como usuário. Mitigação: ter cópia offline adicional.
- **HD externo não é eterno.** SSD externo perde dados após 6-12 meses sem energia. HD magnético falha mecanicamente. Rotacionar a cada 3 anos.
- **Criptografia com senha perdida = backup perdido.** Senha no gestor + cópia impressa em cofre.
- **FileVault no Mac + Time Machine cifrado:** dois níveis, ambos necessários.

## Integração com 3-2-1

Time Machine cobre: 1 backup, 1 mídia. Falta nuvem e offline. Ver `estrategia_3_2_1.md`.

## Incidente real documentado

Relato do próprio Dr. Jesus: Time Machine OFF causou perda de dias de trabalho (19/abr/2026 — ver `project_recuperacao_19abr2026.md` na memória). Lição: verificar `tmutil status` no início da sessão.

## Referência cruzada

- `estrategia_3_2_1.md`
- `restauracao_e_teste.md`
