# ipv64-blocklist

Parser for iptables blocklist

Depencys iptable-persistent & jq

* replace API Key 
* cron for daily run

  Precheck `iptables-legacy-save | grep -F "icmp-port-unreachable"` if emtpy response (no blocked ip)
