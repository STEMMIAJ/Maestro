#!/bin/bash
# Executa em sequencia: T3 (4 comarcas) + T1 (upgrader) — todas com foco medico.
# Espera o perfil _perfil_tjmg/ liberar antes de comecar.
set -u
cd "/Users/jesus/Desktop/STEMMIA Dexter"

PERFIL="src/coleta-honorarios/_perfil_tjmg"
LOCK="$PERFIL/SingletonLock"

aguardar_lock_livre() {
    local etapa="$1"
    while [ -e "$LOCK" ]; do
        echo "[$etapa] aguardando lock liberar ($LOCK existe)... 15s"
        sleep 15
    done
    echo "[$etapa] lock livre, seguindo"
}

log_etapa() {
    echo ""
    echo "=========================================="
    echo "  $1"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
}

# T3a — Muriae (Zona Mata Sul)
log_etapa "T3a MURIAE"
aguardar_lock_livre "T3a"
python3 src/coleta-honorarios/coletor_tjmg_v2.py --busca "honorarios periciais medico Muriae" --max 20

# T3b — Uberlandia (Triangulo)
log_etapa "T3b UBERLANDIA"
aguardar_lock_livre "T3b"
python3 src/coleta-honorarios/coletor_tjmg_v2.py --busca "honorarios periciais medico Uberlandia" --max 20

# T3c — BH
log_etapa "T3c BELO HORIZONTE"
aguardar_lock_livre "T3c"
python3 src/coleta-honorarios/coletor_tjmg_v2.py --busca "honorarios pericia medica Belo Horizonte" --max 20

# T3d — Montes Claros
log_etapa "T3d MONTES CLAROS"
aguardar_lock_livre "T3d"
python3 src/coleta-honorarios/coletor_tjmg_v2.py --busca "honorarios periciais medico Montes Claros" --max 20

# T1 — upgrader das PARCIAIS medicas
log_etapa "T1 UPGRADER (GV-e-regiao, 7 fichas medicas)"
aguardar_lock_livre "T1"
python3 src/coleta-honorarios/upgrade_parciais_inteiroteor.py --regiao GV-e-regiao

log_etapa "FIM DE TUDO"
echo "Aperte ENTER para fechar"
read
