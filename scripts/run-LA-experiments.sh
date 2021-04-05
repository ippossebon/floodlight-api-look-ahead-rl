#!/bin/bash

INPUT=experiments-LA-config.csv
IFS=','
OLDIFS=$IFS

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

chmod +x ./add-initial-flow-entries.sh
chmod +x ./delete-flow-entries.sh
chmod +x ./start-incremental-iperfs-server.sh
chmod +x ./delayed-start-incremental-iperfs-client.sh


while read agent timesteps interval proportion iter
do
	for (( i=0; i < $iter; i++ )); do
    echo "*** Iniciando experimento: $agent - $timesteps steps - intervalo $interval - propotion $proportion- iteração $i"

	    ./add-initial-flow-entries.sh

	    ./start-incremental-iperfs-server.sh $agent $interval $proportion $i

	    ./delayed-start-incremental-iperfs-client.sh $agent $interval $proportion $i &

	    docker run -v $PWD/../:/app --network="bridge" lookahead python run-experiments.py -a $agent -n 8 -s ALL_FLOWS -t $timesteps -v $interval -p $proportion -i $i

	    echo "*** Removendo todas as entradas estáticas..."

	    ./delete-flow-entries.sh

		  sleep 60
  done

done < $INPUT
IFS=$OLDIFS
