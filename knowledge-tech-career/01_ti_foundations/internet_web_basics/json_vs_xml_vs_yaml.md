---
titulo: "JSON vs XML vs YAML"
bloco: "01_ti_foundations/internet_web_basics"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 4
---

# JSON vs XML vs YAML

Três formatos de serialização de dados estruturados, usados para trafegar ou guardar informação legível por humano e máquina.

## O mesmo laudo em três formatos

Cenário: metadados de um laudo pericial.

### JSON

```json
{
  "laudo": {
    "numero": "001/2026",
    "processo": "0001234-56.2026.8.13.0024",
    "perito": "Dr. Jesus",
    "data": "2026-04-23",
    "partes": ["Fulano", "Sicrano"],
    "assinado": true
  }
}
```

### XML

```xml
<laudo>
  <numero>001/2026</numero>
  <processo>0001234-56.2026.8.13.0024</processo>
  <perito>Dr. Jesus</perito>
  <data>2026-04-23</data>
  <partes>
    <parte>Fulano</parte>
    <parte>Sicrano</parte>
  </partes>
  <assinado>true</assinado>
</laudo>
```

### YAML

```yaml
laudo:
  numero: 001/2026
  processo: 0001234-56.2026.8.13.0024
  perito: Dr. Jesus
  data: 2026-04-23
  partes:
    - Fulano
    - Sicrano
  assinado: true
```

## Comparação

| Aspecto | JSON | XML | YAML |
|---|---|---|---|
| Verbosidade | baixa | alta | mínima |
| Comentários | não | sim (`<!-- -->`) | sim (`# `) |
| Tipos nativos | string, num, bool, null, array, obj | tudo string; schema define | string, num, bool, null, date, list, map |
| Indentação importa | não | não | sim (espaços, nunca tab) |
| Schema / validação | JSON Schema | XSD, DTD | JSON Schema adaptado |
| Atributos vs filhos | não existe | sim (ambíguo) | não existe |
| Uso típico 2026 | APIs web, config | docs legais, SOAP, PAdES, XBRL | configs (Kubernetes, GitHub Actions) |

## Quando usar cada

- **JSON** — API REST, config simples de app, troca entre serviços. Padrão de fato da web moderna.
- **XML** — exigido por normas antigas e pelo mundo jurídico/fiscal. NFe, e-SUS, eSocial, assinatura PAdES em PDF, SOAP, PJe (interno). Robusto para documento longo com estrutura estrita.
- **YAML** — config humana que você vai editar à mão. CI/CD, Docker Compose, Ansible, Obsidian frontmatter. Perigo: indentação errada quebra silenciosamente.

## Armadilhas comuns

- **JSON não aceita vírgula sobrando** (`{"a":1,}` é inválido). XML e YAML aceitam.
- **YAML interpreta `no`, `yes`, `on`, `off` como booleano** — se `pais: no` (Noruega), vira `false`. Use aspas: `pais: "no"`.
- **XML com namespaces** (`xmlns:xs=...`) confunde iniciante; é necessário em documentos formais.

## Por que importa para o perito

- **NF-e e documentos fiscais** em processo judicial vêm em XML; perícia sobre autenticidade precisa validar assinatura XMLDSig.
- **Frontmatter YAML** usado em Obsidian e nestes artefatos permite filtrar laudos por campo (`status: rascunho`).
- **DataJud retorna JSON**; scripts do monitor de processos parseiam `hits.hits[].numeroProcesso`.
- **Importação/exportação entre ferramentas** (Claude → N8N → SQLite) costuma usar JSON como lingua franca.

## Referências

- RFC 8259 (JSON), W3C XML 1.0, YAML 1.2 spec.
