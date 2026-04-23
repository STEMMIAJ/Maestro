---
titulo: Princípios básicos de design de software
bloco: 02_programming
tipo: conceito
nivel: iniciante
versao: 0.1
status: rascunho
ultima_atualizacao: 2026-04-23
nivel_evidencia: alto
tempo_leitura_min: 5
---

# Princípios básicos de design de software

Quatro siglas cobrem 80% das decisões. Lembrar: são **heurísticas**, não leis.

## DRY — Don't Repeat Yourself
"Não repita você mesmo." Cada pedaço de conhecimento deve existir em **um único lugar** no código.

Exemplo pericial — ruim:
```python
# scraper_datajud.py
url = f"https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search"

# scraper_comunica.py
url = f"https://api-publica.datajud.cnj.jus.br/api_publica_tjmg/_search"
```

Se o endpoint mudar, altera em 2 lugares — garantia de esquecer um.

Certo:
```python
# config.py
DATAJUD_URL = "https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search"
```

Por que importa: bug dobrado é comum quando regra tem duas fontes.

**Cuidado**: DRY fanático gera abstração prematura. Duas linhas parecidas nem sempre representam a mesma ideia — podem evoluir diferente. Regra prática (Rule of Three): deduplique na **terceira** repetição, não na segunda.

## KISS — Keep It Simple, Stupid
"Mantenha simples." Sempre a solução mais simples que resolve. Não codar para problema que talvez apareça.

Exemplo pericial — ruim:
```python
# sistema plugável com factory + registry + abstract class
# para... baixar 1 tipo de PDF do PJe
class PDFDownloaderFactory:
    def register(self, name, cls): ...
    def create(self, name): ...
```

Certo:
```python
def baixar_pdf_pje(url: str, destino: Path) -> Path:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    destino.write_bytes(r.content)
    return destino
```

Por que importa: código simples é entendido, testado e corrigido mais rápido. Código sofisticado sem necessidade gasta tempo toda vez que alguém (inclusive você amanhã) toca.

## YAGNI — You Aren't Gonna Need It
"Você não vai precisar disso." Não implemente feature que **pode** ser útil no futuro — só o que é necessário agora.

Exemplo pericial — ruim:
```python
def gerar_laudo(ficha, template="padrao", idioma="pt-br", assinar=True,
                enviar_email=False, webhook=None, formato="docx",
                compactar=False, marca_dagua=None):
    ...
```

8 parâmetros. 7 nunca foram usados. Cada um é código a manter, bug potencial.

Certo:
```python
def gerar_laudo(ficha, template="padrao"):
    ...
```

Adicionar parâmetro quando houver **caso real**.

Por que importa: código que você escreve "só por precaução" nunca é removido e vira peso morto. Flexibilidade especulativa mata manutenção.

## SRP — Single Responsibility Principle
"Uma responsabilidade por unidade." Cada função/classe deve ter **um motivo para mudar**.

Exemplo pericial — ruim:
```python
def processar_processo(cnj):
    # 1. baixa do PJe
    # 2. extrai texto
    # 3. acha CID-10
    # 4. preenche template laudo
    # 5. assina no PJeOffice
    # 6. envia email
    # 7. atualiza planilha
    ...
```

Uma função, 7 motivos para mudar. Qualquer alteração em qualquer etapa mexe em tudo. Testar é inviável (precisa mockar 6 coisas).

Certo — separado:
```python
def baixar_processo(cnj): ...
def extrair_texto(pdf_path): ...
def detectar_cids(texto): ...
def preencher_template(ficha, cids): ...
def assinar(docx_path): ...

def fluxo_completo(cnj):
    pdf = baixar_processo(cnj)
    texto = extrair_texto(pdf)
    cids = detectar_cids(texto)
    laudo = preencher_template(montar_ficha(cnj, cids))
    return assinar(laudo)
```

Cada função testável isolada. Mudou o PJeOffice? Mexe só em `assinar`.

Por que importa: SRP é a base para testes, reuso e manutenção. Sem ele, o resto desmorona.

## Regra prática pericial
Antes de aceitar código "pronto":
1. Tem duplicação desnecessária? (DRY)
2. Dá para simplificar sem perder função? (KISS)
3. Tem feature sem caso de uso real? (YAGNI)
4. Função/classe tem **uma** responsabilidade clara? (SRP)

Se três "não", refatorar. Se quatro "sim", aceitar.
