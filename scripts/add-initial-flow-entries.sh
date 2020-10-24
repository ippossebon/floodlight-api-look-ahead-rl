while IFS=, read -r rule_name, switch_id, tcp_src, tcp_dst, out_port
do
  curl --location --request POST 'http://192.168.68.250:8080/wm/staticflowpusher/json' \
    --header 'Content-Type: application/json' \
    --data-raw '{
      "name": "{{rule_name}}",
      "switch": "{{switch_id}}",
      "active": "true",
      "eth_type": "0x0800",
      "ipv4_src": "10.0.0.1",
      "ipv4_dst": "10.0.0.2",
      "ip_proto": "0x06",
      "tcp_src": "{{tcp_src}}",
      "tcp_dst": "{{tcp_dst}}",
      "actions": "output={{out_port}}"
    }'
done < $initial_flows_entries.csv
