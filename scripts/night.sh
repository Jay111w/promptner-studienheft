#!/usr/bin/env bash
# Nachtlauf: Experimente nacheinander, gedrosselt, Mac bleibt wach, Log unter logs/night-*.log.
# Bricht ein Lauf ab (Netz, Limit), wird er bis zu 5x neu gestartet - der Antwort-Cache macht
# Wiederholungen kostenlos, es werden nur noch fehlende Absaetze angefragt.
#
#   scripts/night.sh E4 E5 E7            # diese Experimente, Standard: 150 Saetze, Seeds 1,2
#   LIMIT=100 SEEDS=1 scripts/night.sh E3 # Umgebungsvariablen ueberschreiben Defaults
#   tail -f logs/night-*.log             # zuschauen
set -u
cd "$(dirname "$0")/.."
LIMIT="${LIMIT:-150}"
SEEDS="${SEEDS:-1,2}"
EXTRA="${EXTRA:-}"                      # z. B. --models a,b,c
LOG="logs/night-$(date +%Y%m%d-%H%M).log"
mkdir -p logs
echo "Start $(date) | Experimente: $* | limit=$LIMIT seeds=$SEEDS $EXTRA" | tee -a "$LOG"
FAILED=""
for exp in "$@"; do
  ok=0
  for attempt in 1 2 3 4 5; do
    echo "== $exp, Versuch $attempt, $(date)" | tee -a "$LOG"
    if caffeinate -i uv run promptner run --experiment "$exp" --limit "$LIMIT" --seeds "$SEEDS" $EXTRA >>"$LOG" 2>&1; then
      echo "== $exp fertig, $(date)" | tee -a "$LOG"; ok=1; break
    fi
    echo "== $exp abgebrochen (Versuch $attempt/5), $(date)" | tee -a "$LOG"
    [ "$attempt" -lt 5 ] && sleep 600
  done
  [ "$ok" -eq 1 ] || FAILED="$FAILED $exp"
done
if [ -n "$FAILED" ]; then
  echo "!! NICHT FERTIG:$FAILED - summary/plots uebersprungen. Log: $LOG" | tee -a "$LOG"
  exit 1
fi
uv run promptner summary >>"$LOG" 2>&1 && uv run promptner plots >>"$LOG" 2>&1
echo "Ende $(date) - alles fertig" | tee -a "$LOG"
