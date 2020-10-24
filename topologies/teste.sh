h2 iperf3 -s -p 5201 -1 > saida-server.txt
sleep 1
h1 iperf3 -c 10.0.0.2 -B 10.0.0.1 --cport 46110 -p 5201 -n 10M > saida-client.txt
sleep 1
echo "Rodou script"
