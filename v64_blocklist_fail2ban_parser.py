import re,json,requests
import subprocess

# Get it From IPv64.net Website
v64_api_token="dein-api-key"
# Blocker Node ID
v64_blocker_node_id="deine-blocker-id"
# ipv64.net Api Endpoint
v64_url = "https://ipv64.net/api.php"

# Führe den Befehl 'iptables -L -n' aus und lies die Ausgabe ein
try:
    iptables_output = subprocess.check_output(["iptables", "-L", "-n"], universal_newlines=True)
except subprocess.CalledProcessError as e:
    print("Fehler beim Ausführen des Befehls 'iptables -L -n':", e)
    iptables_output = ""

# Muster für Ketten, die mit "f2b" beginnen
chain_pattern = r'^Chain (f2b[^\s]*) \(.*$'

# Suche nach Zeilen in der Ausgabe, die zu "f2b" Ketten gehören
chain_lines = re.findall(chain_pattern, iptables_output, re.MULTILINE)

# Erstelle eine leere Menge, um eindeutige IPv4-Adressen zu speichern
ipv4_addresses = set()

# Durchsuche die Ausgabe nach Regeln in den "f2b" Ketten
for chain_name in chain_lines:
    # Suche nach Zeilen, die zu dieser Kette gehören
    chain_rule_pattern = re.compile(r'(?<=Chain {0} ).*?(?=\nChain|\Z)'.format(re.escape(chain_name)), re.DOTALL)
    chain_rules = re.search(chain_rule_pattern, iptables_output)
    
    if chain_rules:
        # Extrahiere IPv4-Adressen aus den Regeln in dieser Kette
        ipv4_addresses.update(re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/?\d{0,2})', chain_rules.group(0)))

# Entferne "0.0.0.0/0" und Duplikate
ipv4_addresses.discard("0.0.0.0/0")

if len(ipv4_addresses) == 0:
    print("Keine relevanten IPv4-Adressen in den 'f2b' Ketten gefunden.")
else:
    # Erstelle separate JSON-Objekte für jede IPv4-Adresse
    ipv4_json_objects = [{"ip": ipv4_address} for ipv4_address in ipv4_addresses]

    ip_list = {"ip_list": ipv4_json_objects}

    ip_list = json.dumps(ip_list, indent=2)

# Drucke den JSON-String
#print(ip_list)
    
payload = {'blocker_id': v64_blocker_node_id,
    'report_ip_list': ip_list
}
headers = {
  'Authorization': f"Bearer {v64_api_token}"
}
response = requests.request("POST", v64_url, headers=headers, data=payload)
print(response.text)
