---
titulo: "CPU, RAM e disco"
bloco: "01_ti_foundations/hardware_networks_os"
tipo: "conceito"
nivel: "iniciante"
versao: 0.1
status: "rascunho"
ultima_atualizacao: 2026-04-23
nivel_evidencia: "A"
tempo_leitura_min: 6
---

# CPU, RAM e disco

## CPU (Central Processing Unit)

Unidade que executa instruções do software. Tudo que o computador faz passa por aqui.

- **Core (núcleo)** — unidade de execução independente dentro do chip. CPU de 8 cores executa 8 tarefas em paralelo real.
- **Thread** — fluxo de execução. Com *SMT/Hyperthreading*, 1 core executa 2 threads alternadamente, aproveitando ciclos ociosos. CPU "8 cores / 16 threads" = 8 núcleos físicos, 16 lógicos.
- **Clock (GHz)** — frequência de ciclos por segundo. 3,2 GHz = 3,2 bilhões de ciclos/s. Por si só, não mede desempenho; arquitetura pesa mais (um M3 a 3,5 GHz rende mais que um i7 antigo a 4,0 GHz).
- **Cache L1/L2/L3** — memória ultra-rápida dentro da CPU para evitar ir à RAM. Hierarquia em tamanho e velocidade: L1 (dezenas de KB, ~1 ns) < L2 < L3 (dezenas de MB, ~30 ns).

Arquiteturas comuns: **x86-64** (Intel, AMD), **ARM64** (Apple Silicon M1–M4, Snapdragon). Programa compilado para x86 não roda nativo em ARM sem tradução (Rosetta no macOS).

## RAM (Random Access Memory)

Memória volátil de trabalho. Guarda código e dados que a CPU está usando *agora*. Perde tudo quando desliga.

- Capacidade típica 2026: 16–64 GB em notebook, 128–512 GB em servidor.
- Velocidade: DDR4-3200, DDR5-5600, LPDDR5 (notebooks e M-series). Medida em MT/s.
- Latência: ~80 ns (100× mais lenta que L3, 100.000× mais rápida que SSD).
- Se faltar RAM, SO usa *swap* em disco (ver `swapfile` no Mac) — lento, prejudica responsividade.

Regra prática: Chrome com 50 abas + PJe + ferramentas de perícia consome fácil 16 GB. 32 GB é confortável.

## Disco (armazenamento não-volátil)

Guarda dados persistentes. Sobrevive ao desligamento.

- **HD (Hard Disk Drive)** — prato magnético girando. Barato, grande (4–20 TB), lento (~100 MB/s leitura sequencial, latência ~10 ms). Obsoleto para SO; serve para backup.
- **SSD SATA** — chips flash NAND, interface SATA. ~550 MB/s, latência ~0,1 ms. Padrão em máquinas 2015–2020.
- **SSD NVMe (M.2, PCIe)** — chips flash direto no barramento PCIe. 3.000–14.000 MB/s, latência ~20 µs. Padrão atual; Macs M-series têm NVMe soldado.
- **Durabilidade**: SSD tem limite de ciclos de escrita (TBW). Para uso pericial normal, dura 5–10 anos sem problema.

## GPU (Graphics Processing Unit)

Processador paralelo massivo (milhares de cores simples). Originalmente para gráficos; hoje usado para treino/inferência de IA, renderização de vídeo, mineração.

- **Integrada** — parte da CPU (M-series, Intel Iris). Suficiente para escritório.
- **Dedicada** — placa separada (NVIDIA RTX, AMD Radeon). Necessária para rodar modelos de IA localmente, edição de vídeo 4K+.

Para perito que usa Claude em nuvem: GPU local é irrelevante. Para rodar Whisper/OCR local em lote grande: GPU ajuda.

## Como se relacionam

Fluxo de execução típico:
1. SO carrega programa do **disco** para a **RAM**.
2. **CPU** lê instruções da RAM (via cache).
3. Dados em uso ficam na RAM; alterações são escritas de volta ao disco quando salvas.

Gargalo mais comum em perícia: disco (I/O) ao processar muitos PDFs grandes. Segundo: RAM. CPU raramente satura em trabalho de escritório.

## Por que importa para o perito

- Dimensionar máquina: 32 GB RAM + SSD NVMe 1 TB + CPU 8 cores é o mínimo confortável para rodar Claude CLI + PJe automatizado + N8N + Obsidian.
- Perícia em hardware apreendido exige entender SSD (TRIM destrói evidência) vs HD (recuperação por magnético ainda viável).
- Swap agressivo em máquina antiga mascara desempenho e explica travamentos em audiência.

## Referências

- [TODO/RESEARCH: benchmark NVMe M3 Max vs M4 Pro para cargas de OCR].
