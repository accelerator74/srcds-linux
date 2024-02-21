#!/bin/sh
PIDS=`pidof srcds_linux`
for p in $PIDS; do
	renice -5 $p

	for i in $(pstree -p $p | grep -o '[0-9]\+'); do 
		renice -5 $i
	done
done
