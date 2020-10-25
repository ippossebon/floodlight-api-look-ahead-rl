#!/bin/bash

INPUT=experiments_config.cvs
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

chmod +x ./init-controller.sh
chmod +x ./add-initial-flow-entries.sh
chmod +x ./kill-controller.sh
chmod +x ./delete-flow-entries.sh
chmod +x ./run-mininet.sh
chmod +x ./start-iperfs.sh
chmod +x ./iperf-client.sh
chmod +x ./iperf-server.sh

while read agent num_iperfs flow_size timesteps iter
do
	for i in $(seq 1 $iter)
    # Inicia Floodlight
    ./init-controller.sh

    # Adiciona fluxos iniciais (python2)
    ./add-initial-flow-entries.sh

    # Inicia arquivo com topologia
    ./run-mininet.sh

    # Inicia agente
    cd ../../docker-look-ahead-rl/
    docker compose up -d
    docker exec -it lookahead python ~/floodlight-api-look-ahead-rl/run-experiments.py -a $agent -n $num_iperfs -s $flow_size -t $timesteps

    # Inicia iperfs
    start-iperfs.sh $agent $num_iperfs $flow_size

    # Espera conclusão do agente e iperfs
    WAIT_TIME = $(($timesteps*7))
    sleep $WAIT_TIME

    # Remove fluxos estaticos
    ./delete-flow-entries.sh

    # Mata floodlight
    ./kill-controller.sh

    sleep 5

done < $INPUT
