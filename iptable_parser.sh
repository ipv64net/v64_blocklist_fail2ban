#!/bin/bash

API="YOUR-API-KEY"

IFS=$(echo -en "\n\b")

iptcmd=$(which iptables-legacy-save)
if [ -z "$iptcmd" ]; then iptcmd=$(which iptables-save); fi
if [ -z "$iptcmd" ]; then echo "Need iptables-persistent"; exit 1; fi

servicedetect()
{
	if [[ "$1" =~ .*ssh.* ]]; then echo "ssh"; return; fi
	if [[ "$1" =~ .*(imap|smtp|mail|postfix).* ]]; then echo "mail"; return; fi
	if [[ "$1" =~ .*(www|apache|nginx|npm).* ]]; then echo "www"; return; fi
        return "$1"

}


i=0
iplist=''
for entry in $($iptcmd | grep -F "icmp-port-unreachable")
do
	i=$(($i + 1))
	Service=$(echo "$entry" | cut -d" " -f2)
	IP=$(echo "$entry" | cut -d" " -f4 | cut -d"/" -f1) 
	#echo "Service=$(servicedetect "$Service") IP=$IP"
	if [ $i -eq 1 ]; then
		ip_list="{\"ip\":\"$IP\",\"category\":\"1\",\"info\":\"$(servicedetect "$Service")\"}"
	else
		ip_list="$ip_list,{\"ip\":\"$IP\",\"category\":\"1\",\"info\":\"$(servicedetect "$Service")\"}"
	fi
	#if [ $i -gt 10 ]; then break; fi
done

if [ $i -gt 0 ]; then
	datajson=$(echo "{\"ip_list\":[$ip_list]}\"}" | jq -c . 2>/dev/null)
	curljson=$(jq -n -c --arg data "$datajson" '{"report_ip_list": $data}')
	#curl https://ipv64.net/api.php -H "Authorization: Bearer ${API}" -H 'Content-Type: application/json' -d "$curljson" --trace-ascii /dev/stdout
	curl -s -X POST https://ipv64.net/api.php -H "Authorization: Bearer ${API}" -F "blocker_id=hXTr4CGu3eNHPB8FsqgQAjcI2kl9oJY7" -F "report_ip_list=\"$(echo "$datajson" | sed "s/\"/\\\\\"/g")\""
fi
