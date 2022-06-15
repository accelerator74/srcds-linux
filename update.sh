#!/bin/bash
screen -S SRCDS -X quit
./steamcmd.sh +force_install_dir ../srcds +login anonymous +app_update 222860 +quit