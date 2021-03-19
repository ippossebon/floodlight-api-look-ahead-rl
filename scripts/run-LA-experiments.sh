#!/bin/bash

INPUT=experiments-LA-config.csv
IFS=','
OLDIFS=$IFS

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

chmod +x ./add-initial-flow-entries.sh
chmod +x ./delete-flow-entries.sh
chmod +x ./start-incremental-iperfs-server.sh
chmod +x ./delayed-start-incremental-iperfs-client.sh


while read agent iter
do
	# for (( i=0; i < $iter; i++ )); do
	for (( i=75; i < 80; i++ )); do
    echo "Iniciando experimento: $agent - iteração $i"

	    ./add-initial-flow-entries.sh

	    ./start-incremental-iperfs-server.sh $agent $i

	    ./delayed-start-incremental-iperfs-client.sh $agent $i &

	    docker run -v $PWD/../:/app --network="bridge" lookahead python run-experiments.py -a $agent -n 8 -s ALL_FLOWS -t 5000 -i $i

	    echo "Removendo todas as entradas estáticas..."

	    ./delete-flow-entries.sh

		  sleep 60
  done

done < $INPUT
IFS=$OLDIFS
