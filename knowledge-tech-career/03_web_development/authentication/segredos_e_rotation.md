---
titulo: Gestão de Segredos e Rotação
bloco: 03_web_development
tipo: referencia
nivel: intermediario
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-nist
tempo_leitura_min: 5
---

# Gestão de Segredos e Rotação

Segredo = credencial que dá acesso (API key, senha DB, chave JWT, certificado, token OAuth). Vazou = comprometido. Gestão séria pede: armazenar fora do código, rotacionar regular, auditar uso.

## Onde NÃO guardar

- Hardcoded no código.
- Commitado em git (incluindo histórico; `git log` lê tudo).
- `.env` versionado.
- Slack, email, ticket.
- Print/foto (OCR extrai).

## Onde guardar

### Arquivo .env local (dev)

`.env` **fora do git** (`.gitignore`). Exemplo:

```
DATAJUD_API_KEY=cDZHYzl5QVhITVgl...
DB_URL=postgresql://user:pass@localhost/pericia
JWT_SECRET=...
```

Carregar via `python-dotenv`, `dotenv` (Node), direnv. Commitar `.env.example` sem valores reais.

### Secret manager (produção)

- **AWS Secrets Manager** / **SSM Parameter Store** — integra IAM, rotação automática.
- **GCP Secret Manager** — idem no Google.
- **Azure Key Vault** — idem na Microsoft.
- **HashiCorp Vault** — multi-cloud, self-hosted, dynamic secrets (DB creds efêmeras).
- **Doppler**, **Infisical** — SaaS agnósticos, DX moderna.
- **1Password Secrets Automation / CLI** — se time já usa 1Password.

Acesso por aplicação via IAM role (sem secret para pegar secret — usa identidade da máquina).

### CI/CD

- GitHub Actions Secrets, GitLab CI Variables — criptografados, expostos como env no job.
- Nunca logar (`echo $TOKEN` vira log público). GitHub mascara automaticamente; não contar com isso.

## Rotação

**Rotação** = trocar segredo periodicamente, mesmo sem vazamento. Limita janela de exposição se alguém tiver cópia antiga.

Frequência sugerida:
- **API keys externas** — 90 dias.
- **Senhas DB** — 30–90 dias (ou dinâmicas via Vault, TTL de minutos).
- **Chaves JWT (HMAC)** — 90 dias, com período de sobreposição (aceitar 2 chaves durante rotação).
- **Certificados TLS** — automático via Let's Encrypt (90 dias).
- **Chaves de assinatura (RSA/ECDSA)** — 1–2 anos, com plano de migração.

Pós-vazamento: **rotação imediata** + auditoria de uso + notificar stakeholders.

## MFA (Multi-Factor Authentication)

Adicionar fator além da senha:
- **TOTP** — Google Authenticator, 1Password, Authy. Código a cada 30s.
- **SMS** — **fraco** (SIM swap). Evitar exceto como fallback.
- **Push** — Duo, Okta Verify.
- **WebAuthn/Passkeys** — chave privada no dispositivo, biometria ou PIN local. Resistente a phishing.

MFA é essencial para: email, git providers, cloud consoles, secret managers, admin do sistema pericial.

## Passkeys (WebAuthn)

Credencial criptográfica por site, armazenada no dispositivo (Secure Enclave, TPM). Sem senha, sem TOTP. Impossível phishing (chave ligada ao domínio).

- Registro: dispositivo gera par de chaves, envia pública ao servidor.
- Login: servidor desafia, dispositivo assina com privada (após biometria/PIN).

Adoção: Google, Apple, Microsoft, GitHub, 1Password. Em app próprio (Python): `webauthn` lib, `@simplewebauthn` (Node). Curva média; ganho enorme.

## Detectar vazamento

- **GitHub Secret Scanning** — detecta chaves de ~100 provedores em commits.
- **TruffleHog**, **gitleaks** — scan local/CI de repos.
- **Have I Been Pwned** — email/senha em breaches públicos.
- Pre-commit hook rodando gitleaks evita commit acidental.

## Princípios

- **Menor privilégio** — token só pode o necessário (scopes).
- **TTL curto** — credenciais efêmeras > permanentes.
- **Auditoria** — logar uso de cada secret.
- **Separação por ambiente** — dev ≠ staging ≠ prod. Comprometer dev não pega prod.
- **Defesa em profundidade** — mesmo se secret vazar, IP allowlist/VPN reduz dano.

## Para o sistema pericial

Estado atual: chaves do DataJud, N8N, Telegram, FTP provavelmente em arquivos diversos. Recomendação:

1. Consolidar em `.env` único fora do git, na raiz do projeto.
2. `~/.claude/...` secrets separados dos do código da aplicação.
3. MFA no GitHub, Google, Apple ID, painel do provedor de VPS.
4. Passkeys onde disponível (GitHub, Google).
5. Rotação trimestral da chave DataJud (guia mestre já recomenda).
6. Para produção futura: Doppler ou 1Password CLI integrado ao deploy.
