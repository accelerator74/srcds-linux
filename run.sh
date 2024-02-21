#!/bin/sh
while true
do

./srcds_run -pidfile ../game.pid -game left4dead2 -console -nowatchdog -tickrate 60 -port 27015 +ip 0.0.0.0 +sv_pure 0 +map c1m1_hotel +sv_gametypes coop

echo Restarting in 5 Seconds...
sleep 5
done
