#!/bin/bash

INPUT=experiments-config.csv
IFS=','
OLDIFS=$IFS

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

while read agent num_iperfs flow_size timesteps iter
do
	for (( i=0; i < $iter; i++ )); do
    echo "Iniciando experimento: $agent - $num_iperfs iperfs - $flow_size - $timesteps steps - iteração $i"

    ./start-iperfs-server.sh $agent $num_iperfs $flow_size $i

    ./delayed-start-iperfs-client.sh $agent $num_iperfs $flow_size $i

		sleep 10
  done

done < $INPUT
IFS=$OLDIFS
