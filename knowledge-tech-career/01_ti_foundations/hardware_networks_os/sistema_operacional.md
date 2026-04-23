---
titulo: "Sistema operacional"
bloco: "01_ti_foundations/hardware_networks_os"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 7
---

# Sistema operacional

## O que faz um SO

Sistema operacional (SO) é o software que administra o hardware e oferece serviços a aplicações. Sem SO, cada aplicativo teria que falar direto com CPU, disco e rede — inviável.

Funções nucleares:
1. **Gerência de processos** — cria, agenda e encerra programas em execução.
2. **Gerência de memória** — aloca RAM, isola processos, usa swap.
3. **Gerência de arquivos** — sistema de arquivos (APFS, NTFS, ext4) organiza dados em disco.
4. **Gerência de dispositivos** — drivers para teclado, rede, impressora.
5. **Segurança e permissões** — controle de usuário, sandbox, criptografia (FileVault, BitLocker).
6. **Interface** — GUI (janelas) ou shell (terminal).

## Kernel

Núcleo do SO. Parte que roda em modo privilegiado (*kernel mode*), tem acesso total ao hardware. Aplicações rodam em *user mode*, isoladas; pedem serviços ao kernel via *syscall*.

Tipos:
- **Monolítico** — tudo no kernel (Linux).
- **Microkernel** — kernel mínimo, resto em user space (Minix, parte do macOS via XNU híbrido).
- **Híbrido** — mistura (Windows NT, XNU do macOS/Darwin).

## Processo

Instância de programa em execução. Tem PID (process ID), espaço de memória próprio, descritores de arquivo abertos.

Exemplo: abrir Chrome duas vezes cria dois processos distintos (PIDs diferentes), cada um com sua RAM isolada. Se um trava, o outro não é afetado (isolamento).

Comando `ps aux` no terminal lista processos. Activity Monitor (macOS) mostra graficamente.

## Thread

Fluxo de execução dentro de um processo. Vários threads compartilham memória do mesmo processo (mais leve que criar processo novo).

Exemplo: Chrome usa 1 processo por aba + threads para rede, render, UI dentro de cada aba.

Diferença-chave: processos isolados, threads compartilhados.

## Syscall (chamada de sistema)

Interface pela qual aplicação pede serviço ao kernel. Exemplos: `open()` abre arquivo, `read()` lê bytes, `write()` escreve, `fork()` cria processo, `socket()` cria conexão de rede.

Toda vez que um programa abre um arquivo, ele faz syscall. Ferramenta `dtruss` (macOS) ou `strace` (Linux) mostra syscalls em tempo real — útil para debugar travamento de script.

## macOS, Linux e Windows — comparação

| Aspecto | macOS | Linux | Windows |
|---|---|---|---|
| Kernel | XNU (híbrido Mach+BSD) | Linux (monolítico) | NT (híbrido) |
| Filesystem padrão | APFS | ext4 / btrfs / xfs | NTFS |
| Shell padrão | zsh | bash / zsh | PowerShell / cmd |
| Gerenciador pacotes | Homebrew (3rd-party) | apt, dnf, pacman | winget, choco |
| Instalador apps | .dmg / .pkg / App Store | repositório / .deb / .rpm / Flatpak | .exe / .msi / Store |
| Automação nativa | launchd (plist) | systemd (unit) / cron | Task Scheduler |
| Abertura | fechado (Apple) | aberto (GPL) | fechado (Microsoft) |
| Uso típico | desktop criativo, dev | servidor, dev, embarcado | desktop corporativo, jogos |

macOS é Unix certificado (deriva de BSD+Mach); compartilha muito com Linux em termos de shell e ferramentas CLI. Windows é mundo à parte, mas WSL2 roda Linux real dentro dele.

## Por que importa para o perito

- **PJe funciona mal em macOS Chrome** (assinador Shodō/CNJ instável) → Parallels com Windows é obrigatório. Entender que é escolha do PJe, não limitação do Mac.
- **Monitor de movimentações** usa launchd no Mac (`~/Library/LaunchAgents/com.jesus.*.plist`). Linux usaria systemd; Windows, Task Scheduler.
- **Perícia em máquina apreendida** requer saber o SO para escolher ferramenta forense correta (FTK, Autopsy, Cellebrite).
- **Permissões de arquivo** (`chmod 600 chave_privada`) evitam que outro usuário leia dados pericias.

## Referências

- Tanenbaum, A. — *Modern Operating Systems*, 5ª ed.
- [TODO/RESEARCH: docs oficiais Apple sobre XNU e launchd].
