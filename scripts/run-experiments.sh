#!/bin/bash

INPUT=experiments-config.csv
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }

chmod +x ./add-initial-flow-entries.sh
chmod +x ./kill-controller.sh
chmod +x ./delete-flow-entries.sh
chmod +x ./start-iperfs.sh
chmod +x ./iperf-client.sh
chmod +x ./iperf-server.sh

while read agent num_iperfs flow_size timesteps iter
do
	for (( i=0; i < $iter; i++ )); do
    echo "Iniciando experimento: $agent - $num_iperfs iperfs - $flow_size - $timesteps steps - iteração $i"

    # Adiciona fluxos iniciais (python2)
    ./add-initial-flow-entries.sh

    ./start-iperfs-server.sh $agent $num_iperfs $flow_size $iter

    ./delayed-start-iperfs-client.sh $agent $num_iperfs $flow_size $iter

    # # Inicia agente
    # CONTAINER_NAME='lookahead'
    # # CID=$(docker ps -q -f status=running -f name=^/${CONTAINER_NAME}$)
    # # if [ ! "${CID}" ]; then
    #   # echo "Container doesn't exist"
    #   # cd ..
    #   # docker-compose up -d
    #   # cd scripts
    #   docker stop lookahead
    #   docker rm lookahead


    #   docker run -v $PWD/../:/app/ --network="bridge" --name="lookahead" -d lookahead python /app/run-experiments.py -a $agent -n $num_iperfs -s $flow_size -t $timesteps -i $i
    # # fi
    # unset CID

    # docker exec -it lookahead "python /app/floodlight-api-look-ahead-rl/run-experiments.py -a $agent -n $num_iperfs -s $flow_size -t $timesteps >> /tmp/agent.log"
    sleep 20
    #
    # # # Inicia iperfs
    # echo "Iniciando iperfs..."
    # ~/Documents/UFRGS/Mestrado/projeto/floodlight-api-look-ahead-rl/scripts/start-iperfs.sh $agent $num_iperfs $flow_size $i &

    # echo "Aguardando finalização do agente e iperfs..."
    # # Espera conclusão do agente e iperfs
    # WAIT_TIME=$(($timesteps*7))
    # sleep $WAIT_TIME

    echo "Removendo todas as entradas estáticas..."
    # Remove fluxos estaticos
    ./delete-flow-entries.sh

    sleep 5
  done

done < $INPUT
