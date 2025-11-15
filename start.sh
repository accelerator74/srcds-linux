#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
screen -AdmSL SRCDS -Logfile "$DIR/screenlog.0" "$DIR/run.sh"
