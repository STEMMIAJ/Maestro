---
titulo: "Hardware vs software vs firmware"
bloco: "01_ti_foundations/concepts"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 4
---

# Hardware vs software vs firmware

## Definições

- **Hardware** — componente físico, tangível. CPU, RAM, SSD, placa de rede, cabo, monitor. Se você pode derrubar no chão, é hardware.
- **Software** — instruções (código) que rodam sobre o hardware. Intangível. Navegador, sistema operacional, script Python, laudo em PDF (dado também é software em sentido amplo).
- **Firmware** — software gravado em memória não volátil *dentro* de um dispositivo de hardware, responsável por fazê-lo funcionar no nível mais baixo. Fica entre hardware e software de sistema. Exemplo: BIOS/UEFI da placa-mãe, firmware do SSD, firmware do roteador.

## Camadas (do mais baixo para o mais alto)

```
[ aplicação: Chrome, Word, laudo.pdf ]        ← software aplicativo
[ sistema operacional: macOS, Windows ]       ← software de sistema
[ firmware: UEFI, controller do SSD ]         ← firmware
[ hardware: CPU, RAM, disco, placa-mãe ]      ← hardware
```

Cada camada fala apenas com a imediatamente abaixo, via interface definida. Aplicação não mexe direto no hardware; usa o SO. SO não mexe direto nos chips; usa firmware e drivers.

## Diferença-chave firmware vs software

- Software comum é instalado e removido sem esforço, fica no disco.
- Firmware vem gravado de fábrica em chip do próprio dispositivo (EEPROM, flash interna). Atualizar firmware é operação delicada — falha pode "brickar" o dispositivo (deixar inoperante).

## Exemplos do dia a dia

- Impressora: a mecânica é hardware; o firmware interpreta comandos PostScript; o driver no Mac é software.
- Pen drive: chip de memória é hardware; o controller USB roda firmware; o arquivo `laudo.pdf` copiado para ele é dado.
- iPhone: chip A17 é hardware; iBoot+SEPOS é firmware; iOS é software de sistema; WhatsApp é aplicativo.

## Por que importa para o perito

- Perícia em dispositivo apreendido exige distinguir o que foi alterado: usuário altera aplicação facilmente, software do sistema com privilégio, firmware apenas com ferramenta específica. Alteração de firmware sugere adulteração deliberada.
- Hash de firmware comprometido em roteador é prova de intrusão.
- Atualização de firmware altera comportamento do hardware sem trocar o dispositivo — relevante em casos de defeito de produto.

## Referências

- [TODO/RESEARCH: citar IEEE Std 610.12-1990 para definição formal de firmware].
