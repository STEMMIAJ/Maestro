---
titulo: Autenticação vs Autorização
bloco: 03_web_development
tipo: referencia
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: padrao-nist
tempo_leitura_min: 5
---

# Autenticação vs Autorização

Dois conceitos distintos, sempre confundidos.

- **Autenticação (AuthN)** — **Quem é você?** Provar identidade. Ex: login/senha, biometria, token.
- **Autorização (AuthZ)** — **Você pode fazer isso?** Decidir acesso a recurso/operação. Ex: "perito pode ver processo próprio, não de outro perito".

Autenticar vem sempre antes. Autorizar depende do papel/atributos do usuário autenticado.

## Modelos de autorização

### RBAC (Role-Based Access Control)

Usuário tem papéis; papéis têm permissões.

```
papel: perito
  ├─ ler:processo
  ├─ criar:laudo
  └─ editar:laudo

papel: admin
  ├─ ler:processo
  ├─ criar:laudo
  ├─ editar:laudo
  ├─ deletar:laudo
  └─ gerenciar:usuarios

usuario: dr_jesus → papéis: [perito, admin]
```

Simples, fácil auditar. Limitação: "perito só edita o PRÓPRIO laudo" não cabe em papel — precisa lógica extra.

### ABAC (Attribute-Based Access Control)

Decisão baseada em **atributos** do usuário, recurso, ação, contexto.

Regra: `permitir editar:laudo SE laudo.perito_id == usuario.id E processo.status == 'ativo' E hora_atual ENTRE 06:00 E 22:00`.

Flexível, granular. Implementação: engine de políticas (OPA/Rego, Cedar da AWS, Casbin).

### ReBAC (Relationship-Based)

Baseado em grafo de relações. Ex: Google Zanzibar, OpenFGA. "Usuário tem acesso SE é membro do grupo X que é dono do documento Y".

Ideal para apps tipo Google Docs/Notion. Overkill para dashboard pericial pequeno.

### ACL (Access Control List)

Lista de permissões direto no recurso. "Documento 123 pode ser lido por [alice, bob]". Funciona em poucos recursos; explode em milhões.

## Onde aplicar AuthZ

- **Rota/endpoint** — middleware verifica papel antes de chamar handler.
- **Nível de registro (row-level)** — filtro SQL pelo `perito_id`. Postgres RLS (Row-Level Security) aplica automático.
- **Nível de campo** — esconder CPF de usuários sem permissão. GraphQL resolvers fazem bem.
- **UI** — ocultar botão "Deletar" se usuário não pode. Nunca confiar só no frontend; backend sempre reconfere.

## Princípios

- **Menor privilégio** — padrão é negar; conceder só o necessário.
- **Defesa em profundidade** — verificar em múltiplas camadas (API gateway + serviço + DB).
- **Separação de deveres** — quem aprova ≠ quem executa.
- **Auditoria** — logar cada decisão de acesso (quem, o quê, quando, resultado).

## Exemplo prático FastAPI com RBAC

```python
from fastapi import Depends, HTTPException

def requer_papel(papel: str):
    def checker(user = Depends(usuario_atual)):
        if papel not in user.papeis:
            raise HTTPException(403, "Acesso negado")
        return user
    return checker

@app.delete("/laudos/{id}")
def deletar(id: int, user = Depends(requer_papel("admin"))):
    ...
```

ABAC em cima:

```python
def pode_editar_laudo(user, laudo):
    return "admin" in user.papeis or laudo.perito_id == user.id

@app.put("/laudos/{id}")
def editar(id: int, payload: LaudoIn, user = Depends(usuario_atual)):
    laudo = repo.get(id)
    if not pode_editar_laudo(user, laudo):
        raise HTTPException(403)
    ...
```

## Para o sistema pericial

Papéis provisórios: `admin` (Dr. Jesus), `assistente` (secretário/a), `auditor` (só-leitura). Regras ABAC complementares: cada perito/assistente só vê processos dos quais participa. Postgres RLS implementa direto no DB — extra resistente a bug no app.

## Erros comuns

- "Usuário autenticado = autorizado". Cada request precisa checar.
- Role-check só no frontend (JWT tem role, UI esconde botão; backend não checa). Atacante bypassa via curl.
- JWT sem expiração curta — vazou, vale 1 ano. Usar refresh tokens.
- Papel "super-admin" criado e esquecido, acumula acesso global.
