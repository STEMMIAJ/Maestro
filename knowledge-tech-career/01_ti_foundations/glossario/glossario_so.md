---
titulo: "Glossário de sistema operacional"
bloco: "01_ti_foundations/glossario"
tipo: "glossario"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 6
---

# Glossário de sistema operacional

Ordem alfabética.

- **APFS** — sistema de arquivos padrão do macOS desde 2017, com snapshots e criptografia nativa.
- **Boot** — processo de inicialização do computador até o SO estar pronto.
- **Cgroups** — mecanismo do Linux para limitar e contabilizar recursos por grupo de processos.
- **Cron** — daemon Unix que agenda execução periódica de comandos.
- **Daemon** — processo que roda em segundo plano, geralmente iniciado no boot.
- **Driver** — módulo que permite ao kernel operar um dispositivo específico.
- **ext4** — sistema de arquivos tradicional do Linux.
- **File descriptor** — inteiro que identifica arquivo aberto dentro de um processo.
- **Filesystem** — estrutura lógica que organiza arquivos em um volume.
- **Fork** — syscall que duplica o processo atual criando um processo filho.
- **GUI** — interface gráfica baseada em janelas e ponteiro.
- **Hyperthreading / SMT** — técnica que permite um core executar dois threads em paralelo.
- **Init system** — primeiro processo do SO; lança demais serviços. Exemplos: systemd, launchd.
- **Interrupt** — sinal de hardware ou software que pede atenção imediata ao kernel.
- **Journaling** — técnica em sistemas de arquivos que registra operações antes de aplicar, permitindo recuperação.
- **Kernel** — núcleo privilegiado do SO.
- **launchd** — init system e escalonador do macOS, configurado por arquivos `.plist`.
- **Linux** — kernel monolítico livre; base de distribuições (Ubuntu, Debian, Fedora).
- **macOS** — SO da Apple, baseado em XNU (híbrido Mach+BSD).
- **Mount** — ato de tornar um sistema de arquivos acessível em um ponto do diretório.
- **NTFS** — sistema de arquivos padrão do Windows.
- **PID** — identificador numérico único de um processo em execução.
- **Pipe** — mecanismo que conecta a saída de um processo à entrada de outro.
- **plist** — *property list*; formato XML/binário de configuração no macOS.
- **Processo** — instância em execução de um programa, com memória própria.
- **Shell** — programa que interpreta comandos do usuário (bash, zsh, fish).
- **Signal** — mensagem assíncrona enviada a processo (ex.: SIGTERM, SIGKILL).
- **sudo** — comando que executa outro comando com privilégios elevados.
- **Swap** — área em disco usada como extensão da RAM quando falta memória.
- **Syscall** — chamada de sistema; interface pela qual processo pede serviço ao kernel.
- **systemd** — init system e gerenciador de serviços dominante no Linux moderno.
- **Thread** — fluxo de execução dentro de um processo; threads compartilham memória.
- **User mode / kernel mode** — modos de privilégio da CPU; aplicações rodam em user, kernel roda em kernel.
- **Windows** — família de SOs da Microsoft, baseada no kernel NT.
- **WSL** — *Windows Subsystem for Linux*; roda Linux real dentro do Windows.
- **XNU** — kernel do macOS; híbrido Mach microkernel + BSD monolítico.
