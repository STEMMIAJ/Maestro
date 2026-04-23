---
titulo: "Bit, byte e codificação"
bloco: "01_ti_foundations/concepts"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 5
---

# Bit, byte e codificação

## Bit

Bit (*binary digit*) é a menor unidade de informação: 0 ou 1. Fisicamente, é a presença ou ausência de carga elétrica num transistor. Um bit sozinho distingue duas possibilidades (sim/não, ligado/desligado).

## Byte

Byte = 8 bits. Representa 2⁸ = 256 combinações possíveis. É a unidade mínima endereçável na memória da maioria dos computadores. Um caractere ASCII cabe em 1 byte; um emoji Unicode pode ocupar 4 bytes.

Múltiplos (base 1000, SI):
- 1 KB = 1.000 bytes
- 1 MB = 1.000.000 bytes
- 1 GB = 1.000.000.000 bytes

Múltiplos binários (base 1024, IEC): KiB, MiB, GiB. Sistemas operacionais misturam as duas convenções — por isso um "HD de 1 TB" mostra 931 GiB no Finder.

## ASCII

American Standard Code for Information Interchange. Tabela que mapeia 128 caracteres (letras A–Z, a–z, dígitos 0–9, pontuação, controle) em números de 0 a 127. Cabe em 7 bits. Exemplo: letra `A` = 65 decimal = `01000001` binário.

Limitação: não tem acento. `João` em ASCII puro é impossível.

## UTF-8

Unicode Transformation Format, 8-bit. Codifica qualquer caractere do padrão Unicode (144 mil caracteres, incluindo chinês, emoji, árabe) usando 1 a 4 bytes por caractere. Caracteres ASCII continuam em 1 byte (retrocompatível). `ã` ocupa 2 bytes em UTF-8.

UTF-8 é o padrão de fato da web e de arquivos modernos. Se um laudo PDF aparece com `Jo�o` em vez de `João`, é erro de codificação (leu UTF-8 como se fosse ISO-8859-1 ou vice-versa).

## Base64

Codificação que transforma bytes binários em texto ASCII usando 64 símbolos (A–Z, a–z, 0–9, +, /). Aumenta o tamanho em ~33% — 3 bytes viram 4 caracteres. Não é criptografia; é transporte.

Uso: anexar PDF binário dentro de JSON, incorporar imagem dentro de HTML (`data:image/png;base64,...`), enviar certificado digital por email.

## Por que importa para o perito

- **PDF de laudo corrompido com caracteres estranhos** → quase sempre problema de codificação (UTF-8 vs Latin-1).
- **Assinatura digital em PAdES** usa Base64 para embutir o certificado no PDF.
- **Hash SHA-256** de laudo é calculado sobre os bytes — se você salvar o mesmo texto em UTF-8 e em Latin-1, o hash muda, e a cadeia de custódia quebra.
- **Exportação de dados do PJe** — arquivos `.txt` vindos do sistema judicial frequentemente vêm em ISO-8859-1; abrir direto em editor UTF-8 causa perda de acentos.

## Referências

- RFC 3629 (UTF-8), RFC 4648 (Base64).
- [TODO/RESEARCH: citar norma ABNT para hash em prova digital].
