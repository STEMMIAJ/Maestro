#!/bin/bash
# diagnostico-sistema.sh — Hook SessionStart
# Verifica Bluetooth e microfone ao iniciar sessão
# SIMPLIFICADO em 2026-03-12: removido system_profiler (pesado) e ping
# Evento: SessionStart | Não bloqueia (exit 0 sempre)

AVISOS=""

# 1. Bluetooth (rápido: lê plist direto)
BT=$(defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState 2>/dev/null || echo "0")
if [ "$BT" != "1" ]; then
    AVISOS="$AVISOS\n⚠️ Bluetooth desligado."
    blueutil --power 1 2>/dev/null || true
fi

# 2. Microfone (leve: checa volume de entrada via osascript)
MIC_VOL=$(osascript -e 'input volume of (get volume settings)' 2>/dev/null || echo "0")
if [ "$MIC_VOL" -eq 0 ] 2>/dev/null; then
    AVISOS="$AVISOS\n⚠️ Microfone não detectado. Verifique Bluetooth/Sony."
    osascript -e 'set volume input volume 75' 2>/dev/null
fi

# 3. Ditado (rápido: lê defaults)
DICT=$(defaults read com.apple.HIToolbox AppleDictationAutoEnable 2>/dev/null || echo "0")
if [ "$DICT" != "1" ]; then
    AVISOS="$AVISOS\n⚠️ Ditado desabilitado. Reabilitando..."
    defaults write com.apple.HIToolbox AppleDictationAutoEnable -int 1 2>/dev/null
fi

if [ -n "$AVISOS" ]; then
    echo -e "$AVISOS"
fi

exit 0
