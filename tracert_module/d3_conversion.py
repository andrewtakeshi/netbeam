import sys
import re
import json
import time
import subprocess
import requests


def check_pscheduler(endpoint):
    """
    Queries the endpoint to see if it is running pScheduler. Does this through the API provided by pScheduler.
    :param endpoint: Endpoint to be tested.
    :return: True if endpoint is running pScheduler, False otherwise.
    """

    if not endpoint.__contains__('https'):
        endpoint = 'https://' + endpoint
    response = requests.get(f'{endpoint}/pscheduler', verify = False).content.decode('utf8')
    return response.__contains__('pScheduler API server')


def pscheduler_to_d3(source, dest, numRuns = 1):
    """
    Tries to run a pScheduler traceroute from source to destination.
    The source must also be running pScheduler, as must the server/machine running this code.
    If the source is running pScheduler, a traceroute is scheduled, run, and the results converted into
    JSON ingestible by the d3 visualisation.
    :param source: Source for traceroute
    :param dest: Destination for traceroute.
    :param numRuns: Number of times to run the traceroute.
    :return: JSON ingestible by the d3 visualisation if the traceroute is successful. None otherwise.
    """

    # Check the source
    if not check_pscheduler(source):
        return None

    # Schedule traceroute using pscheduler (allows for remote sources)

    i = 0

    processList = [subprocess.Popen(['pscheduler', 'task', 'trace', '-s', source, '-d', dest], stdout=subprocess.PIPE, universal_newlines=True)] * numRuns
    for process in processList:
        process.wait()

    output = [dict()]
    output[0]['ts'] = int(time.time())
    output[0]['val'] = []

    # Process every line in the traceroute.
    for process in processList:
        for line in process.stdout.readlines():
            # Filter out for only lines that match the traceroute results.
            if re.match('^\s*[0-9]+\s+', line):
                split = line.split()
                # Common to all hops
                toAdd = {
                    "success": 1,
                    "query": 1,
                    "ttl": int(split[0])
                }
                # Server didn't respond. Only add the 'common' items.
                if split[1] == "No" or split[1] == "*":
                    output[i]['val'].append(toAdd)
                # Server responded. Do some additional parsing.
                else:
                    # Extract IP address
                    ip = re.search('\(?([0-9]{1,3}\.){3}[0-9]{1,3}\)?', line)
                    ip = line[ip.regs[0][0]: ip.regs[0][1]]
                    ip = re.sub('\(|\)', '', ip)

                    # Extract RTT
                    rtt = re.findall('[0-9]+\.?[0-9]+ ms', line)
                    rtt = float(re.sub('[ms]', '', rtt[0]))

                    toAdd['ip'] = ip
                    toAdd['rtt'] = rtt

                    output[i]['val'].append(toAdd)
        i += 1

    # Convert to an actual JSON (takes care of some formatting).
    output = json.dumps(output)

    # sys.stdout.write(output)
    # print(output)

    return output

def pasted_to_d3(strIn):
    output = []
    i = -1
    linux = True

    for line in strIn.splitlines():
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



def system_to_d3(dest, numRuns):
    output = []

    i = 0

    processList = [subprocess.Popen(['traceroute', dest], stdout=subprocess.PIPE, universal_newlines=True)] * numRuns
    for process in processList:
        process.wait()

    for process in processList:
        for line in process.stdout.readlines():
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


def copy_to_d3(input):


# def esmond_to_d3()