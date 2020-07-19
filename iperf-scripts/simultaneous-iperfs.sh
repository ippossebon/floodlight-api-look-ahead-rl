iperf -c 10.0.0.2 -n 1G &
sleep 15;
iperf -c 10.0.0.2 -n 100G &
sleep 1;
iperf -c 10.0.0.2 -n 200G &
sleep 50;
iperf -c 10.0.0.2 -n 50G &
sleep 20
