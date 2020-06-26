import sys
import re
import json
import time

output = [dict()]
output[0]["ts"] = int(time.time())
output[0]["val"] = []

for line in sys.stdin:
    if re.match('^\s*[0-9]+\s+', line):
        split = line.split()
        toAdd = {
            "success": 1,
            "query": 1,
            "ttl": int(split[0])
        }
        if split[1] == "No" or split[1] == "*":
            output[0]["val"].append(toAdd)
        else:
            # Extract IP address
            ip = re.search('\(?([0-9]{1,3}\.){3}[0-9]{1,3}\)?', line)
            ip = line[ip.regs[0][0]: ip.regs[0][1]]
            ip = re.sub("\(|\)", "", ip)

            # Extract RTT
            rtt = re.findall("[0-9]+\.?[0-9]+ ms", line)
            rtt = float(re.sub("[ms]", "", rtt[0]))

            toAdd["ip"] = ip
            toAdd["rtt"] = rtt

            output[0]["val"].append(toAdd)

output = json.dumps(output)

sys.stdout.write(output)


