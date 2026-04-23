---
titulo: "Restauração e Teste de Backup"
bloco: "05_security_and_governance"
tipo: "runbook"
nivel: "pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 6
---

# Restauração e Teste de Backup

Backup não testado é presunção, não garantia. A única prova de que o backup funciona é restaurar com sucesso em ambiente separado.

## Princípio operacional

Se hoje o Mac parar de dar boot, quantas horas até voltar ao trabalho com integridade?

Esse número é o RTO real. Se nunca foi medido, não existe.

## Cadência de teste

| Item | Frequência de teste |
|------|--------------------|
| Arquivo isolado | mensal (pegar 1 laudo aleatório e restaurar em pasta temporária) |
| Pasta completa | trimestral (restaurar `~/Desktop/STEMMIA Dexter/` em disco externo) |
| Sistema inteiro | anual (restore completo em Mac secundário ou VM) |
| Base SQLite | mensal (abrir cópia restaurada e rodar queries de integridade) |
| Chave ICP / Keychain | trimestral (importar em Keychain secundário) |

## Runbook mínimo — restauração pontual

1. Identificar data do arquivo saudável (antes da corrupção/exclusão).
2. Montar destino: `mkdir -p /tmp/restore_$(date +%F)`.
3. Time Machine: abrir no Finder, navegar timestamp, copiar para `/tmp/restore_*`.
4. Validar integridade: `shasum -a 256 arquivo` e comparar com hash original, se houver.
5. Mover para destino final só após validação.
6. Documentar no diário: data, origem, destino, resultado.

## Runbook — restauração completa de sistema

Cenário: Mac roubado ou disco morto.

1. Adquirir/acessar Mac secundário ou Mac novo.
2. Assistente de Migração → Restore from Time Machine Backup.
3. Conectar HD de backup cifrado.
4. Inserir senha do backup (guardada no 1Password do celular ou cofre físico).
5. Selecionar backup mais recente validado.
6. Aguardar (6-24h para TB).
7. Após boot: validar CLAUDE.md, chaves SSH, Keychain, certificado ICP.
8. Rodar `tmutil status` para reativar Time Machine imediatamente no novo setup.

## Validação de integridade

### Hashing

Scripts de perícia podem gerar manifest:

```bash
find ~/Desktop/STEMMIA\ Dexter/laudos-assinados \
  -type f -exec shasum -a 256 {} \; > manifest-$(date +%F).txt
```

Comparar manifest pré e pós restore:

```bash
diff manifest-backup.txt manifest-restore.txt
```

Diferença = corrupção ou alteração.

### SQLite

```bash
sqlite3 dexter.db "PRAGMA integrity_check;"
```

Deve retornar `ok`.

### Arquivos críticos

Abrir 3 laudos aleatórios no PDF Reader, verificar assinatura digital válida.

## Retenção após teste

Backup restaurado em `/tmp/` não serve como cópia de segurança — é efêmero. Após validar, apagar com:

```bash
rm -rf /tmp/restore_*
```

(Único contexto onde `rm -rf /tmp/` é seguro; ainda assim revisar antes.)

## Documentação obrigatória

Cada teste gera entrada em `~/Desktop/STEMMIA Dexter/00-CONTROLE/backup-testes.md`:

```
## 2026-04-23
- Restaurado: laudo-processo-12345.pdf
- Origem: Time Machine HD-EXT-1, 2026-04-22 08:00
- Validação hash: ok
- Abriu no Preview: ok
- Assinatura ICP: válida
- Tempo: 3 min
```

## Sinais de alerta

- Backup rodando há dias sem concluir.
- Tamanho do backup estagnado (nada está sendo copiado).
- Teste de restauração falhou mesmo em 1 arquivo.
- `verifychecksums` reporta erro.

Qualquer um desses = parar trabalho pericial e reconstruir cadeia de backup antes de seguir.

## Referência cruzada

- `estrategia_3_2_1.md`
- `time_machine_macos.md`
- `../incident_response/playbook_incidente_minimo.md`
