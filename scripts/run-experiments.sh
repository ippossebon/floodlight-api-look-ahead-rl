#!/bin/bash

INPUT=experiments-config.csv
IFS=','
OLDIFS=$IFS

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

chmod +x ./add-initial-flow-entries.sh
chmod +x ./delete-flow-entries.sh

while read agent num_iperfs flow_size timesteps iter
do
	for (( i=0; i < $iter; i++ )); do
	# for (( i=55; i < 56; i++ )); do
    echo "Iniciando experimento: $agent - $num_iperfs iperfs - $flow_size - $timesteps steps - iteração $i"

	    ./add-initial-flow-entries.sh

	    ./start-iperfs-server.sh $agent $num_iperfs $flow_size $i

	    ./delayed-start-iperfs-client.sh $agent $num_iperfs $flow_size $i &

	    docker run -v $PWD/../:/app --network="bridge" lookahead python run-experiments.py -a $agent -n $num_iperfs -s $flow_size -t $timesteps -i $i

	    echo "Removendo todas as entradas estáticas..."

	    ./delete-flow-entries.sh

		  sleep 60
  done

done < $INPUT
IFS=$OLDIFS
