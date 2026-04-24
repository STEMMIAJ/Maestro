# Fontes e URLs

## Sistemas para acessar (perito)

| Sistema | URL | Autenticação |
|---------|-----|-------------|
| AJ TJMG | https://aj.tjmg.jus.br/aj/internet/pendenciasinternet.jsf | CPF + senha |
| AJG Justiça Federal | https://ajg.cjf.jus.br/ajg2/internet/pendenciasinternet.jsf | CPF + senha |
| PJe TJMG | https://pje.tjmg.jus.br | Certificado A3 VidaaS |
| DJEN consulta | https://comunica.pje.jus.br | Livre |
| Domicílio Judicial Eletrônico | https://domicilio-eletronico.pdpj.jus.br | gov.br |
| Portal CNJ login | https://login.cnj.jus.br | gov.br |

## APIs públicas

| API | URL | Auth |
|-----|-----|------|
| DataJud CNJ | https://api-publica.datajud.cnj.jus.br | Chave pública |
| Comunica PJe | https://comunicaapi.pje.jus.br/api/v1 | Corporativo CNJ |
| MNI Client | https://mni-client.prd.cnj.cloud/swagger-ui/index.html | X-MNI-CPF + X-MNI-SENHA |

## IMAP (Domicílio Eletrônico)

| Campo | Valor |
|-------|-------|
| Email | perito@drjesus.com.br |
| Remetente | `*@pdpj.jus.br` |
| Assunto padrão | "Resumo Diário — Domicílio Judicial Eletrônico" |
| Host IMAP | (preencher em `~/.stemmia/credenciais.env`) |

## Suporte TJMG

- Telefone: 0800-3535-600
- Portal Serviços TI TJMG
- COAPE (Coord. Apoio PJe 1ª Instância)

## Documentos legais

| Norma | Assunto |
|-------|---------|
| Resolução CNJ 234/2016 | Comunicações processuais eletrônicas |
| Resolução CNJ 455/2022 | Portal de Serviços + Domicílio Eletrônico |
| Resolução CNJ 569/2024 | Atualização Domicílio Eletrônico |
| Aviso CGJ/TJMG 37/2019 | Cadastro peritos no PJe |
| Aviso CGJ/TJMG 73/2021 | Auxiliares da justiça no PJe |

## Prazos

| Situação | Prazo |
|----------|-------|
| Aceite nomeação AJ/AJG | 5 dias úteis (~7 corridos) |
| Ciência Domicílio (PJ) | 3 dias úteis |
| Ciência Domicílio (intimação) | 10 dias corridos |
| Ciência tácita (Domicílio) | automática se não abrir |
