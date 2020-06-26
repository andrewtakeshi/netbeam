import sys
import re
import json
import time

output = []

i = -1

linux = True

for line in sys.stdin:
    # For processing multiple traceroutes (i.e. pasting multiple runs in at once)
    if line.__contains__("Tracing") or line.__contains__("traceroute"):
        i += 1
        output.append(dict())
        if not line.__contains__("traceroute"):
            linux = False

        output[i]["ts"] = int(time.time())
        output[i]["val"] = []
    if re.match('^\s*[0-9]+\s+', line):
        split = line.split()

        # Common to all items in the traceroute path.
        toAdd = {
            "success": 1,
            "query": 1,
            "ttl": int(split[0])
        }
        # Server didn't reply; same thing for both Linux and Windows
        if re.match("No|\*", split[1]):
            output[i]["val"].append(toAdd)

        # Server replied; additional information available
        else:
            # Linux traceroute format
            if linux:
                    ip = ""
                    if re.match('([0-9]{1,3}\.){3}[0-9]{1,3}', split[1]):
                        ip = split[1]
                    else:
                        ip = re.sub("\(|\)", "", split[2])

                    rttArr = re.findall("[0-9]+\.?[0-9]+ ms", line)
                    rtt = 0
                    for response in rttArr:
                        rtt += float(re.sub("[ms]", "", response))
                    rtt /= len(rttArr)

                    toAdd["ip"] = ip
                    toAdd["rtt"] = rtt.__round__(3)
                    output[i]["val"].append(toAdd)

            # Windows traceroute format
            else:
                # Case where hostname is found
                if len(split) == 9:
                    toAdd["ip"] = re.sub("\[|\]", "", split[8])
                # Case where only IP is used
                else:
                    toAdd["ip"] = split[7]

                rttArr = re.findall("\<?[0-9]+ ms", line)
                rtt = 0
                for response in rttArr:
                    response = re.sub("ms|<", "", response)
                    rtt += float(response)
                rtt /= len(rttArr)

                toAdd["rtt"] = rtt.__round__(3)
                output[i]["val"].append(toAdd)

output = json.dumps(output)
sys.stdout.write(output)