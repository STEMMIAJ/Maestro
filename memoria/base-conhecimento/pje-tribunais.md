# PJe e Tribunais — Base de Conhecimento

## PJe (Processo Judicial Eletrônico)

### Acesso
- **URL TRT3 (MG):** https://pje.trt3.jus.br
- **URL TJMG:** https://pje.tjmg.jus.br
- **URL TRF1:** https://pje1g.trf1.jus.br
- **Certificado:** A1 digital (arquivo .pfx), instalado no Windows/Parallels
- **IMPORTANTE:** PJe SÓ funciona no Windows (Parallels). NUNCA tentar no Mac Chrome.

### Download Automatizado (funcionando desde 13/abr/2026)
- Chrome aberto com `--remote-debugging-port=9223`
- Perfil isolado: `~/.chrome-pje/`
- Selenium conecta via `debuggerAddress: localhost:9223`
- Script: download_pje.py (Selenium + Chrome debug)
- Pasta destino: ~/Desktop/processos-pje-windows/

### Estrutura do PJe
- **Painel do perito:** lista processos com intimação pendente
- **Documentos:** acessíveis por aba "Documentos" dentro do processo
- **Download:** botão de download individual por documento (PDF)
- **Movimentações:** aba "Movimentações" mostra timeline do processo
- **Prazos:** calculados automaticamente, visíveis no painel

## AJ TJMG (Automação Judicial — Tribunal de Justiça de MG)

- **URL:** https://www.tjmg.jus.br/portal-tjmg/
- **Consulta processual:** https://www4.tjmg.jus.br/juridico/sf/proc_complemento.jsp
- **Jurisprudência:** https://www5.tjmg.jus.br/jurisprudencia/
- Aceita busca por número CNJ, nome das partes, ou número antigo
- Intimações publicadas no DJe (Diário de Justiça eletrônico)

## AJG Federal (Assistência Judiciária Gratuita — Justiça Federal)

- Processos com AJG: honorários periciais pagos pelo Estado
- Valores tabelados (geralmente R$ 1.000 – R$ 2.000)
- Pagamento via RPV (Requisição de Pequeno Valor) — demora 2-6 meses
- Fundamentação: CPC Art. 95 §3º
- Perito pode recusar nomeação em caso de AJG se valor for irrisório (fundamentar)

## DataJud API

### Endpoint
```
https://datajud-wiki.cnj.jus.br/
```

### Uso
- Consulta de processos por número CNJ
- Dados de movimentação, classes, assuntos
- Base para análise de honorários (valores arbitrados em processos similares)
- API pública, sem autenticação para consultas básicas

### Campos Úteis
- `numeroProcesso`: CNJ completo
- `classe`: tipo de ação (ex: Ação Trabalhista)
- `assuntos`: lista de assuntos (CID, doença, acidente)
- `movimentos`: timeline com datas e descrições
- `orgaoJulgador`: vara e tribunal

## Números CNJ — Formato

```
NNNNNNN-DD.AAAA.J.TR.OOOO
```
- N: número sequencial (7 dígitos)
- D: dígitos verificadores (2)
- A: ano de distribuição (4)
- J: segmento de justiça (5=trabalho, 8=estadual, 4=federal)
- TR: tribunal (03=TRT3/MG, 13=TJMG)
- O: origem/vara (4 dígitos)

## Prazos Processuais

| Tipo | Prazo padrão | Observação |
|------|-------------|------------|
| Laudo pericial | 20 dias (CPC Art. 477) | Prorrogável a pedido |
| Manifestação sobre laudo | 15 dias (CPC Art. 477 §1º) | Partes e assistentes |
| Esclarecimentos | 15 dias | Após intimação |
| Honorários (petição) | Antes da entrega do laudo | CPC Art. 465 §4º |
| Recurso (agravo) | 15 dias | Contra decisão sobre honorários |
