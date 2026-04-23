---
titulo: "Gerenciamento de Segredos"
bloco: "05_security_and_governance"
tipo: "pratica"
nivel: "junior-pleno"
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: "consolidado"
tempo_leitura_min: 8
---

# Gerenciamento de Segredos

Segredo é qualquer valor que, exposto, quebra a segurança: senha, token API, chave SSH, chave privada ICP, credencial DataJud, chave Gemini. A regra universal: **nunca no código, nunca no repositório, nunca em claro no disco fora de cofre**.

## Camadas de armazenamento

### 1. `.env` local (mínimo viável)

Arquivo `.env` na raiz do projeto, listado em `.gitignore`. Carregado por `python-dotenv`, `dotenv-cli`, `direnv`.

```
# .env
DATAJUD_KEY=abc123
GEMINI_KEY=xyz789
```

Uso em Python:

```python
from dotenv import load_dotenv
load_dotenv()
key = os.environ["DATAJUD_KEY"]
```

Limite: qualquer processo no mesmo usuário lê. Backup do Desktop vaza. Aceitável só em dev local.

### 2. Keychain do macOS

Cofre nativo do sistema operacional, protegido por senha de login + Secure Enclave.

```bash
# gravar
security add-generic-password -s "datajud" -a "jesus" -w "abc123"

# ler
security find-generic-password -s "datajud" -a "jesus" -w
```

Vantagens: integrado, sem serviço extra, desbloqueado só com sessão ativa.
Limite: macOS-only. Sem versionamento, sem rotação automática, difícil compartilhar.

### 3. 1Password

Gestor comercial. Cofre criptografado em nuvem, chave mestra nunca sai do dispositivo. Recurso `op` CLI permite injetar segredos em tempo de execução:

```bash
op run --env-file=.env.template -- python script.py
```

Recomendado para Dr. Jesus: família/profissional, integra com Keychain, suporta passkey, compartilhamento controlado com secretária.

### 4. Bitwarden

Alternativa open-source com self-host opcional (Vaultwarden). Similar ao 1Password em funcionalidade, custo menor. CLI `bw`.

### 5. HashiCorp Vault

Cofre corporativo. Gerencia segredos dinâmicos (credencial de banco que expira em 1h), auditoria completa, políticas granulares. Overkill para profissional liberal. Relevante quando entrar em equipe de engenharia.

## Hierarquia recomendada

| Contexto | Ferramenta |
|----------|-----------|
| Senha pessoal/profissional | 1Password ou Bitwarden |
| Token de API em script local | Keychain + `security` |
| Segredo em projeto com colaborador | 1Password com cofre compartilhado |
| Infra corporativa, múltiplos serviços | Vault |
| CI/CD (GitHub Actions) | Secrets do GitHub, nunca `.env` commitado |

## Rotação

Segredo compromete validade com o tempo. Regras mínimas:

- Chave API: rotacionar a cada 90 dias ou ao menor sinal de vazamento.
- Senha mestra: 1 vez por ano se não houver suspeita.
- Chave ICP: conforme emissor (1 a 3 anos).
- Revogar imediatamente ao desligar colaborador.

## Detecção de vazamento

- `gitleaks` ou `trufflehog` em pre-commit hook.
- GitHub secret scanning (gratuito em repo público).
- Alerta do Have I Been Pwned com e-mail profissional monitorado.

## Anti-padrões reais

- `DATAJUD_KEY = "abc123"` hardcoded em `client.py` — já vazou várias vezes no ecossistema.
- Screenshot de terminal no grupo do WhatsApp mostrando token.
- `.env` commitado em repo "privado" que vira público por engano.
- Senha anotada em Post-it no monitor.

## Referência cruzada

- `ssh_keys_e_hardening.md`
- `mfa_e_passkeys.md`
- `../compliance_privacy/lgpd_para_medico_perito.md`

[TODO/RESEARCH: avaliar se macOS Sequoia mudou API do Keychain em 2026]
